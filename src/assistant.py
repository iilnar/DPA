from pathlib import Path
import requests
import language.models.message_constant as mc
from answer import AssistantAnswer
from application.application import IntegrationType
from configs.config_constants import HistoryFilePath, IsStubMode, WMDThresholdKey
from form.form import Form
import importlib

class Assistant:
    def __init__(self, language_model, message_bundle, application_dict, config, **kargs):
        self.language_model = language_model
        self.__application_dict = application_dict
        self.__stack = []
        self.__history = []
        self.__config = config
        self.__is_stub_mode = config[IsStubMode]
        self.__message_bundle = message_bundle
        self.__w2v = kargs["w2v"]
        self.__modules = {}

    def process_request(self, user_request_str):
        request_information = self.language_model.parse(user_request_str)

        app, intent_description = self.__extract_app(request_information)
        if app is None or intent_description is None:
            if len(self.__stack) > 0:
                form = self.__stack.pop(0)
                app = form.get_app()
                answer = self.__process_intent(app, request_information, form)
            else:
                answer = AssistantAnswer(mc.DID_NOT_UNDERSTAND)
        else:
            form = Form(app, intent_description)
            answer = self.__process_intent(app, request_information, form)

        formated_answer = self.format_answer(answer)
        self.__history.append((user_request_str, formated_answer))
        return formated_answer

    def __get_module_by_class_name(self, clazz):
        module = self.__modules.get(clazz, None)
        if module is None:
            module_name, class_name = clazz.rsplit(".", 1)
            MyClass = getattr(importlib.import_module(module_name), class_name)
            module = MyClass()
            self.__modules[clazz] = module
        return module

    def __extract_app(self, request_information):
        app_name = request_information.get_app_name()
        app_name = app_name.lower()
        app = self.__application_dict.get(app_name, None)
        intent_description = None
        if app is None:
            temp_list = request_information.get_tokens_list()
            new_request_list = []
            for token in temp_list:
                new_request_list.append(token.get_lemma())

            min_dist = float(self.__config[WMDThresholdKey])
            for app_name, app_description in self.__application_dict.items():
                for intent in app_description.get_intents_list():
                    samples = intent.get_samples()
                    if samples is not None:
                        for sample in samples:
                            dist = self.__w2v.wmdistance(new_request_list, sample)
                            if dist < min_dist:
                                min_dist = dist
                                app = app_description
                                intent_description = intent
        else:
            lemma = request_information.get_intent().get_lemma()
            intent_description = app.get_intent(lemma)
        return app, intent_description

    def __process_intent(self, app, request_information, form):
        answer = form.process(request_information)
        if form.is_finish():
            answer = self.__execute_request(app, form.get_parameters_value())
        else:
            # save_form
            self.__stack.insert(0, form)
        return answer

    def __execute_request(self, app, parameters_dict):
        if app.get_integration_type() == IntegrationType.Module:
            class_name = app.get_impl()
            module = self.__get_module_by_class_name(class_name)
            answer = module.run(self, parameters_dict)
        elif not self.__is_stub_mode:
            url = app.get_endpoint_url()
            try:
                response = requests.post(url, data=parameters_dict)
                if response.status_code == 200:
                    answer = AssistantAnswer(None, message_str=response.json())
                else:
                    answer = AssistantAnswer(mc.ERROR_RESPONSE_CODE, parameters_dict={"code": response.status_code})
            except Exception:
                answer = AssistantAnswer(mc.SERVICE_DOES_NOT_WORK)
        else:
            answer = "AppName: " + app.get_name()
            for key, value in parameters_dict.items():
                answer += "| " + key + "=" + value
            answer = AssistantAnswer(None, message_str=answer)
        return answer

    def stop(self):
        path = Path(self.__config[HistoryFilePath])
        file = None
        try:
            if path.exists():
                file = open(path, encoding="utf-8", mode="a")
            else:
                file = open(path, encoding="utf-8", mode="w")
            for t in self.__history:
                file.write("U:" + t[0] + "\n")
                file.write("A:" + t[1] + "\n")
        finally:
            if file is not None:
                file.close()

    def format_answer(self, answer):
        if answer.message_key is not None:
            message = self.__message_bundle[answer.message_key]
            params = answer.parameters
            if params is not None:
                message = message.format(**params)
        else:
            message = answer.message
        return message

    @property
    def application_dict(self):
        return self.__application_dict

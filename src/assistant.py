import webbrowser
from pathlib import Path

import requests

from application.application import IntegrationType
from configs.config_constants import HistoryFilePath, SearchAddress
from configs.config_constants import IsStubMode
from form.form import Form
from language.models.request_type import RequestType


class Assistant:
    def __init__(self, language_model, application_dict, config):
        self.language_model = language_model
        self.application_dict = application_dict
        self.__stack = []
        self.__history = []
        self.__config = config
        self.__is_stub_mode = config[IsStubMode]

    def process_request(self, user_request_str):
        request_information = self.language_model.parse(user_request_str)
        type_rt = request_information.get_type()
        # Костыль!
        if type_rt == RequestType.ACTION and self.__extract_app(request_information) is None and len(self.__stack) > 0:
            request_information.set_type(RequestType.ANSWER)
            type_rt = request_information.get_type()

        if type_rt == RequestType.ACTION:
            app = self.__extract_app(request_information)
            if app is None:
                answer = "Sorry, I didn't understand you. Please try it again"
            else:
                lemma = request_information.get_intent().get_lemma()
                intent_description = app.get_intent(lemma)
                if intent_description is None:
                    answer = "Sorry, application '{0}' doesn't support action '{1}'".format(app.get_name(), lemma)
                else:
                    form = Form(app, intent_description)
                    answer = self.__process_intent(app, request_information, form)
        elif type_rt == RequestType.QUESTION:
            url = self.__config[SearchAddress]
            tokens_list = request_information.get_tokens_list()
            param = []
            for token in tokens_list:
                param.append(token.get_word())
            url += "?q=" + "+".join(param)
            webbrowser.open(url, new=2)
            answer = "Let's find out the answer in Internet: " + url
        else:
            if len(self.__stack) > 0:
                form = self.__stack.pop(0)
                app = form.get_app()
                answer = self.__process_intent(app, request_information, form)
            else:
                answer = "Sorry, I didn't understand you. Please try it again"

        self.__history.append((user_request_str, answer))
        return answer

    def __extract_app(self, request_information):
        app_name = request_information.get_app_name()
        app_name = app_name.lower()
        app = self.application_dict.get(app_name, None)
        return app

    def __process_intent(self, app, request_information, form):
        answer = form.process(request_information)
        if form.is_finish():
            answer = self.__execute_request(app, form.get_parameters_value())
        else:
            # save_form
            self.__stack.insert(0, form)
        return answer

    def __execute_request(self, app, parameters_dict):
        if not self.__is_stub_mode:
            if app.get_integration_type() == IntegrationType.RemoteApp:
                url = app.get_endpoint_url()
                try:
                    answer = requests.post(url, data=parameters_dict)
                    if answer.status_code == 200:
                        answer = answer.json()
                    else:
                        answer = "Error"
                except Exception:
                    answer = "Sorry, service temporary doesn't work. Try it later."
            else:
                answer = "Done"
        else:
            answer = "AppName: " + app.get_name()
            for key, value in parameters_dict.items():
                answer += "| " + key + "=" + value
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

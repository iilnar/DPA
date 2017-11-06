import webbrowser
from pathlib import Path

from configs.config_constants import HistoryFilePath, SearchAddress
from form.form import Form
from language.models.request_type import RequestType


class Assistant:
    def __init__(self, language_model, application_dict, config):
        self.language_model = language_model
        self.application_dict = application_dict
        self.__stack = []
        self.__history = []
        self.__config = config

    def process_request(self, user_request_str):
        request_information = self.language_model.parse(user_request_str)
        type_rt = request_information.get_type()
        if type_rt == RequestType.ACTION:
            app = self.__extract_app(request_information)
            if app is None:
                answer = "Sorry, I didn't understand you. Please try it again"
            else:
                lemma = request_information.get_intent().get_lemma()
                intent_description = app.get_intent(lemma)
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
                form = self.__stack.pop()
                app = form.get_app()
                answer = self.__process_intent(app, request_information, form)
            else:
                answer = "Sorry, I didn't understand you. Please try it again"

        self.__history.append((user_request_str, answer))
        return answer

    def __extract_app(self, request_information):
        lemma = request_information.get_intent().get_lemma()
        app = None
        if lemma == "remind":
            app = self.application_dict["Calendar"]
            request_information.set_app_name("Calendar")
        elif lemma == "increase":
            app = self.application_dict["Home"]
            request_information.set_app_name("Home")
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
        return "Done"

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

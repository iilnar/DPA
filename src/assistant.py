from pathlib import Path
from configs.config_constants import HistoryFilePath
from form.form import Form


class Assistant:
    def __init__(self, language_model, application_dict, config):
        self.language_model = language_model
        self.application_dict = application_dict
        self.__stack = []
        self.__history = []
        self.__config = config

    def process_request(self, user_request_str):
        request_information = self.language_model.parse(user_request_str)
        if request_information.is_intent():
            app = self.__extract_app(request_information)
            if app is None:
                answer = "Sorry, I didn't understand you. Please try it again"
            else:
                answer = self.__process_intent(app, request_information)
        else:
            # Here we must to handle questions and answers
            answer = "Done"
        self.__history.append((user_request_str, answer))
        return answer

    def __extract_app(self, request_information):
        lemma = request_information.get_intent().get_lemma()
        app = None
        if lemma == "remind":
            app = self.application_dict["Calendar"]
            request_information.set_app_name("Calendar")
        return app

    def __process_intent(self, app, request_information):
        lemma = request_information.get_intent().get_lemma()
        intent_description = app.get_intent(lemma)
        form = Form(intent_description)
        answer = form.process(request_information)
        if form.is_finish():
            answer = self.__execute_request(app, form.get_parameters_value())
        else:
            # save_form
            pass
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

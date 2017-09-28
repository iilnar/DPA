from pathlib import Path


class Assistant:
    def __init__(self, language_model, application_dict, config):
        self.language_model = language_model
        self.application_dict = application_dict
        self.__stack = []
        self.__history = []
        self.__config = config

    def process_intent(self, user_request_str):
        request_information = self.language_model.parse(user_request_str)
        if request_information.is_intent():
            app = self.__extract_app(request_information)
            intent_description = app.get_intent(request_information.get_intent())
        else:
            pass
        answer = "Done"
        self.__history.append((user_request_str, answer))
        return answer

    def __extract_app(self, request_information):
        return self.application_dict[request_information.get_app_name()]

    def stop(self):
        path = Path(self.__config["HistoryFilePath"])
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

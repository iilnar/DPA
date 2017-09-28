
class RequestInformation:

    def __init__(self, app_name_str, intent, is_intent=True):
        self.__is_intent = is_intent
        self.__app_name = app_name_str
        self.__intent = intent

    def is_intent(self):
        return self.__is_intent

    def get_app_name(self):
        return self.__app_name

    def get_intent(self):
        return self.__intent


class LanguageModel:

    def parse(self, string):
        # tokens_list = self.tokenize(string)
        obj = RequestInformation("Calendar", "remind")
        return obj

    def tokenize(self, string):
        pass
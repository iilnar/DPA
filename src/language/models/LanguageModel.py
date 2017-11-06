from language.models.part_of_speech import POS
from language.models.request_type import RequestType

class RequestInformation:
    def __init__(self, tokens_list, intent, rtype):
        self.__type = rtype
        self.__tokens_list = tokens_list
        self.__intent = intent
        self.__app_name = None

    def get_type(self):
        return self.__type

    def get_tokens_list(self):
        return self.__tokens_list

    def get_intent(self):
        return self.__intent

    def get_app_name(self):
        return self.__app_name

    def set_app_name(self, name):
        self.__app_name = name


class LanguageModel:
    def parse(self, string):
        string = self.__preprocess_text(string)
        tokens_list = self.tokenize(string)
        is_question = self.is_question(tokens_list)
        if is_question:
            obj = RequestInformation(tokens_list, None, rtype=RequestType.QUESTION)
        else:
            verb = self.__find_first_verb(tokens_list)
            if verb is None:
                obj = RequestInformation(tokens_list, None, rtype=RequestType.ANSWER)
            else:
                obj = RequestInformation(tokens_list, verb, rtype=RequestType.ACTION)
        return obj

    def tokenize(self, string):
        raise NotImplementedError()

    def __preprocess_text(self, string):
        return string

    def __find_first_verb(self, tokens_list):
        for token in tokens_list:
            if token.get_pos() == POS.VERB:
                return token
        return None

    def convert_ner(self, ner):
        raise NotImplementedError()

    def convert_pos(self, pos_str):
        raise NotImplementedError()

    def is_question(self, tokens_list):
        raise NotImplementedError()

from language.models.part_of_speech import POS


class RequestInformation:
    def __init__(self, tokens_list, intent, is_intent=True):
        self.__is_intent = is_intent
        self.__tokens_list = tokens_list
        self.__intent = intent
        self.__app_name = None

    def is_intent(self):
        return self.__is_intent

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
        verb = self.__find_first_verb(tokens_list)
        if verb is None:
            obj = RequestInformation(tokens_list, None, is_intent=False)
        else:
            obj = RequestInformation(tokens_list, verb)
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

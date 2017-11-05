from application.data_type import DataType
from language.models.named_entity_recognition import NERType


class Form:
    def __init__(self, intent_description):
        self.__int_desc = intent_description
        self.__parameters_value = dict()
        self.__is_finish = False

    def get_parameters_value(self):
        return self.__parameters_value

    def process(self, request_information):
        token_list = request_information.get_tokens_list()
        parameters_list = self.__int_desc.get_parameters_list()
        for param in parameters_list:
            value = self.__parameters_value.get(param.get_name(), None)
            if value is None:
                dt = param.get_data_type()
                for token in token_list:
                    ner_type = token.get_NER_type()
                    if dt == DataType.DATE and ner_type == NERType.DATE:
                        self.__parameters_value[param.get_name()] = token.get_word()
                        break
                    elif dt == DataType.NUMBER and ner_type == NERType.NUMBER:
                        self.__parameters_value[param.get_name()] = token.get_word()
                        break

        for param in parameters_list:
            value = self.__parameters_value.get(param.get_name(), None)
            if value is None and param.is_obligatory():
                return param.get_clarifying_question()

        self.__is_finish = True
        return None

    def is_finish(self):
        return self.__is_finish

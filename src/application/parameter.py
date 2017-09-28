class Parameter:
    def __init__(self, name_str, data_type_str, obligatory_bool=False, question_str=None):
        self.__name = name_str
        self.__data_type = data_type_str
        self.__obligatory = obligatory_bool
        self.__question = question_str

    def get_name(self):
        return self.__name

    def get_data_type(self):
        return self.__data_type

    def is_obligatory(self):
        return self.__obligatory

    def get_clarifying_question(self):
        return self.__question

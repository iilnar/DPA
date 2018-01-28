import re


class Parameter:
    def __init__(self, name_str, data_type_str, obligatory_bool=False, question_str=None, regexp=None, **kwargs):
        self.__name = name_str
        self.__data_type = data_type_str
        self.__obligatory = obligatory_bool
        self.__question = question_str
        if regexp is None:
            self.__regexp = regexp
            self.__group_ids = None
        else:
            self.__regexp = re.compile(regexp)
            ids = kwargs.get("regexp_group", None)
            if ids is None:
                ids = [0]
            self.__group_ids = ids

    def get_name(self):
        return self.__name

    def get_data_type(self):
        return self.__data_type

    def is_obligatory(self):
        return self.__obligatory

    def get_clarifying_question(self):
        return self.__question

    def get_regexp(self):
        return self.__regexp

    @property
    def group_ids(self):
        return self.__group_ids
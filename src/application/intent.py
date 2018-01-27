class Intent:
    def __init__(self, name_str, key_phrases_list, parameters_list, samples=None, **kargs):
        self.__name = name_str
        self.__key_phrases_list = key_phrases_list
        self.__parameters_list = parameters_list
        self.__samples_list = samples
        self.__description = kargs["description"]

    def get_name(self):
        return self.__name

    def get_list_of_key_phrases(self):
        return self.__key_phrases_list

    def get_parameters_list(self):
        return self.__parameters_list

    def get_samples(self):
        return self.__samples_list

    @property
    def description(self):
        return self.__description

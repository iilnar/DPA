import json
from application.application import Application
from application.application import IntegrationType
from application.intent import Intent
from application.parameter import Parameter
from application.data_type import DataType

APPLICATIONS_TAG = "applications"
APPLICATION_NAME_TAG = "name"
APPLICATION_DESCRIPTION_TAG = "description"
APPLICATION_TYPE_TAG = "type"
APPLICATION_ENDPOINT_URL_TAG = "url"
APPLICATION_INTENTS_TAG = "intents"

INTENT_NAME_TAG = "name"
INTENT_KEY_PHRASES_TAG = "key_phrases"
INTENT_PARAMETERS_TAG = "parameters"

PARAMETER_NAME_TAG = "name"
PARAMETER_TYPE_TAG = "data_type"
PARAMETER_OBLIGATORY_TAG = "obligatory"
PARAMETER_QUESTION_TAG = "question"


def load_config(path_str):
    with open(path_str) as data_file:
        data = json.load(data_file)

    app_dict = {}
    for app in data[APPLICATIONS_TAG]:
        app_name = app[APPLICATION_NAME_TAG]
        description = app[APPLICATION_DESCRIPTION_TAG]
        type = app[APPLICATION_TYPE_TAG]
        URL = app.get(APPLICATION_ENDPOINT_URL_TAG, None)
        intents = []
        for intent in app[APPLICATION_INTENTS_TAG]:
            intent_name = intent[INTENT_NAME_TAG]
            key_phrases_list = intent[INTENT_KEY_PHRASES_TAG]
            key_phrases_list = [x.lower() for x in key_phrases_list]
            parameters_list = []
            for parameter in intent[INTENT_PARAMETERS_TAG]:
                param_name = parameter[PARAMETER_NAME_TAG]
                param_data_type = parameter[PARAMETER_TYPE_TAG]
                param_data_type = DataType[param_data_type.upper()]
                param_obligatory = parameter[PARAMETER_OBLIGATORY_TAG]
                param_question = parameter.get(PARAMETER_QUESTION_TAG, None)
                param_inst = Parameter(param_name, param_data_type, obligatory_bool=param_obligatory,
                                       question_str=param_question)
                parameters_list.append(param_inst)

            intent_ints = Intent(intent_name, key_phrases_list, parameters_list)
            intents.append(intent_ints)

        app_inst = Application(app_name, description, intents, integration_type=IntegrationType[type], url=URL)
        app_dict[app_name.lower()] = app_inst

    return app_dict

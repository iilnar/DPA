from configparser import ConfigParser
from application.application_config import load_config
from assistant import Assistant
from interface.console import Console
from interface.telegram import Telegram
from language.models.en.english_language_model import EnglishLanguageModel
from configs.config_constants import InterfaceTypeKey, LogLevelKey, IsStubMode
import logging
from threading import Thread

STARTED_WORKING_MESSAGE = "Assistant started working"
TELEGRAM = "telegram"
CONSOLE = "console"


def start():
    print("Started initialization")
    config_parser = ConfigParser()
    config_parser.read("configs/config.ini", encoding="utf-8")
    default_config = config_parser["DEFAULT"]

    logging.basicConfig(level=default_config[LogLevelKey],
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logging.info("Stub mode: {}".format(default_config[IsStubMode]))

    language_model = EnglishLanguageModel(default_config)
    logging.info("Selected {} language mode".format(language_model.get_language_name()))

    config_parser = ConfigParser()
    config_parser.read("language/models/en/message.ini", encoding="utf-8")
    message_bundle = config_parser["DEFAULT"]

    app_dict = load_config("ApplicationConfig.json")
    assistant = Assistant(language_model, message_bundle, app_dict, default_config)

    interface_type = default_config[InterfaceTypeKey]
    interface_class = get_interface(interface_type)
    interface = interface_class(assistant, message_bundle, default_config)

    if interface_type == CONSOLE:
        print(STARTED_WORKING_MESSAGE)
        interface.start()
    elif interface_type == TELEGRAM:
        assistant_thread = Thread(target=interface, name="Assistant")
        assistant_thread.start()
        print(STARTED_WORKING_MESSAGE)

        request = input("User: ")
        while request != "exit":
            request = input("User: ")

    interface.stop()
    print("Assistant stopped working")


def get_interface(interface):
    clazz = None
    if interface == CONSOLE:
        clazz = Console
    elif interface == TELEGRAM:
        clazz = Telegram

    logging.info("Chosen {} mode".format(clazz.__name__))
    return clazz


if __name__ == "__main__":
    start()

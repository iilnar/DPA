from configparser import ConfigParser
from application.application_config import load_config
from assistant import Assistant
from language.models.en.english_language_model import EnglishLanguageModel
import traceback


def start():
    config_parser = ConfigParser()
    config_parser.read("configs/config.ini", encoding="utf-8")
    default_config = config_parser["DEFAULT"]

    language_model = EnglishLanguageModel(default_config)
    config_parser = ConfigParser()
    config_parser.read("language/models/en/message.ini", encoding="utf-8")
    message_bundle = config_parser["DEFAULT"]

    app_dict = load_config("ApplicationConfig.json")
    assistant = Assistant(language_model, message_bundle, app_dict, default_config)
    print("Assistant starts work")

    print("For finish write 'exit'")
    request = input("User: ")
    while request != "exit":
        try:
            answer = assistant.process_request(request)
            print("Masha: " + answer)
        except Exception:
            print("Error:")
            print(traceback.print_exc())
        request = input("User: ")

    assistant.stop()


if __name__ == "__main__":
    start()

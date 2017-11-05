from configparser import ConfigParser
from application.application_config import load_config
from assistant import Assistant
from language.models.en.english_language_model import EnglishLanguageModel


def start():
    config_parser = ConfigParser()
    config_parser.read("configs/config.ini", encoding="utf-8")
    default_config = config_parser["DEFAULT"]

    language_model = EnglishLanguageModel(default_config)
    app_dict = load_config("ApplicationConfig.json")
    assistant = Assistant(language_model, app_dict, default_config)
    print("Assistant starts work")

    print("For finish write 'exit'")
    request = input("Denis: ")
    while (request != "exit"):
        answer = assistant.process_request(request)
        print("Masha: " + answer)
        request = input("User: ")

    assistant.stop()


if __name__ == "__main__":
    start()

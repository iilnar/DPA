from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from configs.config_constants import StartMessageKey, TokenKey
from assistant import Assistant
import logging

USER_ASKS_PATTERN = "User {} asks: '{}'"
ASSISTANT_ANSWERS_PATTERN = "Answer for user {}: '{}'"


class Telegram:

    def __init__(self, language_model, app_dict, w2v, message_bundle, config):
        self.__language_model = language_model
        self.__app_dict = app_dict
        self.__w2v = w2v
        self.__message_bundle = message_bundle
        self.__config = config
        self.__token = self.__config[TokenKey]
        self.__START_MESSAGE_KEY = self.__config[StartMessageKey]
        self.__user_assistant_dict = {}

        self.__updater = Updater(self.__token)
        dp = self.__updater.dispatcher
        dp.add_handler(CommandHandler("start", self.slash_start), group=0)
        dp.add_handler(MessageHandler(Filters.text, self.idle_main))

    def idle_main(self, bot, update):
        request = update.message.text.strip()
        user_id = update.message.chat_id
        logging.info(USER_ASKS_PATTERN.format(user_id, request))
        assistant = self.__user_assistant_dict.get(user_id, None)
        if assistant is None:
            assistant = Assistant(self.__language_model, self.__message_bundle, self.__app_dict,
                                  self.__config, w2v=self.__w2v, user_id=user_id)
            self.__user_assistant_dict[user_id] = assistant
        answer = assistant.process_request(request)
        logging.info(ASSISTANT_ANSWERS_PATTERN.format(user_id, answer))
        bot.sendMessage(update.message.chat_id, text=answer)

    def slash_start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text=self.__message_bundle[self.__START_MESSAGE_KEY])

    def start(self):
        self.__updater.start_polling()

    def stop(self):
        self.__updater.stop()
        for assistant in self.__user_assistant_dict.values():
            assistant.stop()

    def __call__(self, *args, **kwargs):
        self.start()


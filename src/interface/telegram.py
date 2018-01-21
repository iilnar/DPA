from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from configs.config_constants import StartMessageKey, TokenKey


class Telegram:

    def __init__(self, assistant, message_bundle, config):
        self.__assistant = assistant
        self.__message_bundle = message_bundle
        self.__config = config
        self.__token = self.__config[TokenKey]
        self.__START_MESSAGE_KEY = self.__config[StartMessageKey]

        self.__updater = Updater(self.__token)
        dp = self.__updater.dispatcher
        dp.add_handler(CommandHandler("start", self.slash_start), group=0)
        dp.add_handler(MessageHandler(Filters.text, self.idle_main))

    def idle_main(self, bot, update):
        request = update.message.text.strip()
        answer = self.__assistant.process_request(request)
        bot.sendMessage(update.message.chat_id, text=answer)

    def slash_start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text=self.__message_bundle[self.__START_MESSAGE_KEY])

    def start(self):
        self.__updater.start_polling()

    def stop(self):
        self.__updater.stop()
        self.__assistant.stop()

    def __call__(self, *args, **kwargs):
        self.start()


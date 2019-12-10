import logging, sys
from hendles import handle_echo, handle_contact, handle_error, start, button
from helpers import start_bot_config, start_zk
from jobs import callback_minute
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler
from zoopersistent import ZooPersistent

logging.basicConfig(
    format='%(asctime)s;%(name)s;%(levelname)s;%(message)s',
    level=logging.DEBUG,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    bot_config = start_bot_config()

    zk = start_zk()

    zk_pers = ZooPersistent(main_node='mytelegrambot', zoo_client=zk)

    updater = Updater(token=bot_config['bot_token'], request_kwargs=bot_config['bot_request_kwargs'], persistence=zk_pers, use_context=True)

    dispatcher = updater.dispatcher

    j = dispatcher.job_queue

    job_minute = j.run_repeating(callback_minute, interval=600, first=60, context=dispatcher)

    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(MessageHandler(Filters.text, handle_echo))

    dispatcher.add_handler(MessageHandler(Filters.contact, handle_contact))

    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    dispatcher.add_error_handler(handle_error)

    updater.start_polling()

    updater.idle()

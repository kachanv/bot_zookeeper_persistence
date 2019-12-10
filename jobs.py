import logging
from helpers import update_list_user_data
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


def callback_minute(context: CallbackContext):
    update_list_user_data(context_full=context.job.context)

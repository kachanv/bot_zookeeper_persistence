import logging
import helpers
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def start(update, context):
    if 'name' in context.user_data:
        keyboard(update, context)

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please send me your contact')
        f = open(u'./images/share_contact.png', 'rb')
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
        f.close()


def handle_contact(update, context):
    if update.effective_user.id == update.message.contact.user_id:
        helpers.update_user_data(context=context, user_phone=update.message.contact.phone_number)

        if 'name' in context.user_data:
            keyboard(update, context)

        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='User is not found')

    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='You sent someone phone')


def handle_echo(update, context):
    if 'name' in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Hello, I know you,  %s')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please send me your contact')


def report_1(update, context):
    if 'name' in context.user_data:
        helpers.update_user_data(context=context, user_phone=context.user_data['phone_num'])
        context.bot.send_message(chat_id=update.effective_chat.id, text='Your value %s ' % (context.user_data['value']))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please send me your contact')


def report_2(update, context):
    if 'name' in context.user_data:
        helpers.update_user_data(context=context, user_phone=context.user_data['phone_num'])
        context.bot.send_message(chat_id=update.effective_chat.id, text='Your value %s ' % (context.user_data['value']))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please send me your contact')


def keyboard(update, context):
    if 'name' in context.user_data:
        keyboard = [[InlineKeyboardButton('Report 1', callback_data='report_1'),
                     InlineKeyboardButton('Report 2', callback_data='report_2')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Reports:', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please send me your contact')


def button(update, context):
    query = update.callback_query
    if query.data == 'report_1':
        return report_1(update, context)
    elif query.data == 'report_2':
        return report_2(update, context)


def handle_error(update, context):
    logger.error('Update "%s" error with context error"%s"', update, context.error)

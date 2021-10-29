import logging
from logging.config import fileConfig

import ifaxbotcovid.config.settings as settings
import ifaxbotcovid.config.startmessage as startmessage
from ifaxbotcovid.bot.factory import create_bot, create_chef

# logging settings
fileConfig('ifaxbotcovid/config/logging.ini')
botlogger = logging.getLogger('botlogger')
botlogger.setLevel(logging.DEBUG)

try:
    import ifaxbotcovid.config.token as tkn
    TOKEN = tkn.TOKEN
except ImportError or ModuleNotFoundError as err:
    botlogger.warning('File with Telegram token have not been found')
    raise err

bot, tblogger = create_bot(
    TOKEN, get_logger=True, loglevel=logging.INFO
)

chef = create_chef(
    short_procedure_key=settings.short_procedure_key,
    check_phrases=settings.key_words,
    stop_phrase=settings.stop_phrase,
    maxlen=3,
    time_gap=1.5,
    logger=botlogger
)


@bot.message_handler(commands=['start'])
def answer_start(message):
    '''
    Bot sends welcome message
    '''
    bot.send_message(message.chat.id, startmessage.s, parse_mode='HTML')
    botlogger.info(
        'User %s issued "start" command' % message.from_user.username)
    user = message.from_user.username
    chat_id = message.chat.id
    if (user, chat_id) not in settings.users:
        settings.users.append((user, chat_id))


@bot.message_handler(commands=['log'])
def syslog_sender(message):
    '''
    Bot sends system log as a file (admin only)
    '''
    user = message.from_user.username
    chat_id = message.chat.id
    botlogger.info('User %s requested "log" file via command' % user)
    if chat_id in settings.admins:
        botlogger.debug('Admin privileges grunted')
        try:
            bot.send_document(
                message.chat.id, open('botlog.log'), 'document'
            )
        except Exception as exc:
            botlogger.error('No system log file found! Exception: %s' % exc)
    else:
        botlogger.warning('Access to user %s denied' % user)
        bot.send_message(
            message.chat.id, '<b>Access denied</b>', parse_mode='HTML'
        )


@bot.message_handler(content_types=['text'])
def user_request(message):
    botlogger.info('User %s send some text' % message.from_user.username)
    answer = chef.process_new_message(message)
    if answer.flag:
        if answer.warnmessage:
            bot.send_message(message.chat.id, answer.warnmessage)
            botlogger.info(
                'Warning message sent to %s' % message.from_user.username
            )
        bot.send_message(message.chat.id, answer.ready_text)
        botlogger.info(
            'Ready answer sent to %s' % message.from_user.username
        )
        if message.text.endswith('йй') or message.text.startswith('йй'):
            bot.send_message(message.chat.id, answer.log)
            botlogger.info(
                'Log message sent to %s' % message.from_user.username)


def run_long_polling():
    botlogger.info('Starting polling...')
    bot.infinity_polling()

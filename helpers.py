import sys
import logging
import config
from clickhouse_driver import Client
from kazoo.client import KazooClient
from copy import deepcopy
import json

logger = logging.getLogger(__name__)


def start_bot_config():
    bot_config = config.get_runner_config()
    if bot_config['run_mode'].startswith('dev_'):
        logger.setLevel(logging.DEBUG)

    return bot_config


def start_ch():
    bot_config = start_bot_config()
    ch = Client(bot_config['ch_host'], password=bot_config['ch_pass'])
    ch_test = ch.execute("SELECT 1")
    logger.debug("Clickhouse test. SELECT 1 result: %s", ch_test)

    return ch


def start_zk():
    bot_config = start_bot_config()
    if bot_config['zoo_use_ssl'] == 'true':
        zk = KazooClient(hosts=bot_config['zoo_hosts'],
                         keyfile=bot_config['zoo_key_file'],
                         keyfile_password=bot_config['zoo_keyfile_password'],
                         certfile=bot_config['zoo_cert_file'],
                         ca=bot_config['zoo_ca_file'],
                         use_ssl=True,
                         verify_certs=False)
    elif bot_config['zoo_use_ssl'] == 'false':
        zk = KazooClient(hosts=bot_config['zoo_hosts'])
    else:
        logger.error('Bad value %s in ZOO_USE_SSL. Set ZOO_USE_SSL environment variable to true/false', bot_config['zoo_use_ssl'])
        sys.exit(1)
    zk.start()
    value, stats = zk.get("/")
    logger.error('Zookeeper test. Root data: %s, root stats: %s' % (value, stats))
    zk.stop()

    return zk


# TODO API request
def request_user_data(user_phone):
    try:
        with open('test_data.json') as json_file:
            data = json.load(json_file)
            for doc in data:
                if str(doc['phone_num']).replace(' ', '')[-10:] == str(user_phone).replace(' ', '')[-10:]:
                    return doc
    except Exception as e:
        logger.error('Request user data with error %s', e)


def update_user_data(context, user_phone):
    try:
        user_data = request_user_data(user_phone)
        if isinstance(user_data, (dict)) > 0 and 'phone_num' in user_data:
            for field in user_data:
                context.user_data[field] = user_data[field]
            logger.info('Update data for user "%s": "%s" -> "%s"' % (user_phone, context.user_data, user_data))
        else:
            logger.info('Not valid response data for "%s": "%s"' % (user_phone, user_data))
    except Exception as e:
        logger.error('Update user data with error %s', e)


def update_list_user_data(context_full):
    try:
        users_data = deepcopy(context_full.user_data)
        for user_id in users_data:
            user_data_new = request_user_data(users_data[user_id]['phone_num'])
            if isinstance(user_data_new, (dict)) > 0 and 'phone_num' in user_data_new:
                for field in users_data[user_id]:
                    context_full.user_data[user_id][field] = user_data_new[field]
            else:
                logger.info('Not valid response data for "%s": "%s"' % (users_data[user_id]['phone_num'], user_data_new))
            logger.info('Update data for user "%s": "%s" -> "%s"' % (users_data[user_id]['phone_num'], context_full.user_data[user_id], user_data_new))
    except Exception as e:
        logger.error('Update user data with error %s', e)

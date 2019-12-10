import os, logging

logger = logging.getLogger(__name__)


def get_runner_config():
    config = {
        'run_mode': os.environ.get('RUN_MODE', 'dev_standalone'),
        'zoo_key_file': os.environ.get('ZOO_KEY_FILE', 'zoo.key'),
        'zoo_cert_file': os.environ.get('ZOO_CERT_FILE', 'zoo.cer'),
        'zoo_ca_file': os.environ.get('ZOO_CA_FILE', 'zoo_ca.cer')
    }

    if config['run_mode'] == 'dev_standalone':
        config['ch_host'] = os.environ.get('CH_HOST', 'localhost')
        config['zoo_hosts'] = os.environ.get('ZOO_HOSTS', 'localhost:port')
        config['zoo_use_ssl'] = os.environ.get('ZOO_USE_SSL', 'false')
    elif config['run_mode'] == 'dev_docker':
        config['ch_host'] = os.environ.get('CH_HOST', 'ch')
        config['zoo_hosts'] = os.environ.get('ZOO_HOSTS', 'zoo:port1')
        config['zoo_use_ssl'] = os.environ.get('ZOO_USE_SSL', 'false')
    elif config['run_mode'] == 'prod':
        config['ch_host'] = os.environ.get('CH_HOST', 'clickhouse.ga.loc')
        config['zoo_hosts'] = os.environ.get('ZOO_HOSTS', 'zoo1:port1,zoo2:port2,zoo3:port3')
        config['zoo_use_ssl'] = os.environ.get('ZOO_USE_SSL', 'true')

    try:
        logger.info('try to import zoo_keyfile_password from /creds.py')
        from creds import zoo_keyfile_password
        config['zoo_keyfile_password'] = zoo_keyfile_password
    except ImportError:
        logger.info('filed to import zoo_keyfile_password from /creds.py, try ZOO_KEYFILE_PASSWORD env variable')
        config['zoo_keyfile_password'] = os.environ.get('ZOO_KEYFILE_PASSWORD', '')

    try:
        logger.info('try to import ch_pass from /creds.py')
        from creds import ch_pass
        config['ch_pass'] = ch_pass
    except ImportError:
        logger.info('filed to import ch_pass from /creds.py, try CH_PASS env variable')
        config['ch_pass'] = os.environ.get('CH_PASS', '')

    try:
        logger.info('try to import bot_token from /creds.py')
        from creds import bot_token
        config['bot_token'] = bot_token
    except ImportError:
        logger.info('filed to import bot_token from /creds.py, try BOT_TOKEN env variable')
        config['bot_token'] = os.environ['BOT_TOKEN']

    bot_request_kwargs = {}

    try:
        logger.info('try to import bot_proxy_url from /creds.py')
        from creds import bot_proxy_url
        bot_request_kwargs['proxy_url'] = bot_proxy_url
    except ImportError:
        logger.info('filed to import bot_proxy_url from /creds.py, try BOT_PROXY_URL env variable')
        try:
            bot_request_kwargs['proxy_url'] = os.environ['BOT_PROXY_URL']
        except KeyError:
            pass

    config['bot_request_kwargs'] = bot_request_kwargs

    return config

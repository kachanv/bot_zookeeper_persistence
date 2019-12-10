from telegram.ext import BasePersistence
from copy import deepcopy
from collections import defaultdict
import json
import logging
from telegram.utils.helpers import decode_conversations_from_json, decode_user_chat_data_from_json, enocde_conversations_to_json

logger = logging.getLogger(__name__)


class ZooPersistent(BasePersistence):

    def __init__(self, main_node, zoo_client, on_flush=False):
        super().__init__()
        self.user_data = None
        self.conversations = None
        self.user_id = None
        self.chat_data = None
        self.on_flush = on_flush
        self.main_node = main_node
        self.zoo_client = zoo_client
        self.zoo_client.start()
        self.zoo_client.ensure_path(r'/%s' % main_node)

    def get_user_id(self, context_defaultdict):
        try:
            self.user_id = str(list(context_defaultdict.keys())[0])
            return deepcopy(self.user_id)
        except Exception:
            return None

    def file_list(self, directory='', file_type=''):
        nodes_list = []
        for nodes in self.zoo_client.get_children('/%s' % directory):
            for child_node in self.zoo_client.get_children('/%s/%s' % (directory, nodes)):
                nodes_list.append(r'/%s/%s/%s' % (directory, nodes, child_node))
        file_full_dir = list(filter(lambda x: x.endswith(file_type), nodes_list))
        return file_full_dir

    def load_user_chat_data(self, data_type):
        try:
            json_data_full = defaultdict(dict)
            for file in self.file_list(directory=self.main_node, file_type=data_type):
                node_data, stat = self.zoo_client.get(file)
                json_data = decode_user_chat_data_from_json(node_data.decode('utf-8'))
                json_data_concat = {**json_data, **json_data_full}
                json_data_full = json_data_concat
            return deepcopy(json_data_full)
        except Exception as ex:
            logger.error('Error read data from node with Exception: %s' % ex)
            return None

    def load_conversation_data(self, filename):
        try:
            node_data, stat = self.zoo_client.get(filename).decode('utf-8')
            json_data = decode_conversations_from_json(node_data)
            return json_data
        except Exception as ex:
            logger.error('Error read data from node %s with Exception: %s' % (filename, ex))
            return None

    def dump_user_chat_data(self, filename, data):
        self.zoo_client.ensure_path(filename)
        data_json = json.dumps(data).encode('utf-8')
        self.zoo_client.set(filename, data_json)

    def dump_conversation_data(self, filename, data):
        self.zoo_client.ensure_path(filename)
        data_json = json.dumps(enocde_conversations_to_json(data)).encode('utf-8')
        self.zoo_client.set(filename, data_json)

    def get_user_data(self):
        if self.user_data:
            pass
        data = self.load_user_chat_data(data_type='user_data')
        if not data:
            data = defaultdict(dict)
        else:
            data = defaultdict(dict, data)
        self.user_data = data
        return deepcopy(self.user_data)

    def get_chat_data(self):
        if self.chat_data:
            pass
        data = self.load_user_chat_data(data_type='chat_data')
        if not data:
            data = defaultdict(dict)
        else:
            data = defaultdict(dict, data)
        self.chat_data = data
        return deepcopy(self.chat_data)

    # TODO test conversations persistent
    def get_conversations(self, name):
        if self.conversations:
            pass
        filename = r'/%s/conversations' % self.main_node
        data = self.load_conversation_data(filename)
        if not data:
            data = {name: {}}
        self.conversations = data
        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state):
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        if not self.on_flush:
            filename = r'/%s/conversations' % self.main_node
            self.dump_conversation_data(filename, self.conversations)

    def update_user_data(self, user_id, data):
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        if not self.on_flush:
            filename = r'/%s/%s/user_data' % (self.main_node, self.get_user_id(self.user_data))
            self.dump_user_chat_data(filename, self.user_data)

    def update_chat_data(self, chat_id, data):
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        if not self.on_flush:
            filename = r'/%s/%s/chat_data' % (self.main_node, self.get_user_id(self.chat_data))
            self.dump_user_chat_data(filename, self.chat_data)

    def flush(self):
        if self.user_data:
            for user_id in list(self.user_data.keys()):
                filename = r'/%s/%s/user_data' % (self.main_node, user_id)
                self.dump_user_chat_data(filename, {key: value for (key, value) in self.user_data.items() if key == user_id})
        if self.chat_data:
            for chat_id in list(self.chat_data.keys()):
                filename = r'/%s/%s/chat_data' % (self.main_node, chat_id)
                self.dump_user_chat_data(filename, {key: value for (key, value) in self.chat_data.items() if key == chat_id})
        if self.conversations:
            filename = r'/%s/conversations' % self.main_node
            self.dump_conversation_data(filename, dict(self.conversations))

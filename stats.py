"""
Because I am a scrub and cannot use MongoDB

What do I want to do?

    - Average response time
        - Have to group into "sessions" so it's not skewed
    - Dump all messages by one sender id
        - For markov chains
    - Emoji Usage
        - Will be hard with them being js-escaped

"""
from collections import defaultdict
import pymongo
import json


# TODO this is all disgusting and repetitious. Can be made lovely-ish


def title_gen(f):
    def wrapper(self, conversation):
        title = ' '.join(map(lambda x: x.title(), conversation.split('_')))
        title += ' - %s' % (' '.join(map(lambda x: x.title(), f.__name__.split('_'))),)
        res = f(self, conversation)
        return title, res
    return wrapper


class Statistics(object):

    def __init__(self, name):
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client[name]

    @title_gen
    def total_message_count(self, conversation):
        """
        Count the number of messages in a conversation
        Should not count empty messages
        (Almost) equivalent to:
        grep -e "sender" <name>.json | grep -Eo '":".*",' | cut -d '"' -f 3 | sort | uniq -c
        :return: a dict of {participant: count}
        """
        collection = self.mongo_db[conversation]
        all_messages = collection.find()
        counts = defaultdict(int)
        for message in all_messages:
            if message["text"]:
                counts[message["sender"]] += 1
        return counts

    @title_gen
    def total_message_length(self, conversation):
        """
        Count the length of all the messages in a conversation
        :return: a dict of {participation: length}
        """
        collection = self.mongo_db[conversation]
        all_messages = collection.find()
        counts = defaultdict(int)
        for message in all_messages:
            if message["text"]:
                counts[message["sender"]] += len(message["text"])
        return counts

    @title_gen
    def total_attachments_sent(self, conversation):
        """
        Count the number of attachments (photos etc) sent by each person
        """
        collection = self.mongo_db[conversation]
        all_messages = collection.find()
        counts = defaultdict(int)
        for message in all_messages:
            if message["attachments"]:
                counts[message["sender"]] += len(message["attachments"])
        return counts

    @title_gen
    def average_message_length(self, conversation):
        _, t_l = self.total_message_length(conversation)
        _, t_c = self.total_message_count(conversation)

        d = defaultdict(float)
        for k, v in t_l.items():
            d[k] = v/t_c[k]
        return d

    @title_gen
    def cumulative_messages_sent(self, conversation):
        # TODO
        pass

    def for_all(self, function):
        """
        Calculate a stat for all conversations
        """
        dic = dict()
        for coll in self.mongo_db.list_collection_names():
            if coll != "users":
                dic[coll] = function(coll)
        return dic

    def retrieve_name(self, id):
        """ get name from the users database """
        collection = self.mongo_db["users"]
        res = collection.find({"user_id": str(id)}, {"user_name": 1}).limit(1)
        for r in res:
            return r["user_name"]
        return str(id)

    @staticmethod
    def sort_dict(dic):
        """ return as sorted list """
        return sorted([(k, v) for k, v in dic.items()], key=lambda a: a[1], reverse=True)

if __name__ == "__main__":
    s = Statistics("messages_oliver_gratton")
    print(json.dumps(s.total_message_count("jack_morrison")[1]))
    print(json.dumps(s.total_message_length("jack_morrison")[1]))
    print(json.dumps(s.average_message_length("jack_morrison")[1]))
    # print(json.dumps(s.for_all(s.average_message_length)))
    # print(s.retrieve_name(100005848782846))

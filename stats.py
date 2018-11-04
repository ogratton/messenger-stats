"""
Because I am a scrub and cannot use MongoDB

What do I want to do?

    - Average response time
        - Have to group into "sessions" so it's not skewed
    - Dump all messages by one sender id
        - For markov chains


    maybe something using this sort of thing:
    grep -e "> begin:place_orders" -e " recv " jabet-placer-jasperwh.log | grep place -A1 | grep recv | grep -Eo 'in .*' | cut -c-6 | sort | uniq -c

"""
from collections import defaultdict
import pymongo


# TODO this is all disgusting and repetitious. Can be made lovely


class Statistics(object):

    def __init__(self, name):
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client[name]

    def total_message_count(self, conversation):
        """
        Count the number of messages in a conversation
        Should not count empty messages
        (Almost) equivalent to:
        grep -e "sender" thomas_brex.json | grep -Eo '":".*",' | cut -d '"' -f 3 | sort | uniq -c
        :return: a dict of {participant: count}
        """
        collection = self.mongo_db[conversation]
        all_messages = collection.find()
        counts = defaultdict(int)
        for message in all_messages:
            if message["text"]:
                counts[message["sender"]] += 1
        return sorted([(k, v) for k, v in counts.items()], key=lambda a: a[1], reverse=True)

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
        return sorted([(k, v) for k, v in counts.items()], key=lambda a: a[1], reverse=True)

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
        return sorted([(k, v) for k, v in counts.items()], key=lambda a: a[1], reverse=True)

    def for_all(self, function):
        """
        Calculate a stat for all conversations
        """
        dic = dict()
        for coll in self.mongo_db.list_collection_names():
            if coll != "users":
                dic[coll] = function(coll)
        return dic

if __name__ == "__main__":
    s = Statistics("messages_oliver_gratton")
    # print(s.total_message_count("maurice_hewins"))
    # print(s.total_message_length("maurice_hewins"))
    # print(s.total_attachments_sent("maurice_hewins"))
    print(s.for_all(s.total_message_count))

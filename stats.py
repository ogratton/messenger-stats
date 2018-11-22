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
import bson


# TODO this is all disgusting and repetitious. Can be made lovely-ish

class Statistics(object):

    def __init__(self, name):
        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mongo_db = self.mongo_client[name]

    def total_messages_sent(self, conversation):
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

    def total_messages_length(self, conversation):
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

    def average_message_length(self, conversation):
        t_l = self.total_messages_length(conversation)
        t_c = self.total_messages_sent(conversation)

        d = defaultdict(float)
        for k, v in t_l.items():
            d[k] = v/t_c[k]
        return d

    def time_chunks(self, conversation, resolution="month"):
        collection = self.mongo_db[conversation]

        # TODO fill in the gaps with zeroes (or just pad either side of an edge value)

        format = {
            "year": "%Y",
            "month": "%Y-%m",
            "month_only": "%m",
            "day": "%Y-%m-%d",
            "day_only": "%d",
            "hour": "%Y-%m-%dT%H:00",
            "hour_only": "%H:00",
            "minute": "%Y-%m-%dT%H:%M",
            "second": "%Y-%m-%dT%H:%M:%SZ"
        }[resolution]

        result = collection.aggregate([{
                    "$match": {"$and": [{"text": {"$ne": None}}, {"text": {"$ne": ""}}]}
                }, {
                    "$project": {
                        "timestamp": {"$dateToString": {"format": format, "date": "$timestamp"}},
                    }
                }, {
                    "$group": {
                        "_id": "$timestamp",
                        "count": {"$sum": 1}
                    }
                }, {
                    "$project": {
                        "_id": 0,
                        "timestamp": "$_id",
                        "count": 1
                    }
                }, {
                    "$sort": {"timestamp": 1}
                }
            ]
        )

        return result

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
    # print(json.dumps(s.total_messages_sent("jack_morrison")))
    # print(json.dumps(s.total_messages_length("jack_morrison")))
    # print(json.dumps(s.average_message_length("jack_morrison")))
    # print(json.dumps(s.for_all(s.average_message_length)))
    # print(s.retrieve_name(100005848782846))
    print(*s.time_chunks("wales_is_fuckin_sick", resolution="year"), sep=', ')

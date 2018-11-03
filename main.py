#!/usr/bin/python3
"""
TODO LIST
    * store in mongodb
    * load recent messages rather than whole thing again every time
    * dump all conversations (or first X)
"""
from fbchat import Client
from fbchat.models import *
import json
import functools
import os
import datetime


def requires_login(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.client.isLoggedIn():
            self.login()
        return f(self, *args, **kwargs)
    return wrapper


def catch_interrupt(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except KeyboardInterrupt:
            self.logout()
    return wrapper


class Session:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = self.login()

    def login(self):
        print("Logging in")
        try:
            client = Client(self.username, self.password)
        except FBchatUserError as e:
            raise ValueError(e)
        return client

    def logout(self):
        if self.client.isLoggedIn():
            print("Logging out")
            self.client.logout()
        else:
            print("Not logged in anyway")

    @requires_login
    def get_client(self):
        return self.client

    @requires_login
    def send_message(self, text, recipient, tt):
        thread_type = {'user': ThreadType.USER, 'group': ThreadType.GROUP}[tt]
        message_id = self.client.send(
            Message(text=text),
            thread_id=recipient,
            thread_type=thread_type
        )
        print('Sent: "%s" to %s %s' % (text, tt, recipient))
        return message_id

    @requires_login
    def react(self, message_id, reaction):
        self.client.reactToMessage(message_id, reaction)

    @staticmethod
    def user_to_dict(user):
        return {
            "user_id": user.uid,
            "user_name": user.name,
            "user_photo": user.photo,
            "user_url": user.url
        }

    @staticmethod
    def group_to_dict(group):
        return {
            "participants": list(group.participants),
            "nicknames": group.nicknames
            # TODO some more fluff too
        }

    @staticmethod
    def parse_message_reaction(reaction_dict):
        reacts = {
            MessageReaction.LOVE: "love",
            MessageReaction.SMILE: "smile",
            MessageReaction.WOW: "wow",
            MessageReaction.SAD: "sad",
            MessageReaction.ANGRY: "angry",
            MessageReaction.YES: "yes",
            MessageReaction.NO: "no"
        }
        json_friendly_dict = dict()
        for k, v in reaction_dict.items():
            json_friendly_dict[k] = reacts[v]
        return json_friendly_dict

    def message_to_dict(self, message):
        """
        :type message: Message
        """
        # TODO attachments will be tricky in json
        return {
            "text": message.text,
            "sender": message.author,
            "timestamp": str(datetime.datetime.utcfromtimestamp(int(message.timestamp[:10]))),
            # "mentions": message.mentions,
            "is_read": message.is_read,
            "read_by": message.read_by,
            "reactions": self.parse_message_reaction(message.reactions),
            # "emoji_size"
            # "sticker"
            # "attachments"
            "message_id": message.uid
        }

    @requires_login
    def history_to_json(self, user, limit=1, before=None):
        history = self.client.fetchThreadMessages(user.uid, limit=limit, before=before)
        print("Retrieved %s messages" % (len(history),))
        # NOTE: history comes out newest first
        first_timestamp = history[-1].timestamp
        return (
            first_timestamp,
            len(history),
            [
                json.dumps(self.message_to_dict(message), separators=(',', ':'), indent=4)
                for message in reversed(history)
            ]
        )

    def _get_full_history(self, user):
        num = 10000
        received = 10000
        chunks = []
        messages = []
        before = None

        while received == num:
            if before is not None:
                print("Chunk before %s" % (datetime.datetime.utcfromtimestamp(int(before[:10])),))
            before, received, json_contents = self.history_to_json(user, limit=num, before=before)
            chunks.append(json_contents)
        for chunk in reversed(chunks):
            messages.extend(chunk)

        return messages

    def get_history(self, user, limit=None, before=None):
        if limit is None and before is None:
            return self._get_full_history(user)

    @requires_login
    def search_users(self, name):
        """
        Return list of users matching name,
        best match first
        """
        # TODO give the user a choice of the results
        return self.client.searchForUsers(name)

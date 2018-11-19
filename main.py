#!/usr/bin/python3
"""
TODO LIST
    * store in mongodb
    * load recent messages rather than whole thing again every time
    * dump all conversations (or first X)
"""
from fbchat import Client
from fbchat.models import *
import functools
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

    def __init__(self, username, password, users_name):
        self.username = username
        self.password = password
        self.client = self.login()

        # TODO temp
        self.users_name = users_name
        # self.user_obj = self.get_user()

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
    def get_user(self):
        """
        Return the user blob of the person logged in
        """
        # TODO for now we need them to also tell us their name
        return self.client.searchForUsers(self.users_name)[0]

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
            "user_url": user.url,
            "affinity": user.affinity
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

    @staticmethod
    def parse_attachment(attachment):
        if hasattr(attachment, "url"):
            # Stickers, files, audio
            if attachment.url is not None:
                return str(attachment.url)
        if hasattr(attachment, "animated_preview_url"):
            # Animated stickers & gifs and stuff
            if attachment.animated_preview_url is not None:
                return str(attachment.animated_preview_url)
        if hasattr(attachment, "large_preview_url"):
            # Images
            if attachment.large_preview_url is not None:
                return str(attachment.large_preview_url)
        if hasattr(attachment, "large_image_url"):
            # Videos
            if attachment.large_image_url is not None:
                return str(attachment.large_image_url)

    def parse_attachments(self, attachments):
        # TODO this is bad
        lst = []
        if attachments:
            for attachment in attachments:
                lst.append(self.parse_attachment(attachment))
            return lst

    @staticmethod
    def parse_mentions(mentions):
        # TODO parse mentions
        return mentions

    def message_to_dict(self, message):
        """
        :type message: Message
        """
        return {
            "text": message.text,
            "sender": message.author,
            # TODO we get rid of microseconds because they aren't always given
            "timestamp": str(datetime.datetime.utcfromtimestamp(int(message.timestamp[:10]))),
            # "mentions": self.parse_mentions(message.mentions),  # TODO
            "is_read": message.is_read,
            "read_by": message.read_by,
            "reactions": self.parse_message_reaction(message.reactions),
            # "emoji_size"
            "sticker": self.parse_attachment(message.sticker),
            "attachments": self.parse_attachments(message.attachments),
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
            [self.message_to_dict(message) for message in reversed(history)]
        )

    def _get_full_history(self, user):
        num = 10000
        received = 10000
        chunks = []
        messages = []
        before = None

        while received == num:
            if before is not None:
                print("Getting chunk before %s" % (datetime.datetime.utcfromtimestamp(int(before[:10])),))
            before, received, json_contents = self.history_to_json(user, limit=num, before=before)
            chunks.append(json_contents)
        for chunk in reversed(chunks):
            messages.extend(chunk)

        return messages

    def get_history(self, user, limit=None, before=None):
        if limit is None and before is None:
            return self._get_full_history(user)

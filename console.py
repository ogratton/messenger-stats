"""
Command-line interface
"""
# from getpass import getpass
from main import Session
from time import sleep
from functools import wraps
from fbchat.models import Group, User
import pymongo
import json
import os


class CommandException(Exception):
    pass


def command(func):
    # TODO 'usage' as decorator arg
    # TODO make it useful or lose it
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # func.command = True
        return func(*args, **kwargs)
    return wrapper


class Console(object):

    results_size = 5

    def __init__(self):
        self.sesh = self.login()
        self.active_selection = None

        self.mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
        # self.user = self.sesh.user_obj
        self.username = self.sesh.users_name.replace(' ', '_').lower()
        db_name = "messages_%s" % (self.username,)
        self.mongo_db = self.mongo_client[db_name]
        self.add_user_to_db(self.sesh.get_user())

        self.commands = {
            "help": self.help,
            "select_user": self.select_user,
            "select_group": self.select_group,
            "messages": self.messages,
            "quit": self.quit
        }

    @staticmethod
    def login():
        usr = input("email:")
        # TODO security \o/
        pwd = input('password:')
        name = input('your name:')

        # TODO super secure
        if not usr and not pwd and not name:
            with open("info", 'r') as info:
                info = json.loads(info.read())
                usr = info["usr"]
                pwd = info["pwd"]
                name = info["name"]

        try:
            return Session(usr, pwd, name)
        except ValueError as e:
            print(e)

    def help(self):
        """
        Print list of all commands
        """
        for name, f in self.commands.items():
            # TODO put usage in place of name and remove usage from doc
            # use @command?
            print(name, f.__doc__)

    def select_user(self, *args):
        """
        select_user <name>
        Searches for a person and returns a list of candidates
        """
        search_string = ' '.join(args)
        users = self.sesh.client.searchForUsers(search_string)
        return self._select_user_result(users, "user")

    def select_group(self, *args):
        """
        select_group <name>
        Searches for a group and returns a list of candidates
        """
        search_string = ' '.join(args)
        groups = self.sesh.client.searchForGroups(search_string)
        return self._select_user_result(groups, "group")

    def _select_user_result(self, users, type):
        """
        Display a list of search results and ask for a selection
        """
        if not users:
            print('< No results found!')
            return False
        pages = self._pagify_list(users, self.results_size)
        i = 0
        while True:
            for page in pages:
                for _ in page:
                    print("[%d] %s" % (i, users[i].name))
                    i += 1
            inp = input('< Select a %s, or type "n" to cancel\n>' % (type,))
            if inp in ['', 'n']:
                break
            error_msg = '< Please enter the number of the search result you want to select\n'
            try:
                index = int(inp)
                if index < len(users):
                    selection = users[index]
                    print("< Selected %s" % (selection.name,))
                    self.active_selection = selection
                    return True
                else:
                    print(error_msg)
            except ValueError:
                print(error_msg)
        return True

    def messages(self, log="db", limit=None, before=None):
        """
        get_messages <?log> <?limit> <?before>
        Log: "file" or "db" (JSON file or MongoDB)
        If limit is empty, will return all
        If before is empty, will return from now
        Uses current selection (use select_group or select_user)
        """
        # TODO update existing files if we have it already
        # TODO ignore `limit` and `before` for the mo (always full)
        messages = self.sesh.get_history(self.active_selection, limit, before)

        if log == "file":
            self._to_file(messages)
        elif log == "db":
            self._to_db(messages)
        else:
            print("< Invalid logging method %s. Please use 'file' or 'db'" % (log,))

    def _to_file(self, messages):
        filename = "%s.json" % (self.active_selection.name.replace(' ', '_').lower())
        filepath = '/'.join((os.path.dirname(os.path.abspath(__file__)), "logs", filename))
        json_messages = json.dumps(messages, separators=(',', ':'), indent=4)
        with open(filepath, 'w+') as file_:
            print(json_messages, sep='\n', file=file_)

    def _to_db(self, messages):
        self._to_file(messages)
        self.add_user_to_db(self.active_selection)
        # to do manually from the logs:
        # mongoimport --db messages --collection ?<name> --file logs/?<name>.json --jsonArray
        name = self.active_selection.name.replace(' ', '_').lower()
        coll = self.mongo_db[name]
        coll.remove()
        coll.insert(messages)
        print('< Inserted message history into messages database')

    def add_user_to_db(self, user):
        coll = self.mongo_db["users"]
        if isinstance(user, Group):
            # TODO do each user
            # for p in user.participants:
            #     coll.insert(p)
            print('< TODO insert group members into user database')
        elif isinstance(user, User):
            replacement = self.sesh.user_to_dict(user)
            coll.find_one_and_replace({"user_id": replacement["user_id"]}, replacement)
            print('< Inserted %s into the users database' % (user.name,))

    def quit(self):
        print("< Logging out")
        self.sesh.logout()
        exit()

    @staticmethod
    def _pagify_list(lst, pg_size):
        num_slices = 1 + len(lst) // pg_size
        slices = []
        for i in range(num_slices):
            j = i*pg_size
            slices.append(lst[j:j+pg_size])
        return slices

    def run(self):
        """
        Input loop
        """
        sleep(0.5)
        try:
            while True:
                inp = input(">")
                words = inp.split(" ")
                f, args = words[0], words[1:]
                if f in self.commands:
                    try:
                        self.commands[f](*words[1:])
                    except CommandException as e:
                        print(e)
                else:
                    print('Invalid input "%s". Type help for list of commands' % (f,))
        except KeyboardInterrupt:
            self.quit()

if __name__ == '__main__':
    cons = Console()
    cons.run()

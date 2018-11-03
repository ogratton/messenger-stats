"""
Command-line interface
"""
from getpass import getpass
from main import Session
import json


class Console(object):

    def __init__(self):
        self.sesh = self.login()
        self.run()

    @staticmethod
    def login():
        usr = input("email:")
        pwd = getpass('password:')

        # TODO super secure
        if not usr and not pwd:
            with open("info", 'r') as info:
                info = json.loads(info.read())
                usr = info["usr"]
                pwd = info["pwd"]

        return Session(usr, pwd)

    def help(self):
        """
        Print list of all commands
        """

    def run(self):
        """
        Input loop
        """
        while True:
            # TODO big old if blob of commands
            inp = input(">")
            try:
                getattr
            except:
                print("Invalid input. Type help for list of commands.")

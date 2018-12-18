import cmd
import readline
import os
import getpass

import sys
sys.path.append("../..")

import clfpy as cf

from cli_gss import GssCLI
from cli_services import ServicesCLI

AUTH_endpoint = "https://api.hetcomp.org/authManager/AuthManager?wsdl"
CLIENTS = {
    "gss": GssCLI,
    "services": ServicesCLI
}


class CLI(cmd.Cmd):

    def __init__(self):
        super(CLI, self).__init__()
        auth = cf.AuthClient(AUTH_endpoint)
        if "CFG_TOKEN" in os.environ:
            print("Found environment variable 'CFG_TOKEN'")
            self.session_token = os.environ["CFG_TOKEN"]
        else:
            self.session_token = self.authenticate(auth)

        self.user = auth.get_username(self.session_token)
        self.project = auth.get_project(self.session_token)

    def authenticate(self, auth):
        try:
            username = os.environ['CFG_USERNAME']
            password = os.environ['CFG_PASSWORD']
            project = os.environ['CFG_PROJECT']
            print("Found environment variables for username, password, "
                  "and token")
        except KeyError:
            username = input("Please enter username: ")
            project = input("Please enter project: ")
            password = getpass.getpass("Please enter password: ")

        print("Logging in ...")
        session_token = auth.get_session_token(username, project, password)
        if "401" in str(session_token):
            print("Error: Authentication failed")
            exit()
        return session_token

    def preloop(self):
        self.client = None
        self.update_prompt()

        self.intro = ("\nWelcome to the CloudFlow command line interface."
                      "\nChoose a client by typing 'client CLIENT' "
                      f"({list(CLIENTS.keys())} available)")

    def update_prompt(self):
        self.prompt = (f"\n{self.user}@{self.project}: ")

    def do_client(self, client_ID):
        """Select a client. Usage: client CLIENT_NAME"""
        if client_ID.lower() not in CLIENTS:
            print(f"Unknown client ID {client_ID}")
        else:
            client = CLIENTS[client_ID](self.session_token, self.user,
                                        self.project)
            client.cmdloop()

    def complete_client(self, text, line, begidx, endidx):
        candidates = list(CLIENTS.keys())
        matches = [c for c in candidates if c.startswith(text)]
        return matches

    def do_shell(self, arg):
        """Execute a shell command. Usage: shell CMD"""
        os.system(arg)

    def do_exit(self, arg):
        """Exit the application."""
        print('Goodbye')
        return True

    def do_EOF(self, arg):
        """Exit the application."""
        print('Goodbye')
        return True


if __name__ == '__main__':
    CLI().cmdloop()

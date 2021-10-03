#!/bin/python3

import sys
import subprocess
import os
from os import path
import random


PYTHON = sys.executable

if os.name in ("nt", "dos"):
    VIM = 'C:\\Program Files (x86)\\Vim\\vim82\\gvim.exe'
else:
    import shutil
    VIM = shutil.where("vim")


class PyConsole:
    def __init__(self, argv):
        self.root_dir = path.dirname(path.abspath(argv[0]))

        self.script_dir =    path.join(self.root_dir, "scripts")
        self.pyconsole_vim = path.join(self.root_dir, "pyconsole.vim")
        self.pyconsole_py =  path.join(self.root_dir, "pyconsole.py")

        self.tmux_failed = False
        self.id = None

    def reset(self):
        self.tmux_failed = False
        self.generate_id()

        if not path.exists(self.script_dir):
            os.mkdir(self.script_dir)

        while path.exists(self.pyconsole_script):
            self.generate_id()

        self.claim_file()

    @property
    def pyconsole_script(self):
        return path.join(self.script_dir, self.id + ".py")

    def generate_id(self):
        n = random.randint(1E4, 1E5-1)
        self.id = f"pyconsole_{n}"

    def claim_file(self):
        with open(self.pyconsole_script, "x") as f:
            f.write("")

    def start(self):
        self.reset()

        try:
            tmux_command = [
                "tmux",
                "new-session", "-s", self.id, "-d",
                f"{PYTHON} {self.pyconsole_py} {self.pyconsole_script}"
            ]
            subprocess.call(tmux_command)

            subprocess.call(
                self.vim_command(f"tmux a -t {self.id}")
            )

        except FileNotFoundError:
            self.tmux_failed = True

            subprocess.call(
                self.vim_command(f"{PYTHON} {self.pyconsole_py} {self.pyconsole_script}")
            )

        self.cleanup()

    def vim_command(self, command):
        return [
            VIM, "-c", "let b:command=\"" + command + 
            f"\" | source {self.pyconsole_vim}", self.pyconsole_script
        ]

    def cleanup(self):
        if not self.tmux_failed:
            tmux_command = [
                "tmux", "kill-session", "-t", self.id
            ]
            subprocess.call(tmux_command)

        if path.exists(self.pyconsole_script):
            os.remove(self.pyconsole_script)


if __name__ == "__main__":
    pyconsole = PyConsole(sys.argv)
    pyconsole.start()

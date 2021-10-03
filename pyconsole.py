#!/bin/python3

import re
import ast
import os
import sys
import traceback

import pynput
from pynput.keyboard import Key
from pynput.mouse import Button

from global_env import global_env

class Session:
    default_globals = global_env

    def __init__(self):
        self.globals = self.default_globals.copy()
        self.extra_utils()

    def __contains__(self, key):
        return key in self.globals

    def reset(self):
        self.globals.clear()
        for key, value in self.default_globals.items():
            self.globals[key] = value
        self.extra_utils()
        self.refresh()

    def extra_utils(self):
        self.globals["Key"] = Key
        self.globals["Button"] = Button
        self.globals["exit"] = exit
        self.globals["quit"] = exit
        self.globals["reset"] = self.reset

    def refresh(self):
        self.globals["mouse"] = pynput.mouse.Controller()
        self.globals["keyboard"] = pynput.keyboard.Controller()


class Exit(Exception):
    pass

def exit():
    raise Exit

def clear(n_lines=100):
    if os.name == "posix":
        os.system("clear")
    elif os.name in ("nt", "dos", "ce"):
        os.system("cls")
    else:
        print("\n" * n_lines)

def make_print(body):
    for i, node in enumerate(body):
        if hasattr(node, "body"):
            make_print(node.body)
        elif isinstance(node, ast.Expr):
            body[i] = ast.If(
                test=ast.Compare(
                    left=ast.NamedExpr(
                        target=ast.Name(
                            id="_",
                            ctx=ast.Store()
                        ),
                        value=node.value
                    ),
                    ops=[ast.IsNot()],
                    comparators=[ast.Constant(value=None)]
                ),
                body=[
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Name(
                                id="print",
                                ctx=ast.Load()
                            ),
                            args=[
                                ast.Name(
                                    id="_",
                                    ctx=ast.Load()
                                )
                            ],
                            keywords=[]
                        )
                    )
                ],
                orelse=[]
            )

modules = {
    "random": [
        "randint",
        "random",
        "choice",
        "seed"
    ],
    "time": [
        "sleep",
        "time"
    ],
    "math": [
        "floor",
        "ceil",
        "sin",
        "cos",
        "tan"
    ]
}


def fix_idiot(tree):
    if hasattr(tree, "__dict__"):
        for value in tree.__dict__.values():
            if isinstance(value, list):
                for subtree in value:
                    fix_idiot(subtree)
            else:
                fix_idiot(value)

        if not isinstance(tree, ast.Call) or \
                not isinstance(tree.func, ast.Attribute) or \
                not isinstance(tree.func.value, ast.Name) or \
                (id := tree.func.value.id) not in modules or \
                tree.func.attr not in modules[id]:
            return

        tree.func = ast.Name(tree.func.attr, ctx=ast.Load())


def exec_script(script, session):
    tree = ast.parse(script)
    make_print(tree.body)
    fix_idiot(tree)
    ast.fix_missing_locations(tree)
    exec(
        compile(tree, filename="<ast>", mode="exec"),
        session.globals,
        session.globals
    )

if __name__  == "__main__":
    file_name = sys.argv[1]

    session = Session()

    with open(file_name, "r") as f:
        script = f.read()

    while True:
        session.refresh()

        while True:
            try:
                input()
                break
            except KeyboardInterrupt:
                pass

        with open(file_name, "r") as f:
            script = f.read()

        try:
            clear()

            if "on_key_press" in session:
                del session.globals["on_key_press"]
            if "on_key_release" in session:
                del session.globals["on_key_release"]

            exec_script(script, session)

            if "on_key_press" in session or \
                    "on_key_release" in session:
                if "on_key_press" not in session:
                    session.globals["on_key_press"] = lambda key: 1;
                if "on_key_release" not in session:
                    session.globals["on_key_release"] = lambda key: 1;
                with pynput.keyboard.Listener(
                    on_press=session.globals["on_key_press"],
                    on_release=session.globals["on_key_release"]
                ) as listener:
                    listener.join()


        except KeyboardInterrupt:
            pass

        except Exit:
            pass

        except Exception:
            tb = traceback.format_exc()
            print(tb)

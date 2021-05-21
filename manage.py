#!/bin/env python
"""
Management script template file for python projects.

Individual commands are defined in subclasses of `CommandMixin`.
This script recovers all declared commands and builds an argument
parser for them.

USAGE:
    1. Declare a subclass of CommandMixin
    2. Add arguments to the command's sub parser (`add_args`)
    3. Implement `run` logic
    4. Invoke from CLI (python manage.py)
"""
import sys
from argparse import ArgumentParser
from pathlib import Path
from subprocess import run


class CommandMixin:
    """Base class for management commands.  Class name will be the command
    name (all lower case) and its docstring will be the command help message"""

    @property
    def project_root(self):
        return Path(__file__).resolve().parent

    @classmethod
    def add_args(cls, parser):
        """Add args to commands"""
        pass

    def run(self, **kwargs):
        """Command logic"""
        raise NotImplementedError


class CommandProxyMixin(CommandMixin):
    """Helper class that simply proxies a command to a shell,
    preserving argument"""

    command = "echo"
    default = None
    
    @property
    def __doc__(self):
        return f"Runs {self.command} with received arguments"

    @classmethod
    def add_args(cls, parser):
        """Takes any number of arguments and sends it to proxied command"""
        help=f'Arguments that will be sent to "{cls.command}"'
        if cls.default: 
            parser.add_argument("args", nargs="*", default=[cls.default], help=help)
        else:
            parser.add_argument("args", nargs="*", help=help)

    def run(self, args):
        """Joins command defined in self with arguments received and pass it
        to a shell"""
        cmd = [token for token in self.command.split(' ') if token]
        cmd = cmd + args
        cmd = " ".join(cmd)
        run(cmd, stdout=sys.stdout, stderr=sys.stderr, shell=True)


## Default Command
class Test(CommandProxyMixin):
    command = "python -m unittest"
    default = "discover"


# Helpers for main
def _get_commands():
    """Return dict with all subclasses of CommandMixin"""
    predicate = lambda value: CommandMixin in getattr(value, "__mro__", []) and value is not CommandMixin and value is not CommandProxyMixin
    values = globals().values()
    return {value.__name__.lower(): value for value in values if predicate(value)}


def build_parser():
    """Build parser adding all subcommands"""
    parser = ArgumentParser("Management scripts runner")
    subparser = parser.add_subparsers(dest="subcommand", required=True)
    for name, command in _get_commands().items():
        command_parser = subparser.add_parser(name, help=command.__doc__)
        command.add_args(command_parser)
    return parser


def main():
    commands = _get_commands()
    parser = build_parser()
    args = parser.parse_args().__dict__
    command_name = args.pop("subcommand")
    command_klass = commands[command_name]
    command = command_klass()
    command.run(**args)


if __name__ == "__main__":
    main()

# Copyright (c) 2016 Robbin Bonthond

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# ------------------------------------------------------------------------------------
# modified to avoid conflcts with rich_click

# sourcery skip: assign-if-exp, use-named-expression

import rich_click as click

_click7 = click.__version__[0] >= "7"


class ClickAliasedGroup(click.RichGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._commands = {}
        self._aliases = {}

    def add_command(self, *args, **kwargs):
        aliases = kwargs.pop("aliases", [])
        super().add_command(*args, **kwargs)
        if aliases:
            cmd = args[0]
            name = args[1] if len(args) > 1 else None
            name = name or cmd.name
            if name is None:
                raise TypeError("Command has no name.")

            self._commands[name] = aliases
            for alias in aliases:
                self._aliases[alias] = cmd.name

    def command(self, *args, **kwargs):
        aliases = kwargs.pop("aliases", [])
        decorator = super().command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def group(self, *args, **kwargs):
        aliases = kwargs.pop("aliases", [])
        decorator = super().group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def resolve_alias(self, cmd_name):
        if cmd_name in self._aliases:
            return self._aliases[cmd_name]
        return cmd_name

    def get_command(self, ctx, cmd_name):
        cmd_name = self.resolve_alias(cmd_name)
        command = super().get_command(ctx, cmd_name)
        if command:
            return command
        return None

    # def format_commands(self, ctx, formatter):
    # TODO: output alias with commands - but that is a significant re-write
    # for now add alias to help text


# ------------------------------------------------------------------------------------

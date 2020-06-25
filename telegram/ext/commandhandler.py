#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2020
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""This module contains the CommandHandler and PrefixHandler classes."""
import re

from future.utils import string_types

from telegram.ext import Filters

from telegram import Update, MessageEntity
from .handler import Handler


class CommandHandler(Handler):
    """Handler class to handle Telegram commands.

    Commands are Telegram messages that start with ``/``, optionally followed by an ``@`` and the
    bot's name and/or some additional text. The handler will add a ``list`` to the
    :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of strings,
    which is the text following the command split on single or consecutive whitespace characters.

    By default the handler listens to messages as well as edited messages. To change this behavior
    use ``~Filters.update.edited_message`` in the filter argument.

    Attributes:
        command (:obj:`str` | List[:obj:`str`]): The command or list of commands this handler
            should listen for. Limitations are the same as described here
            https://core.telegram.org/bots#commands
        callback (:obj:`callable`): The callback function for this handler.
        filters (:class:`telegram.ext.BaseFilter`): Optional. Only allow updates with these
            Filters.

    Args:
        command (:obj:`str` | List[:obj:`str`]): The command or list of commands this handler
            should listen for. Limitations are the same as described here
            https://core.telegram.org/bots#commands
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not).

    Raises:
        ValueError - when command is too long or has illegal chars.
    """

    def __init__(self, command, callback, filters=None):
        super(CommandHandler, self).__init__(callback)

        if isinstance(command, string_types):
            self.command = [command.lower()]
        else:
            self.command = [x.lower() for x in command]
        for comm in self.command:
            if not re.match(r'^[\da-z_]{1,32}$', comm):
                raise ValueError('Command is not a valid bot command')

        if filters:
            self.filters = Filters.update.messages & filters
        else:
            self.filters = Filters.update.messages

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`list`: The list of args for the handler

        """
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if (message.entities and message.entities[0].type == MessageEntity.BOT_COMMAND
                    and message.entities[0].offset == 0):
                command = message.text[1:message.entities[0].length]
                args = message.text.split()[1:]
                command = command.split('@')
                command.append(message.bot.username)

                if not (command[0].lower() in self.command
                        and command[1].lower() == message.bot.username.lower()):
                    return None

                filter_result = self.filters(update)
                if filter_result:
                    return args, filter_result
                else:
                    return False

    def collect_additional_context(self, context, update, dispatcher, check_result):
        context.args = check_result[0]
        if isinstance(check_result[1], dict):
            context.update(check_result[1])


class PrefixHandler(CommandHandler):
    """Handler class to handle custom prefix commands

    This is a intermediate handler between :class:`MessageHandler` and :class:`CommandHandler`.
    It supports configurable commands with the same options as CommandHandler. It will respond to
    every combination of :attr:`prefix` and :attr:`command`. It will add a ``list`` to the
    :class:`CallbackContext` named :attr:`CallbackContext.args`. It will contain a list of strings,
    which is the text following the command split on single or consecutive whitespace characters.

    Examples::

        Single prefix and command:

            PrefixHandler('!', 'test', callback) will respond to '!test'.

        Multiple prefixes, single command:

            PrefixHandler(['!', '#'], 'test', callback) will respond to '!test' and
            '#test'.

        Miltiple prefixes and commands:

            PrefixHandler(['!', '#'], ['test', 'help`], callback) will respond to '!test',
            '#test', '!help' and '#help'.


    By default the handler listens to messages as well as edited messages. To change this behavior
    use ~``Filters.update.edited_message``.

    Attributes:
        prefix (:obj:`str` | List[:obj:`str`]): The prefix(es) that will precede :attr:`command`.
        command (:obj:`str` | List[:obj:`str`]): The command or list of commands this handler
            should listen for.
        callback (:obj:`callable`): The callback function for this handler.
        filters (:class:`telegram.ext.BaseFilter`): Optional. Only allow updates with these
            Filters.

    Args:
        prefix (:obj:`str` | List[:obj:`str`]): The prefix(es) that will precede :attr:`command`.
        command (:obj:`str` | List[:obj:`str`]): The command or list of commands this handler
            should listen for.
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        filters (:class:`telegram.ext.BaseFilter`, optional): A filter inheriting from
            :class:`telegram.ext.filters.BaseFilter`. Standard filters can be found in
            :class:`telegram.ext.filters.Filters`. Filters can be combined using bitwise
            operators (& for and, | for or, ~ for not).

    """

    def __init__(self,
                 prefix,
                 command,
                 callback,
                 filters=None):

        super(PrefixHandler, self).__init__('nocommand', callback, filters=filters)

        if isinstance(prefix, string_types):
            self.prefix = [prefix.lower()]
        else:
            self.prefix = prefix
        if isinstance(command, string_types):
            self.command = [command.lower()]
        else:
            self.command = command
        self.command = [x.lower() + y.lower() for x in self.prefix for y in self.command]

    def check_update(self, update):
        """Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`list`: The list of args for the handler

        """
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            if message.text:
                text_list = message.text.split()
                if text_list[0].lower() not in self.command:
                    return None
                filter_result = self.filters(update)
                if filter_result:
                    return text_list[1:], filter_result
                else:
                    return False

    def collect_additional_context(self, context, update, dispatcher, check_result):
        context.args = check_result[0]
        if isinstance(check_result[1], dict):
            context.update(check_result[1])

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
""" This module contains the InlineQueryHandler class """
import re

from future.utils import string_types

from telegram import Update
from .handler import Handler


class InlineQueryHandler(Handler):
    """
    Handler class to handle Telegram inline queries. Optionally based on a regex. Read the
    documentation of the ``re`` module for more information.

    Attributes:
        callback (:obj:`callable`): The callback function for this handler.
        pattern (:obj:`str` | :obj:`Pattern`): Optional. Regex pattern to test
            :attr:`telegram.InlineQuery.query` against.

    Args:
        callback (:obj:`callable`): The callback function for this handler. Will be called when
            :attr:`check_update` has determined that an update should be processed by this handler.
            Callback signature for context based API:

            ``def callback(update: Update, context: CallbackContext)``

            The return value of the callback is usually ignored except for the special case of
            :class:`telegram.ext.ConversationHandler`.
        pattern (:obj:`str` | :obj:`Pattern`, optional): Regex pattern. If not ``None``,
            ``re.match`` is used on :attr:`telegram.InlineQuery.query` to determine if an update
            should be handled by this handler.

    """

    def __init__(self,
                 callback,
                 pattern=None,):
        super(InlineQueryHandler, self).__init__(callback)

        if isinstance(pattern, string_types):
            pattern = re.compile(pattern)

        self.pattern = pattern

    def check_update(self, update):
        """
        Determines whether an update should be passed to this handlers :attr:`callback`.

        Args:
            update (:class:`telegram.Update`): Incoming telegram update.

        Returns:
            :obj:`bool`

        """

        if isinstance(update, Update) and update.inline_query:
            if self.pattern:
                if update.inline_query.query:
                    match = re.match(self.pattern, update.inline_query.query)
                    if match:
                        return match
            else:
                return True

    def collect_additional_context(self, context, update, dispatcher, check_result):
        if self.pattern:
            context.matches = [check_result]

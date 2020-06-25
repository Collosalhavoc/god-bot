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
from queue import Queue

import pytest

from telegram import (Update, CallbackQuery, Bot, Message, User, Chat, PollAnswer,
                      ChosenInlineResult, ShippingQuery, PreCheckoutQuery)
from telegram.ext import PollAnswerHandler, CallbackContext, JobQueue

message = Message(1, User(1, '', False), None, Chat(1, ''), text='Text')

params = [
    {'message': message},
    {'edited_message': message},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat', message=message)},
    {'channel_post': message},
    {'edited_channel_post': message},
    {'chosen_inline_result': ChosenInlineResult('id', User(1, '', False), '')},
    {'shipping_query': ShippingQuery('id', User(1, '', False), '', None)},
    {'pre_checkout_query': PreCheckoutQuery('id', User(1, '', False), '', 0, '')},
    {'callback_query': CallbackQuery(1, User(1, '', False), 'chat')}
]

ids = ('message', 'edited_message', 'callback_query', 'channel_post',
       'edited_channel_post', 'chosen_inline_result',
       'shipping_query', 'pre_checkout_query', 'callback_query_without_message')


@pytest.fixture(scope='class', params=params, ids=ids)
def false_update(request):
    return Update(update_id=2, **request.param)


@pytest.fixture(scope='function')
def poll_answer(bot):
    return Update(0, poll_answer=PollAnswer(1, User(2, 'test user', False), [0, 1]))


class TestPollAnswerHandler(object):
    test_flag = False

    @pytest.fixture(autouse=True)
    def reset(self):
        self.test_flag = False

    def callback_basic(self, update, context):
        self.test_flag = (isinstance(context, CallbackContext)
                          and isinstance(context.bot, Bot)
                          and isinstance(update, Update)
                          and isinstance(context.update_queue, Queue)
                          and isinstance(context.job_queue, JobQueue)
                          and isinstance(context.user_data, dict)
                          and context.chat_data is None
                          and isinstance(context.bot_data, dict)
                          and isinstance(update.poll_answer, PollAnswer))

    def test_basic(self, dp, poll_answer):
        handler = PollAnswerHandler(self.callback_basic)
        dp.add_handler(handler)

        assert handler.check_update(poll_answer)

        dp.process_update(poll_answer)
        assert self.test_flag

    def test_other_update_types(self, false_update):
        handler = PollAnswerHandler(self.callback_basic)
        assert not handler.check_update(false_update)

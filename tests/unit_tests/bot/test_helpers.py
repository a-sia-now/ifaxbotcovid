import pytest
import time

from ifaxbotcovid.bot.helpers import (MessageStorage,
                                      JointMessage, LogConstructor)


@pytest.fixture(scope='class')
def storage():
    return MessageStorage()


@pytest.fixture(scope='class')
def check_phrases():
    phrases = ['Hello', 'Foobar']
    return phrases


@pytest.fixture(scope='class')
def stop_phrase():
    phrase = 'Bye'
    return phrase


@pytest.fixture(scope='function')
def ready_storage(check_phrases, stop_phrase):
    kwargs = dict(
        check_phrases=check_phrases,
        stop_phrase=stop_phrase
    )
    r_storage = MessageStorage(**kwargs)
    r_storage.append(text='Hello there!', chat_id='11')
    r_storage.append(text='Unwanted string from different user', chat_id='42')
    r_storage.append(text="That's a Foobar", chat_id='11')
    r_storage.append(text='Bye, it is the last message.', chat_id='11')
    return r_storage


class TestMessageStorage:

    def test_message_storage_exist(self, storage):
        assert len(storage) == 1
        assert (
            type(storage._db[0].time) == float
            ) or (
            type(storage._db[0].time) == int
            )
        assert storage._db[0].text == ''
        assert storage._db[0].chat_id == ''

    def test_append(self, storage):
        storage.append(text='HelloWorld', chat_id='123')
        storage.append(text='LastInserted', chat_id='456')
        assert len(storage) == 3, 'Wrong storage length'
        assert (
            type(storage._db[1].time) == float and
            type(storage._db[2].time) == float
            ) or (
            type(storage._db[1].time) == int and
            type(storage._db[2].time) == int
            )
        assert storage._db[1].text == 'HelloWorld'
        assert storage._db[1].chat_id == '123'
        assert storage._db[2].text == 'LastInserted'
        assert storage._db[2].chat_id == '456'

    def test_last_message(self, storage):
        assert storage._db[-1].text == 'LastInserted'
        assert storage._db[-1].chat_id == '456'
        assert storage._last().text == 'LastInserted'
        assert storage._last().chat_id == '456'

    def test_last_before_last_message(self, storage):
        assert storage._last_before_last().text == 'HelloWorld'
        assert storage._last_before_last().chat_id == '123'

    def test_last_before_last_not_exist(self):
        storage = MessageStorage()  # empty, only one default message long
        assert not storage._last_before_last()

    def test_sequence(self, storage):
        storage.append(text='Bacon', chat_id='123')
        storage.append(text='Eggs', chat_id='456')
        storage.append(text='Spam', chat_id='123')
        sequence = storage._get_sequence()
        last_chat_id = '123'
        assert type(sequence) == tuple
        assert len(sequence) == 3
        assert set(
            message.chat_id for message in sequence
            ) == {last_chat_id}
        assert sequence[-1].text == 'Spam'
        assert sequence[-2].text == 'Bacon'
        assert sequence[-3].text == 'HelloWorld'

    def test_sequence_2(self, storage):
        storage.append(text='DeadParrot', chat_id='456')
        storage.append(text='KingAuthor', chat_id='456')
        sequence = storage._get_sequence()
        last_chat_id = '456'
        assert len(sequence) == 4
        assert set(
            message.chat_id for message in sequence
            ) == {last_chat_id}
        assert sequence[-1].text == 'KingAuthor'
        assert sequence[-2].text == 'DeadParrot'
        assert sequence[-3].text == 'Eggs'
        assert sequence[-4].text == 'LastInserted'

    def test_check_phrases_default(self, storage):
        assert storage.check_phrases == []
        assert storage.stop_phrase == ''

    def test_check_phrases_assignment(self,
                                      check_phrases,
                                      stop_phrase):

        new_msg_storage = MessageStorage(
            check_phrases=check_phrases,
            stop_phrase=stop_phrase
        )
        assert new_msg_storage.check_phrases == check_phrases
        assert new_msg_storage.stop_phrase == stop_phrase

    def test_joint_message(self,
                           check_phrases,
                           stop_phrase,
                           ready_storage):
        text = 'This is some joint message. Hello!'
        joint_message = JointMessage(text, ready_storage)
        assert joint_message._message == text
        assert joint_message.check_phrases == check_phrases
        assert joint_message.stop_phrase == stop_phrase

    def test_gluer_functionality(self, ready_storage):
        expect_msg = "Hello there!That's a FoobarBye, it is the last message."
        assert ready_storage.get_joint()._message == expect_msg

    def test_gluer_bad_time(self, check_phrases, stop_phrase):
        kwargs = dict(
            check_phrases=check_phrases,
            stop_phrase=stop_phrase,
            time_gap=1.5
        )
        t = int(time.time())

        r_storage = MessageStorage(**kwargs)
        r_storage.append(
            text='Hello there!', chat_id='11',
            time=t
        )
        r_storage.append(
            text='Unwanted string from different user',
            chat_id='42',
            time=t + 1)
        r_storage.append(
            text="That's a Foobar",
            chat_id='11',
            time=t + 2)
        r_storage.append(
            text='Bye, it is the last message.',
            chat_id='11',
            time=t + 4)

        joint_message = r_storage.get_joint()
        assert joint_message._message == 'Bye, it is the last message.'
        assert joint_message.valid is False

    def test_joint_message_validation(self, ready_storage):
        expect_text = "Hello there!That's a FoobarBye, it is the last message."
        joint_message = ready_storage.get_joint()
        assert joint_message.valid
        assert joint_message.text
        assert joint_message.text == expect_text

    def test_joint_message_bad_validation(self, ready_storage):
        ready_storage.append(
            text='No stop word in last message! An error!',
            chat_id='11')
        joint_message = ready_storage.get_joint()
        assert not joint_message.valid
        assert not joint_message.text

    def test_validation_without_proper_params(self,
                                              check_phrases,
                                              stop_phrase):
        storage = MessageStorage(
            check_phrases=check_phrases,
            stop_phrase=stop_phrase
        )
        assert not storage.get_joint().valid

        # not valid because no 'Bye' stop_phrase and no 'Foobar'
        storage.append('Hello', chat_id='123')
        assert not storage.get_joint().valid

        # not valid because no 'Foobar' string
        storage.append('Bye', chat_id='123')
        assert not storage.get_joint().valid

    def test__eq__method_in_joint_message_object(self, ready_storage):
        text = "Hello there!That's a FoobarBye, it is the last message."
        joint_message = ready_storage.get_joint()
        assert joint_message == text
        another_storage = MessageStorage()
        another_joint_message = JointMessage(text, another_storage)
        assert joint_message == another_joint_message

    def test_good_single_message(self, check_phrases, stop_phrase):
        storage = MessageStorage(
            check_phrases=check_phrases,
            stop_phrase=stop_phrase
        )
        text = "Hello there!That's a FoobarBye, it is the last message."
        storage.append(text, chat_id='567')

        assert storage._last().text == text
        assert not storage.get_joint()._flag
        assert storage.get_joint()._message == text
        assert storage.get_joint().valid
        assert storage.get_joint().text == text

        storage.append(text, chat_id='567', time=time.time() + 2)
        assert storage.get_joint().valid
        assert len(storage.get_joint()) == len(text)
        assert storage.get_joint().text == text

    def test_drop_storage(self, ready_storage):
        ready_storage.drop()
        assert len(ready_storage) == 1

    def test_log_constructor(self):
        log_as_list = [
            'Hello',
            'ThisIsLogMessage1',
            'ThisIsLogMessage2',
            ['ThisIsNestedLogMessage'],
            'ThisIsLogMessage3',
            ['Nested1', 'Nested2', 'Nested3']
        ]
        log_as_single_string = LogConstructor.join_log_message(log_as_list)
        expecting = '\n'.join(
            (
                'Hello',
                'ThisIsLogMessage1',
                'ThisIsLogMessage2',
                'ThisIsNestedLogMessage',
                'ThisIsLogMessage3',
                'Nested1', 'Nested2', 'Nested3'
            )
        ) + '\n'
        assert log_as_single_string == expecting
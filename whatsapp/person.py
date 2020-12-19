"""This module is used to contain info about a person.
"""

import typing


class PersonDict(typing.TypedDict):
    """A whatsapp.person.PersonDict dict

    Keys:
        this_person (bool): if True, the person is the client.
        person (str): the person that sent the message. Only works with text messages, and only works in group chats.
    """
    this_person: bool
    person: str

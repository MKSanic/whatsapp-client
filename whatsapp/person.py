"""This module is used to contain info about a person.
"""

import typing


class PersonDict(typing.TypedDict):
    """A whatsapp.person.PersonDict dict

    Keys:
        this_person (bool): if True, the person is the client.
    """
    this_person: bool

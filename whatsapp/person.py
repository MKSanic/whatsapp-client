"""This module is used to contain info about a person.
"""

import typing


class PersonDict(typing.TypedDict):
    """Person dict

    Keys:
        this_person (bool): if True, the person is the client.
    """
    this_person: bool

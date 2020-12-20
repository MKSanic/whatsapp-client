"""This module contains the exceptions for the whatsapp package.
"""


class FileTooBigError(Exception):
    """Raises when the given file is too big.
    """

    def __init__(self, size):
        self.message = f"The file is over 64MB (file is {size} bytes)"
        super().__init__(self.message)


class UnknownFileTypeError(Exception):
    """Raises when the given filetype is unknown.
    """

    def __init__(self):
        self.message = "There was given an unknown file type"
        super().__init__(self.message)


class CommandNotFoundError(Exception):
    """Raises when the given command couldn't been found.
    """

    def __init__(self):
        self.message = "The specified command couldn't be found"
        super().__init__(self.message)


class UnknownChatError(Exception):
    """Raises when the given chat is unknown.
    """

    def __init__(self, chat: str):
        self.message = f"Couldn't find chat {chat}"
        super().__init__(self.message)


class ClientNotStartedError(Exception):
    """Raises when the client hasn't been started yet.
    """

    def __init__(self):
        self.message = "The client isn't started yet"
        super().__init__(self.message)


class NotAPictureMessageError(Exception):
    """Raises when the message is not a picture message.
    """

    def __init__(self):
        self.message = "The message isn't a picture"
        super().__init__(self.message)


class InvalidPrefixError(Exception):
    """Raises when the given prefix is invalid.
    """

    def __init__(self):
        self.message = "The command prefix is invalid."
        super().__init__(self.message)


class CantFindMessageError(Exception):
    """Raises when the client can't find any messages.
    """

    def __init__(self):
        self.message = "Couldn't find any message in the chat."
        super().__init__(self.message)


class CantSetReplyError(Exception):
    """Raises when the client can't set a reply on a message.
    """

    def __init__(self):
        self.message = "Selenium couldn't find the reply button."
        super().__init__(self.message)


class CantRemoveMessageError(Exception):
    """Raises when the client can't remove a message.

    Args:
        owns_message (bool): default True, if False gives a  different error message.
    """

    def __init__(self, owns_message: bool = True):
        self.message = "Selenium couldn't find the remove message button."
        if not owns_message:
            self.message = "This message can't be removed because it isn't sent by me."
        super().__init__(self.message)


class UnableToSetGroupNameError(Exception):
    """Raises when the client is unable to set a group.
    """
    def __init__(self):
        self.message = "Unable to set the group name. Perhaps the client doesn't have permission to set it?"
        super().__init__(self.message)

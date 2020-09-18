class Message(object):
    """
    A Message object.\n
    This object has 2 variables: sender and contents\n
    sender will return a person object
    contents will return the message text
    """
    def __init__(self, sender, contents):
        self.sender = sender
        self.contents = contents
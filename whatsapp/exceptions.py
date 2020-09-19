class FileTooBigError(Exception):
    def __init__(self, size, message = None):
        if message is None:
            self.message = "The file is over 64MB (file is %s bytes)" % size
        else:
            self.message = message
        
        super().__init__(self.message)

class UnknownFileTypeError(Exception):
    def __init__(self, message = None):
        if message is None:
            self.message = "There was given an unknown file type to the send_file function"
        else:
            self.message = message
        
        super().__init__(self.message)

class CommandNotFoundError(Exception):
    def __init__(self, message = None):
        if message is None:
            self.message = "The specified command couldn't be found"
        else:
            self.message = message
        
        super().__init__(self.message)

class UnknownChatError(Exception):
    def __init__(self, chat, message = None):
        if message is None:
            self.message = "Couldn't find chat %s" % chat
        else:
            self.message = message
        
        super().__init__(self.message)
    
class ClientNotStartedError(Exception):
    def __init__(self):
        self.message = "The client isn't started yet"
        super().__init__(self.message)
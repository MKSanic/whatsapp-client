class Self(object):
    """
    Self
    """
    def __init__(self):
        pass

class Other(object):
    """
    Not self
    """
    def __init__(self):
        pass

class Person(object):
    """
    Person object
    Has 1 object: person, will return a Self or Other object
    """
    def __init__(self, person):
        self.person = person
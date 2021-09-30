"""

Base sender class

"""

import abc

class MessageSender(metaclass=abc.ABCMeta):
    """An abstract message sender for the state monitor."""

    # Methods, attributes and code common to all senders go here.

    @abc.abstractmethod
    def send(self, msg):
        pass
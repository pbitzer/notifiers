"""
Post slack notifications

"""

import logging
import urllib.parse
import urllib.request
from configparser import ConfigParser
from pathlib import Path

from notifiers.base import MessageSender

HTTP_STATUS_OK = 200  # This is the code returned from Slack when posting a message is OK.
BASE_URL = 'https://hooks.slack.com/services/'

class SlackSender(MessageSender):
    def __init__(self, key_file, channel=None, logger=None):
        """
        Handle sending messages in Slack.

        Parameters
        ----------
        key_file : str or pathlib.Path
            The path to the file that contains the Slack key for the
            workspace to send the message. This file should also define
            the channel to which the message should be posted. 
        channel : str
            The channel to send the message to. This should match to at least
            one key defined in `key_file`.
        logger : logging.Logger or False, optional
            If not False and message send fails, log it to the passed logger
            or the default logger, if not passed.

        """
        self.logger = logging.getLogger(__name__) if logger is None else logger

        slack_key_file = Path(key_file).expanduser()

        if not slack_key_file.exists():
            raise FileNotFoundError

        config = ConfigParser()
        config.read(slack_key_file)

        # Define the url, including the channel....
        slack_url = urllib.parse.urljoin(BASE_URL, config['channel'][channel])

        self.request = urllib.request.Request(url=str(slack_url),
                                              headers={'Content-type': 'application/json'},
                                              method='POST')

    def send(self, msg):
        """
        Send a Slack message.

        If the message sending fails and there is a logger associated with
        the class, log it. Otherwise, raise a `RuntimeWarning`.
        """

        self.request.data = f'{{"text": "{msg}"}}'.encode('utf-8')

        resp = urllib.request.urlopen(self.request)

        if resp.status != HTTP_STATUS_OK:
            warning_msg = f"Sending to slack failed. Message: {msg}"

            if self.logger:
                self.logger.warning(warning_msg)
            else:
                raise RuntimeWarning(warning_msg)

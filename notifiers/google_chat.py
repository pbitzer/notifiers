"""
Post Google Chat notifications

"""
import json
import logging
import urllib.parse
import urllib.request
from configparser import ConfigParser
from pathlib import Path

from notifiers.base import MessageSender

HTTP_STATUS_OK = 200  # This is the code returned from Slack when posting a message is OK.
BASE_URL = 'https://chat.googleapis.com/v1/spaces/'


class GoogleChatSender(MessageSender):
    def __init__(self, key_file, channel=None, logger=None):
        """
        Handle sending messages in Google Chat.

        Parameters
        ----------
        key_file : str or pathlib.Path
            The path to the file that contains the Google Chat webhook key for the
            space to send the message. This file should also define
            the channel to which the message should be posted. 
        channel : str
            The channel to send the message to. This should match to at least
            one key defined in `key_file`.
        logger : logging.Logger or False, optional
            If not False and message send fails, log it to the passed logger
            or the default logger, if not passed.

        """
        self.logger = logging.getLogger(__name__) if logger is None else logger

        _key_file = Path(key_file).expanduser()

        if not _key_file.exists():
            raise FileNotFoundError

        config = ConfigParser(interpolation=None)
        config.read(_key_file)

        # Define the url, including the channel....
        url = urllib.parse.urljoin(BASE_URL, config['channel'][channel])

        msg_hdr = {'Content-Type': 'application/json; charset=UTF-8'}

        self.request = urllib.request.Request(url=url,
                                              headers=msg_hdr,
                                              method='POST')

    def send(self, msg):
        """
        Send a Google Chat message.

        If the message sending fails and there is a logger associated with
        the class, log it. Otherwise, raise a `RuntimeWarning`.
        """
        send_msg = {'text': msg}

        self.request.data = json.dumps(send_msg).encode('utf-8')

        resp = urllib.request.urlopen(self.request)

        if resp.status != HTTP_STATUS_OK:
            warning_msg = f"Sending to Google Chat failed. Message: {msg}"

            if self.logger:
                self.logger.warning(warning_msg)
            else:
                raise RuntimeWarning(warning_msg)

import time
import configparser
import os
from slackclient import SlackClient
from app.Database import Database


class SlackCrawler(Database):
    slack_client = None

    def __init__(self):
        Database.__init__(self)
        self.slack_client = SlackClient(self.get_slack_token())

    @staticmethod
    def get_slack_response(callback, args=None):
        while True:
            if args is None:
                response = callback()
            else:
                response = callback(args)

            if response['ok'] is False and response['error'] is 'ratelimited':
                print('Hit rate limit, sleeping for 60 seconds')
                time.sleep(60)
            else:
                break

        return response

    @staticmethod
    def get_slack_token():
        settings = configparser.ConfigParser()
        settings.read('settings.cfg')

        return os.environ["SLACK_TOKEN"] if None else settings.get('slack', 'token')

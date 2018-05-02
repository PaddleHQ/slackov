from app.Channels import Channels
from crawler.SlackCrawler import SlackCrawler


class ChannelCrawler(SlackCrawler):
    channels = None

    def __init__(self):
        SlackCrawler.__init__(self)
        self.channels = Channels()

    def run(self):
        channel_list = self.get_slack_response(
            self.get_channel_list
        )
        for channel in channel_list['channels']:
            if not Channels().exists_by_id(channel['id']):
                print ("Inserting '%s'" % (channel['name']))
                self.channels.create(channel)
            else:
                print ("Skipping '%s'" % (channel['name']))

    def get_channel_list(self):
        return self.slack_client.api_call(
            "channels.list",
        )

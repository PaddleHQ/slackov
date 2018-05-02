import json

from app.Channels import Channels
from app.Sentences import Sentences
from crawler.SlackCrawler import SlackCrawler


class ChannelHistoryCrawler(SlackCrawler):
    next_cursor = ''

    def run(self):
        channels = Channels().get_all_channels()
        for channel in channels:
            self.next_cursor = ''
            print('Crawling channel %s' % channel.name)

            while True:
                channel_history = self.get_slack_response(
                    self.get_conversation_history,
                    {'channel_id': channel.id, 'next_cursor': self.next_cursor}
                )

                if channel_history['ok'] is False:
                    print(channel_history['error'])
                    break

                has_scraped_newest_messages = self.scape_messages(channel.id, channel_history['messages'])
                if not channel_history['has_more'] or has_scraped_newest_messages:

                    for message in channel_history['messages']:
                        ts = message['ts'].encode('utf-8')

                        if 'replies' in message:
                            self.get_thread_messages(channel.id, ts)

                    break

                self.next_cursor = channel_history['response_metadata']['next_cursor']

    def scape_messages(self, channel_id, messages):
        amount_of_messages = len(messages)
        for i, message in enumerate(messages):
            ts = message['ts'].encode('utf-8')

            is_slackov = False
            if 'bot_id' in message:
                is_slackov = message['bot_id'] == 'B9JHZ0Q07'
                message['user'] = 'C9GRYGZK2'

            if 'user' in message and ('subtype' not in message or is_slackov):
                employee_id = message['user'].encode('utf-8')
                channel_id = channel_id.encode('utf-8')
                text = message['text'].encode('utf-8').strip()
                ts_exists = Sentences().ts_exists(ts)
                if text.startswith('/slackov'):
                    continue

                reactions = None
                if 'reactions' in message:
                    reactions = json.dumps(message['reactions'])

                if text:
                    self.create_sentences(text, employee_id, channel_id, ts, reactions)
                    print "[%s][%s] %s: %s" % (ts, channel_id, employee_id, text)

                if 'attachments' in message and 'image_url' in message['attachments']:
                    self.create_sentences(message['attachments']['image_url'], employee_id, channel_id, ts, reactions)
                    print "[%s][%s] %s: %s" % (ts, channel_id, employee_id, message['attachments']['image_url'])

                if 'replies' in message:
                    self.get_thread_messages(channel_id, ts)

                if i == (amount_of_messages-1) and ts_exists:
                    print('All caught up!')
                    return True

            else:
                print('[%s][%s] Skipping: %s' % (ts, channel_id, self.get_bad_message_error_message(message)))

        return False

    @staticmethod
    def create_sentences(text, employee_id, channel_id, ts, reactions=None, parent_ts=None):
        if Sentences().ts_exists(ts) is False:
            Sentences().create(text, employee_id, channel_id, ts, reactions, parent_ts)
        else:
            print('[%s][%s] Skipping: %s' % (ts, channel_id, 'Sentence already exists'))

    def get_thread_messages(self, channel_id, parent_ts):
        next_thread_cursor = ''
        while True:
            conversation = self.get_slack_response(
                self.get_conversation_relies,
                {'channel_id': channel_id, 'ts': parent_ts, 'next_cursor': next_thread_cursor}
            )
            if 'messages' in conversation:
                self.scape_thread_messages(channel_id, conversation['messages'], parent_ts)
            else:
                break

            if not conversation['has_more']:
                break

            next_thread_cursor = conversation['response_metadata']['next_cursor']

    def scape_thread_messages(self, channel_id, replies, parent_ts):
        replies.pop(0)

        for message in replies:
            ts = message['ts'].encode('utf-8')
            if 'user' in message and 'subtype' not in message:
                employee_id = message['user'].encode('utf-8')
                text = message['text'].encode('utf-8').strip()
                channel_id = channel_id.encode('utf-8')
                reactions = None

                if 'reactions' in message:
                    reactions = json.dumps(message['reactions'])

                self.create_sentences(text, employee_id, channel_id, ts, reactions, parent_ts)
                print "[%s][%s] %s: %s" % (ts, channel_id, employee_id, text)
            else:
                print('[%s][%s] Skipping: %s' % (ts, channel_id, self.get_bad_message_error_message(message)))

    def get_conversation_history(self, args):
        return self.slack_client.api_call(
            "conversations.history",
            channel=args['channel_id'],
            cursor=args['next_cursor'],
        )

    def get_conversation_relies(self, args):
        return self.slack_client.api_call(
            "conversations.replies",
            channel=args['channel_id'],
            ts=args['ts'],
            cursor=args['next_cursor'],
        )

    @staticmethod
    def get_bad_message_error_message(message):
        if 'subtype' in message:
            return 'Message by bot/ app'
        elif 'user' not in message:
            return 'No user was set'

        return 'Unknown reason'

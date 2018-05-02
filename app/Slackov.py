import markovify
import operator

from app.Employees import Employees
from app.Sentences import Sentences


class Slackov:
    sentences = None

    def __init__(self):
        self.sentences = Sentences()

    def get_user_generated_sentence(self, slack_handle):
        sentences = self.sentences.get_user_sentences(slack_handle)
        text = self.attempt_to_generate_text(sentences)
        full_name = Employees().get_full_name(slack_handle)

        return self.build_response(full_name, text)

    def get_user_generated_sentence_from_channel(self, slack_handle, channel):
        sentences = self.sentences.get_user_sentences_in_channel(slack_handle, channel)
        text = self.attempt_to_generate_text(sentences)
        full_name = Employees().get_full_name(slack_handle)

        return self.build_response(full_name, text)

    def get_user_generated_sentence_with_beginning(self, slack_handle, beginning):
        sentences = self.sentences.get_user_sentences(slack_handle)
        flat_sentences = reduce(operator.add, sentences)
        full_name = Employees().get_full_name(slack_handle)
        text_model = markovify.Text(flat_sentences)
        text = text_model.make_sentence_with_start(beginning.encode('utf8'))
        if text is None:
            raise Exception("Insufficient data to generate sentence")

        return self.build_response(full_name, text)

    def get_random_user_generated_sentence(self):
        handle = Employees().get_random_employee()

        return self.get_user_generated_sentence(handle)

    def get_channel_generated_sentences(self, name):
        sentences = self.sentences.get_channel_sentences(name)
        text = self.attempt_to_generate_text(sentences)

        return self.build_response(name, text)

    def get_multiple_users_generated_sentences(self, slack_handles):
        from collections import OrderedDict
        slack_handles = list(OrderedDict.fromkeys(slack_handles))
        sentences = self.sentences.get_multiple_users_sentences(slack_handles)
        handles = ",".join(slack_handles)
        text = self.attempt_to_generate_text(sentences)

        return self.build_response(handles, text)

    @staticmethod
    def build_response(name, sentences):
        return {'name': name, 'sentences': sentences}

    @staticmethod
    def attempt_to_generate_text(sentences):
        flat_sentences = reduce(operator.add, sentences)
        text = None
        for i in range(5):
            text_model = markovify.Text(flat_sentences)
            text = text_model.make_sentence()
            if text is not None:
                break

        if text is None:
            raise Exception("Insufficient data to generate sentence")

        return text

from flask import request, jsonify
from flask_cors import cross_origin

from app import app
from app.Slackov import Slackov

slackov = Slackov()


@app.route("/")
def hello():
    return "Welcome to slackov"


@app.route("/generate/user", methods=['POST'])
@cross_origin()
def generate_user():
    params = get_request_params(request.form['text'])

    try:
        if 'text' in request.form and request.form['text'] and params is not False:
            handle = params['handle']

            from app.Employees import Employees
            if not Employees().exists(handle):
                return build_ephemeral_response('Handle does not exist')

            if 'channel' in params:
                sentences = slackov.get_user_generated_sentence_from_channel(params['handle'], params['channel'])
            elif 'beginning' in params:
                sentences = slackov.get_user_generated_sentence_with_beginning(params['handle'], params['beginning'])
            else:
                sentences = slackov.get_user_generated_sentence(params['handle'])
        else:
            sentences = slackov.get_random_user_generated_sentence()
    except:
        return build_ephemeral_response('Insufficient data to generate sentence, please try again')

    return build_success_response(sentences)


@app.route("/generate/channel", methods=['POST'])
@cross_origin()
def generate_channel():
    if request.form['text']:
        name = format_channel(request.form['text'])
        from app.Channels import Channels

        if not Channels().exists(name):
            return build_ephemeral_response('Channel does not exist')

        try:
            sentences = slackov.get_channel_generated_sentences(name)
        except:
            return build_ephemeral_response('Insufficient data to generate sentence, please try again')

        return build_success_response(sentences)
    else:
        return build_ephemeral_response('Channel name not set')


@app.route("/generate/combination", methods=['POST'])
@cross_origin()
def generate_combination():
    if request.form['text']:
        names = request.form['text'].split(' ')
        names = [s.strip('@') for s in names]

        try:
            sentences = slackov.get_multiple_users_generated_sentences(names)
        except:
            return build_ephemeral_response('Insufficient data to generate sentence, please try again')

        return build_success_response(sentences)
    else:
        return build_ephemeral_response('Channel name not set')


@app.route("/employee/toggle", methods=['POST'])
@cross_origin()
def toggle_user():
    from app.Employees import Employees

    if request.form['text'] == 'enable':
        Employees().toggle(request.form['user_id'], True)
        return build_ephemeral_response('You have enabled your account to work with Slackov')
    elif request.form['text'] == 'disable':
        Employees().toggle(request.form['user_id'], False)
        return build_ephemeral_response('You have disabled your account to work with Slackov')
    else:
        return build_ephemeral_response("Please entry 'enable' or 'disable")


def build_success_response(sentence):
    from app.Sentences import Sentences
    text = Sentences().format_all_ats(sentence['sentences'])
    response = {
        'response_type': 'in_channel',
        'text': "*%s*: %s" % (sentence['name'], text)
    }

    return jsonify(response)


def build_ephemeral_response(sentences):
    response = {
        'response_type': 'ephemeral',
        'text': sentences
    }

    return jsonify(response)


def format_handle(handle):
    return handle.replace('@', '').strip()


def format_channel(name):
    return name.replace('#', '').strip()


def get_request_params(request):
    raw_params = request.split(' ')
    raw_params = filter(None, raw_params)
    if len(raw_params) == 0:
        return False

    return_array = {'handle': format_handle(raw_params[0])}

    if len(raw_params) > 1:
        text = format_channel(raw_params[1])
        from app.Channels import Channels
        if Channels().exists(text):
            return_array['channel'] = text
        else:
            return_array['beginning'] = text

    return return_array

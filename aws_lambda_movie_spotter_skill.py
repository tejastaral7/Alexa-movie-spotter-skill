from __future__ import print_function
from bs4 import BeautifulSoup
import requests


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me a movie name to get info about it by saying, " \
                    "get info about movie movie name"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "You can ask me movie info by saying, " \
                        "get info about movie movie name"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_movie_name_attributes(movie_name):
    return {"Movie Name": movie_name}

def get_theatres(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'MovieName' in intent['slots']:
        movie_name = intent['slots']['MovieName']['value']
        session_attributes = create_movie_name_attributes(movie_name)
        url = "https://www.google.com.tr/search?q={}".format("showtimes for " + movie_name)
        data = requests.get(url)
        soup = BeautifulSoup(data.text)
        theaters = soup.find_all(class_="lr_c_fcb lr-s-stor")
        
        speech_output = "theatre name"
        reprompt_text = "for which movie do you wanna find theatre"

    else:
        speech_output = ""
        reprompt_text = ""


    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_movie_info(intent, session):
   
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'MovieName' in intent['slots']:
        movie_name = intent['slots']['MovieName']['value']
        session_attributes = create_movie_name_attributes(movie_name)
        url = "https://www.google.com.tr/search?q={}".format(movie_name + " imdb")
        r  = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, 'html.parser')
        #scr = soup.find_all("div",{"class":"TbwUpd"})
        scr = soup.find_all(class_="r")
        q = scr[0].a.get("href").split("=")
        link = q[1].split("&") 
        raw  = requests.get(link[0])
        soup = BeautifulSoup(raw.text)
        imdb_rating = soup.find_all(class_="ratingValue")
        imdb = imdb_rating[0].strong.span.get_text()
        print(link[0])
        print(imdb)
        category = soup.find_all(class_="subtext")
        #print(category[0])
        categories = category[0].find_all("a")
        genres = []
        for x in categories[:-1]:
            genres.append(x.text)
        #print(genres)
        gen = genres[0]
        for x in genres[1:]:
            gen = gen + "," + x
        print(gen)
        summary = soup.find(class_="summary_text").text
        print(summary)
        #print(scr)
        speech_output = "Info about movie " + movie_name + "." + \
                         " imdb rating: " + imdb + " . " + \
                         "Category: " + gen + " " +  \
                         "Summary: " + summary 
        reprompt_text = "You can ask me movie info by saying, " \
                        "get info about movie movie name"
    else:
        speech_output = "About which movie do you want to find information?"
        reprompt_text = "tell me a movie name"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MovieInfoIntent":
        return get_movie_info(intent, session)
    elif intent_name == "TheatreFinderIntent":
        return get_theatres(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
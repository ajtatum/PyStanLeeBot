import os, sys, json, logging, jsonpickle, urllib.request
from flask import Flask, request, Response, jsonify #import main Flask class and request object
from logging.handlers import RotatingFileHandler
from slackclient import SlackClient
from Models.SlackRequest import SlackRequest
from Models.SlackQueryResponse import SlackQueryResponse

DEBUG = os.getenv('DEGUG', default=True)
TEST_AUTH_KEY = os.getenv('TEST_AUTH_KEY')
SLACK_STANLEE_API_TOKEN = os.getenv('SLACK_STANLEE_API_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MARVEL_GOOGLE_CSE_ID = os.getenv('MARVEL_GOOGLE_CSE_ID')
DC_COMICS_GOOGLE_CSE_ID = os.getenv('DC_COMICS_GOOGLE_CSE_ID')

slack_client = SlackClient(SLACK_STANLEE_API_TOKEN)

app = Flask(__name__) #create the Flask app

@app.route('/', methods=['GET'])
def home():
    return "<h1>StanLeeBot</h1>"

@app.route('/slack-marvel', methods=['POST'])
def SlackMarvel():

    sr = SlackRequest()
    sr.ChannelName = request.form.get('channel_name')
    sr.ChannelId = request.form.get('channel_id')
    sr.UserName = request.form.get('user_name')
    sr.UserId = request.form.get('user_id')
    sr.Text = urllib.parse.quote(request.form.get('text'))

    slack_client.api_call(
        "chat.postMessage",
        channel=sr.ChannelId,
        attachments=GetGoogleSearchSlackResponseJson(sr, MARVEL_GOOGLE_CSE_ID),
        unfurl_links=True,
        unfurl_media=True,
        as_user=True
    )

    return Response(), 200

@app.route('/slack-dc', methods=['POST'])
def SlackDCComics():

    sr = SlackRequest()
    sr.ChannelName = request.form.get('channel_name')
    sr.ChannelId = request.form.get('channel_id')
    sr.UserName = request.form.get('user_name')
    sr.UserId = request.form.get('user_id')
    sr.Text = urllib.parse.quote(request.form.get('text'))

    slack_client.api_call(
        "chat.postMessage",
        channel=sr.ChannelId,
        attachments=GetGoogleSearchSlackResponseJson(sr, DC_COMICS_GOOGLE_CSE_ID),
        unfurl_links=True,
        unfurl_media=True
    )

    return Response(), 200

@app.route('/test-marvel', methods=['GET'])
def TestMarvel():
    authKey = request.args.get('auth_key')
    if TEST_AUTH_KEY == authKey:
        sr = SlackRequest()
        sr.ChannelName = request.args.get('channel_name')
        sr.ChannelId = request.args.get('channel_id')
        sr.UserName = request.args.get('user_name')
        sr.UserId = request.args.get('user_id')
        sr.Text = urllib.parse.quote(request.args.get('text'))

        resp = Response(response=jsonpickle.encode(GetGoogleSearchSlackResponseJson(sr, MARVEL_GOOGLE_CSE_ID)),
                        status=200,
                        mimetype="application/json")

        return resp
    else:
        return Response(), 403

@app.route('/test-dc', methods=['GET'])
def TestDCComics():
    authKey = request.args.get('auth_key')
    if TEST_AUTH_KEY == authKey:
        sr = SlackRequest()
        sr.ChannelName = request.args.get('channel_name')
        sr.ChannelId = request.args.get('channel_id')
        sr.UserName = request.args.get('user_name')
        sr.UserId = request.args.get('user_id')
        sr.Text = urllib.parse.quote(request.args.get('text'))

        resp = Response(response=jsonpickle.encode(GetGoogleSearchSlackResponseJson(sr, DC_COMICS_GOOGLE_CSE_ID)),
                        status=200,
                        mimetype="application/json")

        return resp
    else:
        return Response(), 403

def GetGoogleSearchSlackResponseJson(sr, cse):
    url = "https://www.googleapis.com/customsearch/v1?cx={}&key={}&q={}".format(cse, GOOGLE_API_KEY, sr.Text)

    app.logger.debug(jsonpickle.encode(sr))
    app.logger.debug("Url Requested: {}".format(url))

    res = urllib.request.urlopen(url)
    res_body = res.read()

    j = json.loads(res_body.decode("utf-8"))
    
    sqr = SlackQueryResponse()
    sqr.FromJson(j)
    return sqr.ToJson()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
    handler = RotatingFileHandler('logs/StanLeeBotApp.log', maxBytes=10000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    #app.logger.addHandler(handler)
    app.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    app.logger.setLevel(logging.DEBUG)

    app.run(debug=DEBUG) #run app in debug mode on port 5000
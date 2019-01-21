import os, sys, json, logging, jsonpickle, urllib.request
from flask import Flask, request, Response, jsonify #import main Flask class and request object
from logging.handlers import RotatingFileHandler
from slackclient import SlackClient
from Models.SlackRequest import SlackRequest
from Models.SlackQueryResponse import SlackQueryResponse

DEBUG = os.getenv('DEGUG', default=True)
SLACK_STANLEE_API_TOKEN = os.getenv('SLACK_STANLEE_API_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

slack_client = SlackClient(SLACK_STANLEE_API_TOKEN)

app = Flask(__name__) #create the Flask app

@app.route('/', methods=['GET'])
def home():
    return "<h1>StanLeeBot</h1>"

@app.route('/slack', methods=['POST'])
def slack():

    sr = SlackRequest()
    sr.ChannelName = request.form.get('channel_name')
    sr.ChannelId = request.form.get('channel_id')
    sr.UserName = request.form.get('user_name')
    sr.UserId = request.form.get('user_id')
    sr.Text = urllib.parse.quote(request.form.get('text'))

    url = "https://www.googleapis.com/customsearch/v1?cx={}&key={}&q={}".format(GOOGLE_CSE_ID, GOOGLE_API_KEY, sr.Text)

    app.logger.debug("Url Requested: {}".format(url))

    res = urllib.request.urlopen(url)
    res_body = res.read()

    j = json.loads(res_body.decode("utf-8"))
    
    sqr = SlackQueryResponse()
    sqr.FromJson(j)

    slack_client.api_call(
        "chat.postMessage",
        channel=sr.ChannelId,
        attachments=sqr.ToJson(),
        unfurl_links=True,
        unfurl_media=True
    )

    return Response(), 200

@app.route('/test', methods=['GET'])
def test():

    sr = SlackRequest()
    sr.ChannelName = request.args.get('channel_name')
    sr.ChannelId = request.args.get('channel_id')
    sr.UserName = request.args.get('user_name')
    sr.UserId = request.args.get('user_id')
    sr.Text = urllib.parse.quote(request.args.get('text'))

    url = "https://www.googleapis.com/customsearch/v1?cx={}&key={}&q={}".format(GOOGLE_CSE_ID, GOOGLE_API_KEY, sr.Text)

    app.logger.debug("Url Requested: {}".format(url))

    res = urllib.request.urlopen(url)
    res_body = res.read()

    j = json.loads(res_body.decode("utf-8"))

    sqr = SlackQueryResponse()
    sqr.FromJson(j)

    resp = Response(response=jsonpickle.encode(sqr.ToJson()),
                    status=200,
                    mimetype="application/json")

    return resp

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    formatter = logging.Formatter( "%(asctime)s | %(pathname)s:%(lineno)d | %(funcName)s | %(levelname)s | %(message)s ")
    handler = RotatingFileHandler('logs/StanLeeBotApp.log', maxBytes=10000, backupCount=5)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    app.logger.setLevel(logging.DEBUG)

    app.run(debug=DEBUG) #run app in debug mode on port 5000
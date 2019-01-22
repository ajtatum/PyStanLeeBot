import os, sys, json, logging, jsonpickle, urllib.request, time, re
from flask import Flask, request, Response, jsonify #import main Flask class and request object
from logging.handlers import RotatingFileHandler
from slackclient import SlackClient
from Models.SlackRequest import SlackRequest
from Models.SlackQueryResponse import SlackQueryResponse

DEBUG = os.getenv('DEGUG', default=True)
SLACK_STANLEE_API_TOKEN = os.getenv('SLACK_STANLEE_API_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "giphy"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = SlackClient(SLACK_STANLEE_API_TOKEN)
starterbot_id = None

app = Flask(__name__) #create the Flask app

@app.route('/', methods=['GET'])
def home():
    return "<h1>StanLeeBot</h1>"

@app.route('/slackrtm', methods=['POST'])
def slackrtm():
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

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
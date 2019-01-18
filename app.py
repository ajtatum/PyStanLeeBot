from flask import Flask, request, Response, jsonify #import main Flask class and request object
import urllib.request
import os, sys, json, jsonpickle
from slackclient import SlackClient
from Models.SlackRequest import SlackRequest

SLACK_STANLEE_API_TOKEN = os.getenv('SLACK_STANLEE_API_TOKEN')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID=os.getenv('GOOGLE_CSE_ID')

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

    print(url)

    res = urllib.request.urlopen(url)
    res_body = res.read()

    j = json.loads(res_body.decode("utf-8"))

    slack_client.api_call(
        "chat.postMessage",
        channel=sr.ChannelId,
        text="{}\n{}".format(j['items'][0]['title'],j['items'][0]['link']),
        unfurl_links="true"
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

    print(url)

    res = urllib.request.urlopen(url)
    res_body = res.read()

    j = json.loads(res_body.decode("utf-8"))

    return j['items'][0]['title']

if __name__ == '__main__':
    app.run(debug=True) #run app in debug mode on port 5000
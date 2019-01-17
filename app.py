from flask import Flask, request, Response, jsonify #import main Flask class and request object
import urllib.request
import os, sys, json, jsonpickle
from Models.SlackRequest import SlackRequest

SLACK_STANLEE_API_TOKEN = os.getenv('SLACK_STANLEE_API_TOKEN')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID=os.getenv('GOOGLE_CSE_ID')

app = Flask(__name__) #create the Flask app

@app.route('/', methods=['GET'])
def home():
    return "<h1>StanLeeBot</h1>"

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
    app.run(debug=os.getenv('Debug', default=True)) #run app in debug mode on port 5000
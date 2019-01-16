from flask import Flask, request, Response, jsonify #import main Flask class and request object
import os, sys, json

app = Flask(__name__) #create the Flask app

@app.route('/', methods=['GET'])
def home():
    return "<h1>StanLeeBot</h1>"    

if __name__ == '__main__':
    app.run(debug=os.getenv('Debug', default=True)) #run app in debug mode on port 5000
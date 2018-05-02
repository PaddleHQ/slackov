from flask import Flask, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)

from app import api
app.config['CORS_HEADERS'] = 'Content-Type'

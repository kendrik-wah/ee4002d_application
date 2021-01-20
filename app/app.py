import floormat
from flask import Flask
import requests
import pymongo
from pymongo import MongoClient

app = Flask(__name__)
db = MongoClient('localhost', 27017)

"""
Acquire the blackboard database.
"""
mcu_database = db.microcontrollers
blackboard = db.blackboard


@app.route('/initialize')
def initialize():
    """
    TODO: Connection procedure:
        1) Ensure that microcontrollers can be contacted using HTTP or MQTT. But I think for now, I'll just use HTTP.
            a) Let the application contact the microcontroller.
            b) Receive the response obtained from the microcontroller.
        2) Ensure that databases can be contacted.
            a) Let the application contact the database.
                a.1) The floormat database.
                a.2) The blackboard(?)
            b) Receive a response (if applicable).
    :return:
    """



    requests.post("")
    return


@app.route('/')
def index():
    """
    TODO: Render floormat:
        1) Create a visualization for the floormat (start from a tile).
        2) Create a visualization for the activation/ deactivation of a tile.

    :return:
    """
    return 'Hello world!'


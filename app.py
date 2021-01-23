import floormat
import requests
import pymongo
import demo

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect
from pymongo import MongoClient

async_mode = None
app = Flask(__name__)
socket = SocketIO(app, async_mode=async_mode)
db = MongoClient('localhost', 27017)

"""
Acquire the blackboard database.
"""
mcu_database = db.microcontrollers
blackboard = db.blackboard


rotate_idx = 0


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

    heatmaps = demo.demo_processFloormatData()
    for heatmap in heatmaps:
        render_template('heatmap.html',
                        sync_mode=socket.async_mode,
                        heatmap=heatmap)


if __name__ == "__main__":
    socket.run(app, debug=True)
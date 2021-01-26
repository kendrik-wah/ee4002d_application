import floormat
import requests
import pymongo
import demo

from random import random
from threading import Thread, Event
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect
from pymongo import MongoClient

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)
db = MongoClient('localhost', 27017)

"""
Acquire the blackboard database.
"""
mcu_database = db.microcontrollers
blackboard = db.blackboard


# Random Number Generator Thread
thread = Thread()
thread_stop_event = Event()


class RandomThread(Thread):
    def __init__(self):
        self.delay = 0.5
        super(RandomThread, self).__init__()


    def heatMap(self):

        i = 0
        heatmaps = demo.demo_processFloormatData()
        maxLen = len(heatmaps)-1

        while not thread_stop_event.isSet():

            heatmap = heatmaps[i]

            if i == maxLen:
                i = 0
            else:
                i += 1

            socketio.emit('newheatmap', {'heatmap': heatmap,
                                         'cols': len(heatmap),
                                         'rows': len(heatmap[0])},
                          namespace='/test')

            socketio.sleep(self.delay)

    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        # infinite loop of magical random numbers
        print("Making random numbers")
        while not thread_stop_event.isSet():
            number = round(random()*10, 3)
            print(number)
            socketio.emit('newnumber', {'number': number}, namespace='/test')
            socketio.sleep(self.delay)

    def run(self):
        self.heatMap()


@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': 'got it'})


# Python code to start Asynchronous Number Generation
@app.route('/')
def index():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('heatmap.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')
    # Start the random number generator thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()


if __name__ == "__main__":
    socketio.run(app, debug=True)
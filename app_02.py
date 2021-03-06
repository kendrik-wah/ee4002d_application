import floormat
import requests
import pymongo
import demo
import csv
import os

from random import random
from threading import Thread, Event
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, emit, disconnect
from pymongo import MongoClient
from bluepy.btle import Scanner
from floormat.floormat import Floormat
from interface.ble_scanner import ScanDelegate
from interface.ble_peripheral import blePeripheral

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

# Floormat Thread
thread = Thread()
thread_stop_event = Event()

FLOORMAT_MAC = "ac:67:b2:f9:25:de"

class RandomThread(Thread):
    def __init__(self):
        self.delay = 0.5
        super(RandomThread, self).__init__()

    def heatMapCompletePipeline(self):

        weightMap = demo.demo_acquireSensorClassMapping()
        bleScanner = Scanner().withDelegate(ScanDelegate())
        devices = bleScanner.scan()

        floormat = Floormat(row=4, column=4)
        dims = floormat.get_dimensions()
        print("dims: {}".format(dims))
        c = dims[1]
        r = dims[0]
        
        for dev in devices:
            print(dev.addr, dev.getScanData())
            if dev.addr == FLOORMAT_MAC:
                try:
                    global peripheral
                    peripheral = blePeripheral(dev.addr)
                except Exception as e:
                    raise(e)
					
                services = peripheral.acquireService()
                characteristics = peripheral.getCharacteristics()
                peripheral.enableNotify(uuid="e514ae34-a8c5-11ea-bb37-0242ac130002")
                refreshFlag = False
                floormatData = []

                while not thread_stop_event.isSet():

                    if peripheral.peripheral.waitForNotifications(3.0):
                        datetime = peripheral.getDateTime()
                        data = peripheral.getData()
                        # print("data: {}".format(data))
                        
                        if data == "\\" and not refreshFlag:
                            refreshFlag = True
                        elif refreshFlag and data == '/':
                            refreshFlag = False
                            floormatData = []
                        elif refreshFlag:
                            floormatData.append(data)

                        tiles = set()
                        for j in range(len(data)):
                            tiles.add(((len(floormatData)-1, j), data[j]))
                            
                        for i in range(r):
                            for j in range(c):
                                floormat.activate_tile(i, j)

                        floormat.update_tile_state(tiles)
                        statemat = floormat.get_floormat_states(key=1)
                        toSaveData = ""
                        
                        for row in statemat:
                            toSaveData += ','.join(list(map(lambda x: str(x), row)))
                        
                        if not os.path.isfile('./data.csv'):
                            with open("data.csv", 'w+', newline="") as inputFile:
                            	smWriter = csv.writer(inputFile)
                            	smWriter.writerow([toSaveData])
                        else:
                            with open("data.csv", 'a', newline="") as inputFile:
                            	smWriter = csv.writer(inputFile)
                            	smWriter.writerow([toSaveData])
                            
                        # print("statemat: {}".format(statemat))

                        for i in range(r):
                            for j in range(c):
                                for key, val in weightMap.items():
                                    if statemat[i][j] <= 0:
                                        statemat[i][j] = val["colour"]
                                        break

                                    elif val["min"] <= statemat[i][j] <= val["max"]:
                                        statemat[i][j] = val["colour"]
                                        break
                        
                        socketio.emit('newheatmap', {'heatmap': statemat,
                                                     'cols': c,
                                                     'rows': r})
                        socketio.sleep(self.delay)

                    else:
                        print("Nothing new has arrived, connection status: {}".format(peripheral.getState()))
                        pass

    def run(self):
        self.heatMapCompletePipeline()


@socketio.on('tarecal', namespace='/tarecal')
def tareCalHandler(flag, methods=['GET', 'POST']):
    print("flag received: {}".format(flag))
    tareCal(flag)

def tareCal(flag, methods=['GET', 'POST']):
    print(flag)
    if flag == 1 or flag == 2:
        peripheral.writeData(uuid="809a3309-2e5c-4d68-acef-196222cf9886", data=bytes(str(flag)))


# Python code to start Asynchronous Number Generation
@app.route('/')
def index():
    # only by sending this page first will the client be connected to the socketio instance
    return render_template('heatmap.html')


@socketio.on('connect')
def connect():
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


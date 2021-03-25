import os
import sys
import datetime
import json
import floormat
import requests
import demo
import csv
import time
import bluepy.btle

from queue import Queue
from random import random
from threading import Thread, Event, Timer
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, emit, disconnect
from mongoclient import DatabaseClient
from bluepy.btle import Scanner
from floormat.floormat import Floormat
from interface.ble_scanner import ScanDelegate
from interface.ble_peripheral import blePeripheral
from algorithms import getSnapshot, createHeatMap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

EMIT = 'E'
POST = 'P'
WRITE = 'W'

# Define endpoints
FLOORMAT_MAC = "ac:67:b2:f9:25:de"
NOTIFY_UUID = "e514ae34-a8c5-11ea-bb37-0242ac130002"
# APP_ENDPOINT = 'https://cosmos-visuals.herokuapp.com/'
APP_ENDPOINT = 'http://127.0.0.1:5000/'

dbClient = DatabaseClient()


class TimedThread(Thread):
    def __init__(self, queue, master):
        Thread.__init__(self)
        self.queue = queue
        self.master = master
        
    def run(self):
        while True:
            key = self.queue.get()
            try:   
                if key == EMIT:
                    self.master.emitHeatmap()
                elif key == POST:
                    self.master.postHeatmap()
                elif key == WRITE:
                    self.master.writeToCSV()
            finally:
                self.queue.task_done()


#####################################
# Begin defining class RandomThread #
#####################################

class RandomThread(Thread):
    def __init__(self):
        self.delay = 0.5
        self.bleScanner = Scanner().withDelegate(ScanDelegate())
        self.peripheral = None
        self.services = None
        self.characteristics = None
        
        self.floormat = Floormat(row=4, column=4)
        self.dims = self.floormat.get_dimensions()
        self.weightMap = demo.demo_acquireSensorClassMapping()
        self.statemat = None
        self.heatmap = None
        self.floormatData = []
        self.rowCnt = 0
        
        self.isConnected = False
        self.refreshFlag = True
        self.writeFlag = False
        
        super(RandomThread, self).__init__()
        
        
    def getWeightMap(self):
        return self.weightMap
        
        
    def getScanner(self):
        return self.bleScanner
        
        
    def getPeripheral(self):
        return self.peripheral
    
    
    def scanDevices(self):
        devices = self.bleScanner.scan()
        return devices
    
    
    def getWriteFlag(self):
        return self.writeFlag
    
    
    def setWriteFlag(self, flag):
        if flag != False and flag != True:
            print("flag has to be either True or False!")
        self.writeFlag = flag
        
    
    def connectDevice(self, devices, mac=None, notifyUUID=None):
        for device in devices:
            if device.addr == mac and mac:
                try:
                    self.peripheral = blePeripheral(dev.addr)
                    
                    if notifyUUID:
                         try:
                             self.peripheral.enableNotify(uuid=notifyUUID)
                         except Exception as e:
                             raise(e)
                    
                    self.isConnected = True
                    print("Connected successfully to {}".format(mac))
                    return True
                             
                except Exception as e:
                    if isinstance(e, BTLEException):
                        print("Device cannot be connected to. It may be connected currently.")
                    else:
                        raise(e)
                    
                    return False
                    
    def disconnectDevice(self):
        if not self.peripheral:
            pass
        else:
            try:
                 self.peripheral.disconnect()
                 self.isConnected = False
            except Exception as e:
                 if isinstance(e, BTLEDisconnectError):
                     print("Failed to disconnect peripheral. Peripheral might not be connected.")
                 else:
                     raise(e)
               
                     
    def acquireData(self):
        data = self.peripheral.getData()
        if data == "\\" and not self.refreshFlag:
            self.refreshFlag = True
        elif self.refreshFlag and data == '/':
            self.refreshFlag = False
            self.floormatData = []
        elif self.refreshFlag:
            self.floormatData = data
            
    
    def activateTiles(self):
        for i in range(self.dims[0]):
            for j in range(self.dims[1]):
                self.floormat.activate_tile(i, j)
    
            
    def updateFloormat(self):
        tiles = set()
        while self.rowCnt < 4:     
            self.acquireData()            
            for j in range(len(self.floormatData)):
                tiles.add(((self.rowCnt, j), self.floormatData[j]))
            
            self.rowCnt = self.rowCnt+1
            socketio.sleep(self.delay)        

        self.rowCnt = 0
        self.floormat.update_tile_state(tiles)
        self.peripheral.setDateTime(datetime.datetime.now())
        self.statemat = self.floormat.get_floormat_states(key=1)
        self.heatmap = createHeatMap(self.statemat, self.weightMap, self.dims[0], self.dims[1])

        print('statemat: {}'.format(self.statemat))
        print('heatmap: {}'.format(self.heatmap))
        print('cols: {}'.format(self.dims[1]))
        print('rows: {}'.format(self.dims[0]))
        print('datetime: {}'.format(self.peripheral.getDateTime()))
        print('isTared: {}'.format(self.floormat.tareStatus()[0]))
        print('completeTared: {}'.format(self.floormat.tareStatus()[1]))
        print('writeFlag: {}'.format(self.writeFlag))
        
        queue = Queue()
        worker = TimedThread(queue, self)
        worker.daemon = True
        worker.start()
            
        queue.put(POST)
        queue.put(EMIT)
        if self.getWriteFlag():
            queue.put(WRITE)
            
        queue.join()
        
        if self.floormat.tareStatus()[1]:
            self.floormat.set_isTared(False)
            self.floormat.set_completeTared(False)
        
    
    def writeToCSV(self):
        if not os.path.isfile('./data.csv'):
            with open("data.csv", 'w+', newline="") as inputFile:
                smWriter = csv.writer(inputFile)
                smWriter.writerow(['datetime','data'])
                smWriter.writerow(getSnapshot(self.peripheral, self.floormat, self.dims[0]-1))
        else:
            with open("data.csv", 'a', newline="") as inputFile:
                smWriter = csv.writer(inputFile)
                smWriter.writerow(getSnapshot(self.peripheral, self.floormat, self.dims[0]-1))
    
        
    def getFloormat(self):
        return self.floormat        
        
        
    def getStatemat(self):
        return self.floormat.get_floormat_states(key=1)
        
        
    def getHeatmap(self):
        return createHeatMap(self.getStatemat(), self.getWeightMap(), 4, 4)
        
    
    def postHeatmap(self):
        try:
            req = requests.post(APP_ENDPOINT + 'matdata', data=json.dumps({'heatmap': self.heatmap, 
                                                                           'cols': self.dims[1],
                                                                           'rows': self.dims[0],
                                                                           'datetime': self.peripheral.getDateTime(),
                                                                           'isTared': self.floormat.tareStatus()[0],
                                                                           'completeTared': self.floormat.tareStatus()[1]}))
            if req.status_code != 200:
                print("Emission failed")
            else:
                print("Emission success")
                
            return True
            
        except Exception as e:
           raise(e)
           time.sleep(3)
           self.postHeatmap()


    def emitHeatmap(self):
        socketio.emit('newheatmap', {'heatmap': self.heatmap,
                                     'cols': self.dims[1],
                                     'rows': self.dims[0],
                                     'datetime': self.peripheral.getDateTime(),
                                     'isTared': self.floormat.tareStatus()[0],
                                     'completeTared': self.floormat.tareStatus()[1]})

        
    def testCalibratedValues(self):
    
        weightMap = demo.demo_acquireSensorClassMapping()
        statemaps = demo.demo_processFloormatData()
        
        while True:
             for heatmap in statemaps:
                 socketio.emit('newheatmap', {'heatmap': heatmap,
                                              'cols': 4,
                                              'rows': 4})
                 socketio.sleep(self.delay+2)


    def runPipeline(self):
        devices = self.scanDevices()
        
        self.activateTiles()
        self.statemat = self.floormat.get_floormat_states(key=1)
        self.heatmap = createHeatMap(self.statemat, self.weightMap, self.dims[1], self.dims[0])
        
        for dev in devices:
            print(dev.addr, dev.getScanData())
            if dev.addr == FLOORMAT_MAC:
                try:
                    self.peripheral = blePeripheral(dev.addr)
                    queue = Queue()
                    worker = TimedThread(queue, self)
                    worker.daemon = True
                    worker.start()
            
                    queue.put(POST)
                    queue.put(EMIT)
                    queue.join()
                    
                except Exception as e:
                    raise(e)
                    sys.exit(1)
	
                self.services = self.peripheral.acquireService()
                self.characteristics = self.peripheral.getCharacteristics()
                self.peripheral.enableNotify(uuid=NOTIFY_UUID)

                while not thread_stop_event.isSet():
                    try:
                        if self.peripheral.peripheral.waitForNotifications(3.0):
                            print("========================= ACQUIRING DATA ========================")
                            self.updateFloormat()
                            socketio.sleep(self.delay)
                            print("=================================================================")

                        else:
                            print("Nothing new has arrived")
                            pass
                            
                    except Exception as e:
                        raise(e)
                        print("=========================== HELLO WORLD ========================")
                        self.peripheral.disconnect()
                        self.peripheral = blePeripheral(FLOORMAT_MAC)
                        self.peripheral.enableNotify(uuid=NOTIFY_UUID)
                        print("Peripheral successfully re-connected!")

    def run(self):
        self.runPipeline()

# Floormat Thread
thread = RandomThread()
thread_stop_event = Event()

###################################
# End defining class RandomThread #
###################################



###################################################
# Begin define SocketIO interactions and handlers #
###################################################
    
@socketio.on('connect')
def connect():
    # need visibility of the global thread object
    global thread
    # Start the floormat thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = RandomThread()
        thread.start()

def connectHandler(msg):
    print("connection established: {}".format(msg))
    socketio.emit('reinitialized', data={"datetime": datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y %H:%M:%S")})

def tareCalHandler(flag):
    print("flag received: {}".format(flag))
    tareCal(flag)

def recordHandler(data):
    thread.setWriteFlag(not thread.getWriteFlag())
    print("Record flag switched")
    recordResponse(thread.getWriteFlag())

def tareCal(flag):
    if (flag == 1 or flag == 2) and not thread.floormat.tareStatus()[0]:
        thread.floormat.set_isTared(True)
        thread.peripheral.writeData(uuid="809a3309-2e5c-4d68-acef-196222cf9886", data=bytes(str(flag), encoding='utf-8'))
        thread.floormat.set_completeTared(True)
    else:
        socketio.emit('midtarecal')
        
def recordResponse(flag):
    socketio.emit('record-notify', data={"flag": flag,
                                         "datetime": datetime.datetime.strftime(datetime.datetime.now(), "%d-%m-%Y %H:%M:%S")})
    

socketio.on_event('connack', connectHandler)
socketio.on_event('tarecal', tareCalHandler)
socketio.on_event('record', recordHandler)

#################################################
# End define SocketIO interactions and handlers #
#################################################

# Python code to start Floormat generation
@app.route('/')
def index():
    return render_template('heatmap.html')


##########################################################
# Begin main application code (DO NOT PUT ANYTHING HERE) #
##########################################################

if __name__ == "__main__":
    socketio.run(app, debug=True, port=8000)
    
########################################################
# End main application code (DO NOT PUT ANYTHING HERE) #
########################################################




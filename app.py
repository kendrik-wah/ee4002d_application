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
from interface.ble_peripheral import blePeripheral, PeripheralDelegate
from algorithms import getSnapshot, createHeatMap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

SERVICE = 'S'
CHARACTERISTIC = 'C'
ACQUIRE = 'A'
EMIT = 'E'
POST = 'P'
WRITE = 'W'
LOG = 'L'
MTU_SIZE = 200

# Define endpoints
TEST_FLOORMAT_MAC = "ac:67:b2:f9:25:de"
ACTUAL_FLOORMAT_MAC = "8c:aa:b5:86:4a:2a"

FLOORMAT_MAC = ACTUAL_FLOORMAT_MAC
NOTIFY_UUID = "e514ae34-a8c5-11ea-bb37-0242ac130002"
APP_ENDPOINT = 'https://cosmos-visuals.herokuapp.com/'
# APP_ENDPOINT = 'http://127.0.0.1:5000/'

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
                if key == SERVICE:
                    self.master.services = self.master.peripheral.acquireService()
                    
                elif key == CHARACTERISTIC:
                    self.master.characteristics = self.master.peripheral.getCharacteristics()
                    
                elif key == ACQUIRE:
                    self.master.floormat.update_tile_state(self.master.tiles)
                    self.master.peripheral.setDateTime(datetime.datetime.now())
                    self.master.statemat = self.master.floormat.get_floormat_states(key=1)
                    self.master.heatmap = createHeatMap(self.master.statemat, self.master.weightMap, self.master.dims[0], self.master.dims[1])
        
                elif key == EMIT:
                    self.master.emitHeatmap()
                    
                elif key == POST:
                    self.master.postHeatmap()
                    
                elif key == WRITE:
                    self.master.writeToCSV()
                    
                elif key == LOG:
                    print('statemat: {}'.format(self.master.statemat))
                    print('heatmap: {}'.format(self.master.heatmap))
                    print('datetime: {}'.format(self.master.peripheral.getDateTime()))
                    print('isTared: {}'.format(self.master.floormat.tareStatus()[0]))
                    print('completeTared: {}'.format(self.master.floormat.tareStatus()[1]))
                    print('writeFlag: {}'.format(self.master.writeFlag))
            
            except Exception as e:
                self.master.peripheral.disconnect()
                self.master.peripheral = blePeripheral(FLOORMAT_MAC, MTU_SIZE)
                self.master.peripheral.peripheral.setDelegate(PeripheralDelegate(self.master.peripheral))
                self.master.peripheral.enableNotify(uuid=NOTIFY_UUID)
                self.master.floormat.set_isTared(False)
                self.master.floormat.set_completeTared(False)
                print("Peripheral successfully re-connected!")
                
            except KeyboardInterrupt:
            	self.master.peripheral.disconnect()
            	sys.exit(1)
            	
            finally:
                self.queue.task_done()


#####################################
# Begin defining class RandomThread #
#####################################

class RandomThread(Thread):
    def __init__(self):
        self.delay = 0.1
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
        self.tiles = set()
        
        self.isConnecting = False
        self.isConnected = False
        self.refreshFlag = True
        self.writeFlag = False
        
        self.workers = 1 # Change number of workers here.
        self.queue = Queue()
        for i in range(self.workers):
            worker = TimedThread(self.queue, self)
            worker.daemon = True
            worker.start()
        
        super(RandomThread, self).__init__()
        
        
    def getWeightMap(self):
        return self.weightMap
        
        
    def getScanner(self):
        return self.bleScanner
        
        
    def getPeripheral(self):
        return self.peripheral
    
    
    def scanDevices(self, cnt=0):
        return self.bleScanner.scan()
    
    
    def getWriteFlag(self):
        return self.writeFlag
    
    
    def setWriteFlag(self, flag):
        if flag != False and flag != True:
            print("flag has to be either True or False!")
        self.writeFlag = flag
        
    
    def connectDevice(self, devices, mac=None, notifyUUID=None, counter=0):
        print("Finding device {}, counter at: {}".format(mac, counter))
        
        if not devices:
            return False
            
        elif counter >= 3:
            print("isConnecting: {}, isConnected: {}".format(self.isConnecting, self.isConnected))
            print("Max connection counter reached. Will restart after 5 seconds")
            time.sleep(5)
            self.connectDevice(self.scanDevices(), mac, notifyUUID, 0)
            
        for device in devices:
            if device.addr == mac and mac and not self.isConnected and not self.isConnecting and counter < 3:
                try:
                    self.peripheral = blePeripheral(device.addr, MTU_SIZE)
                    self.peripheral.peripheral.setDelegate(PeripheralDelegate(self.peripheral))
                    self.isConnecting = True
                    
                    self.queue.put(POST)
                    self.queue.put(EMIT)
                    self.queue.join()
                    
                    if notifyUUID:
                         try:
                             self.peripheral.enableNotify(uuid=notifyUUID)
                         except Exception as e:
                             raise(e)
                    
                    self.queue.put(SERVICE)
                    self.queue.put(CHARACTERISTIC)
                    self.queue.join()

                    self.isConnected = True
                    print("Connected successfully to {}".format(mac))
                             
                except Exception as e:
                    raise(e)
                    #if isinstance(e, bluepy.btle.BTLEException):
                    #    print("Device cannot be connected to. It may be connected currently.")
                    #    time.sleep(5)
                    #    self.connectDevice(self.scanDevices(), mac, notifyUUID, counter+1)
                    #else:
                    #    raise(e)
                        
        if counter < 3 and not self.isConnected:
            self.isConnecting = False
            self.connectDevice(self.scanDevices(), mac, notifyUUID, counter+1)
            
        return counter < 3
                    
    def disconnectDevice(self):
        if not self.peripheral:
            pass
        else:
            try:
                 self.peripheral.disconnect()
                 self.isConnected = False
            except Exception as e:
                 raise(e)
                 #if isinstance(e, BTLEDisconnectError):
                  #   print("Failed to disconnect peripheral. Peripheral might not be connected.")
                # else:
                 #    raise(e)
               
                     
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
        self.tiles = set()
        self.acquireData()
        cntr = 0
        
        while self.rowCnt < self.dims[0]:
            for j in range(self.dims[1]):
                self.tiles.add(((self.rowCnt, j), self.floormatData[cntr]))
                cntr += 1
            
            self.rowCnt = self.rowCnt+1     
        
        self.rowCnt = 0
        self.queue.put(ACQUIRE)
        self.queue.put(LOG)    
        self.queue.put(POST)
        self.queue.put(EMIT)
        if self.getWriteFlag():
            self.queue.put(WRITE)
            
        self.queue.join()
        
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
                 socketio.sleep(self.delay/2)


    def runPipeline(self):
        
        self.activateTiles()
        self.statemat = self.floormat.get_floormat_states(key=1)
        self.heatmap = createHeatMap(self.statemat, self.weightMap, self.dims[1], self.dims[0])
        
        while not self.isConnected:
            if not self.isConnecting:
                self.isConnecting = True
                self.connectDevice(self.scanDevices(), FLOORMAT_MAC, NOTIFY_UUID)
            time.sleep(1)
            
            if self.isConnected:
                break
        
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
                self.peripheral.disconnect()
                self.peripheral = blePeripheral(FLOORMAT_MAC, MTU_SIZE)
                self.peripheral.peripheral.setDelegate(PeripheralDelegate(self.peripheral))
                self.peripheral.enableNotify(uuid=NOTIFY_UUID)
                self.floormat.set_isTared(False)
                self.floormat.set_completeTared(False)
                print("Peripheral successfully re-connected!")

    def run(self):
        try:
            self.runPipeline()
        except KeyboardInterrupt:
            if self.peripheral:
                self.peripheral.disconnect()
            sys.exit(1)
            
            
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
    socketio.emit('record-flagger', {"flag": False})

def tareCalHandler(flag):
    print("flag received: {}".format(flag))
    tareCal(flag)

def recordHandler():
    thread.setWriteFlag(not thread.getWriteFlag())
    print("Record flag switched")
    recordResponse(thread.getWriteFlag())
    if thread.getWriteFlag():
        socketio.emit('record-flagger', {"flag": True})
    else:
        socketio.emit('record-flagger', {"flag": False})


def tareCal(flag):
    if (flag == 1 or flag == 2) and not thread.floormat.tareStatus()[0]:
        try:
            thread.floormat.set_isTared(True)
            thread.peripheral.writeData(uuid="809a3309-2e5c-4d68-acef-196222cf9886", data=bytes(str(flag), encoding='utf-8'))
            thread.floormat.set_completeTared(True)
            
        except Exception as e:
            thread.peripheral.disconnect()
            thread.peripheral = blePeripheral(FLOORMAT_MAC, MTU_SIZE)
            thread.peripheral.peripheral.setDelegate(PeripheralDelegate(thread.peripheral))
            thread.peripheral.enableNotify(uuid=NOTIFY_UUID)
            thread.floormat.set_isTared(False)
            thread.floormat.set_completeTared(False)
            print("Peripheral successfully re-connected!")
            
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
    try:
        socketio.run(app, debug=True, port=8000)
    except KeyboardInterrupt:
        if thread.peripheral:
            thread.peripheral.disconnect()
        sys.exit(1)
    
########################################################
# End main application code (DO NOT PUT ANYTHING HERE) #
########################################################




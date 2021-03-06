import os
import datetime
import json
import floormat
import requests
import pymongo
import demo
import csv
import datetime
import bluepy.btle

from random import random
from threading import Thread, Event
from pymongo import MongoClient
from bluepy.btle import Scanner
from floormat.floormat import Floormat
from interface.ble_scanner import ScanDelegate
from interface.ble_peripheral import blePeripheral
from algorithms import getSnapshot, createHeatMap


FLOORMAT_MAC = "ac:67:b2:f9:25:de"
NOTIFY_UUID = "e514ae34-a8c5-11ea-bb37-0242ac130002"

def demo_acquireSensorClassMapping():

    with open("weightMapping.json", "r") as json_file:
        loadedData = json.load(json_file)

    weightMapping = dict()
    for key, val in loadedData.items():
        weightMapping[int(key)] = val
    
    return weightMapping


def demo_getTileFactors():
    
    with open("tileFactors.json", "r") as json_file:
        loadedData = json.load(json_file)
        
    tileFactors = dict()
    for key, val in loadedData.items():
        tileFactors[int(key)] = val
    
    return tileFactors
    
    
def demo_processFloormatData():
    
    test_cases = open("test_cases.txt", "rb")
    weightMap = demo_acquireSensorClassMapping()
    statemaps = []

    for test_case in test_cases:

        floormat = Floormat(row=4, column=4, tileFactor=demo_getTileFactors())
        dims = floormat.get_dimensions()
        m = dims[1]
        n = dims[0]
        tiles = set()

        test_case = list(map(lambda x: float(x), test_case.decode('utf-8').split(',')))
        counter = 0
        
        for i in range(m):
            for j in range(n):
                tiles.add(((i, j), test_case[counter]))
                counter += 1
                floormat.activate_tile(i, j)
        print("tiles: {}".format(tiles))

        floormat.update_tile_state(tiles)
        statemat = floormat.get_floormat_states(key=1)
        statemat = list(map(lambda x: list(map(lambda y: round(y, 2), x)), statemat))
        
        print("=================================================\n")
        print("statemat: {}".format(statemat))
        print("=================================================\n")

        for i in range(m):
            for j in range(n):
                for key, val in weightMap.items():
                    if statemat[i][j] <= 0:
                        statemat[i][j] = val["colour"]
                        break

                    elif val["min"] <= statemat[i][j] <= val["max"]:
                        statemat[i][j] = val["colour"]
                        break

        statemaps.append(statemat)
    
    return statemaps


def demo_bleScan():
	weightMap = demo_acquireSensorClassMapping()
	bleScanner = Scanner().withDelegate(ScanDelegate())
	devices = bleScanner.scan()

	for dev in devices:
		print(dev.addr, dev.getScanData())
		if dev.addr == '8c:aa:b5:86:4a:2a':

			peripheral = blePeripheral(dev.addr)
			services = peripheral.acquireService()
			print("services: {}".format(services))
			
			characteristics = peripheral.getCharacteristics()
			print("characteristics: {}".format(characteristics))
			print()

			print("Peripheral: {}".format(peripheral.getAddress()))
			print("=================================")

			for service in services:
				print("UUID: {}".format(service.uuid))
				print("UUID: {}".format(service.uuid.getCommonName()))
				print("UUID: {}".format(service.uuid.binVal))
				c = peripheral.getCharacteristics(uuid=service.uuid)
				print("c: {}".format(c))
			print("=================================")

			for uuid, chars in characteristics.items():
				print("UUID: {}, {}".format(uuid.getCommonName(), uuid.binVal))
				for char in chars:
					print("Characteristic: {}, {}, {}".format(char.uuid, char.propertiesToString(), char.getHandle()))

				print()

			peripheral.enableNotify(uuid="e514ae34-a8c5-11ea-bb37-0242ac130002")
			while True:
				if peripheral.peripheral.waitForNotifications(3.0):
					print("{}: {}".format(peripheral.getDateTime(), peripheral.getData()))
				else:
					print("nada nada yada haha")
				
			print("Waiting")
			break

	

if __name__ == "__main__":
    print(demo_getTileFactors())
    # demo_processFloormatData()

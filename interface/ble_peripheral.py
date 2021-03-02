from bluepy.btle import Peripheral, DefaultDelegate
from bluepy import btle

import datetime
import threading

event = threading.Event()

def processData(data=None, delimiter=','):
	if not data:
		return None
	if not isinstance(data, bytes):
		pass
	else:
		# floormat values
		return list(map(lambda x: float(x), data.decode().split(delimiter)))

class PeripheralDelegate(DefaultDelegate):

    def __init__(self, per):
        DefaultDelegate.__init__(self)
        self.peripheral = per

    def handleNotification(self, cHandle, data):      
        self.peripheral.setDateTime(datetime.datetime.now())
        print("raw data: {}".format(data))
        
        if data == b'/' or data == b'\\':
            self.peripheral.setData(data.decode())
        else:
            self.peripheral.setData(processData(data, ','))
        
        #print("values updated")
        event.wait(1)


class blePeripheral(object):
	def __init__(self, addr):
		self.peripheral = Peripheral(addr, "public")
		self.peripheral.setDelegate(PeripheralDelegate(self))
		self.dt = None
		self.setDateTime(datetime.datetime.now())

		self.data = ""

	def getAddress(self):
		return self.peripheral.addr

	def disconnect(self):
		return self.peripheral.disconnect()

	def acquireService(self, uuid=None):
		if not uuid:
			return self.peripheral.getServices()
		else:
			return self.peripheral.getServiceByUUID(uuid)

	def getCharacteristics(self, uuid=None, sFlag=True):
		if sFlag:
			services = self.acquireService(uuid)

			if uuid:
				return services.getCharacteristics()
			else:
				characteristics = dict()

				for service in services:
					characteristics[service.uuid] = service.getCharacteristics()

				return characteristics
				
		else:
			if uuid:
				return self.peripheral.getCharacteristics(uuid=uuid)
			else:
				return self.peripheral.getCharacteristics()
				
	def enableNotify(self, uuid):
		if not uuid:
			print("Needs a valid UUID to enable notifications.")
			return
		else:
			setup_data = b'\x01\x00'
			char = self.getCharacteristics(uuid=uuid)[0]
			notifyHandle = char.getHandle() + 1
			self.peripheral.writeCharacteristic(notifyHandle, setup_data, withResponse=True)
			
	def setData(self, data):
		self.data = data
	
	def getData(self):
		return self.data
		
	def setDateTime(self, dt):
		self.dt = datetime.datetime.strftime(dt, "%d-%M-%Y %H:%M:%S")
	
	def getDateTime(self):
		return self.dt
		
	def writeData(self, uuid=None, data=None):
		dataCharacteristic = self.peripheral.getCharacteristics(uuid=uuid)
		resp = dataCharacteristic.write(data=data, withResponse=True)
		print(resp)
			


from bluepy.btle import Peripheral, DefaultDelegate

class PeripheralDelegate(DefaultDelegate):

    def __init__(self, per):
        DefaultDelegate.__init__(self)
        self.peripheral = per

    def handleNotification(self, cHandle, data):
        sensedValChar = self.peripheral.getCharacteristics(uuid="0000fff0-0000-1000-8000-00805f9b34fb")[0]
        print(sensedValChar.read(), cHandle, data)


class blePeripheral(object):
    def __init__(self, addr):
        self.peripheral = Peripheral(addr)
        self.peripheral.setDelegate(PeripheralDelegate(self))

    def getAddress(self):
        return self.peripheral.addr

    def disconnect(self):
        return self.peripheral.disconnect()

    def acquireService(self, uuid=None):
        if not uuid:
            return self.peripheral.getServices()
        else:
            return self.peripheral.getServiceByUUID(uuid)

    def getCharacteristics(self, uuid=None):
        services = self.acquireService(uuid)

        if uuid:
            return services.getCharacteristics()
        else:
            characteristics = dict()

            for service in services:
                characteristics[service.uuid] = service.getCharacteristics()

            return characteristics

    def enableNotify(self, uuid):
        if not uuid:
            print("Needs a valid UUID to enable notifications.")
            return
        else:
            setup_data = b'\x01\x00'
            char = self.getCharacteristics(uuid=uuid)[3]
            notifyHandle = char.getHandle() + 1
            self.peripheral.writeCharacteristic(notifyHandle, setup_data, withResponse=True)


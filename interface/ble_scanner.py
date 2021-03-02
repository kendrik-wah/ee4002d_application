from bluepy.btle import Scanner, DefaultDelegate


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.scanner = Scanner()
        self.scan_time = 30
        self.devices = set()
        self.services = dict()

    def addDevices(self, dev):
        self.devices.add(dev)
        self.services[dev] = dict()

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev and dev.addr in self.devices:
            print("Discovered device: ", dev.addr)

    def beginScan(self):
        devices = self.scanner.scan(self.scan_time)
        return devices

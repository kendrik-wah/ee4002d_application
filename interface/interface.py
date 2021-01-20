import requests

interfaces = {1: "pyboard",
              2: "database",
              3: "application",
              None: "unconnected",
              4: 'unknown'}

class Interface(object):

    def __init__(self, type=None):
        """
        :param type: integer, meant to denote which interface it is.
                     None = no interface attached yet.
                     1 = pyboard interface.
                     2 = database interface.
                     3 = application interface.
        """
        self._type = type
        self._endpoint = None

    def get_interface_type(self):
        if self._type not in interfaces:
            return interfaces[4]
        return interfaces[self._type]

    def change_interface_type(self, type):
        if not type:
            print("Please state a type.")
            return
        else:
            self._type = type

    def notify_client(self, payload=dict()):
        if not payload:
            print("No message in notification")
            return

        try:
            tx = requests.post(self._endpoint, payload)
        except requests.exceptions.Timeout:
            raise Exception("timeout event has occurred! check that {} is still contactable.".format(self._endpoint))
        except requests.exceptions.HTTPError:
            error_code = tx.status_code
            raise Exception("HTTP error {} has occurred.".format(error_code))
        else:
            return tx.json()


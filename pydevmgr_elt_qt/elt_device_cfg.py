from pydevmgr_core_qt import QtBaseDevice 

class EltDeviceCfg(QtBaseDevice):
    def __init__(self, device):
        super().__init__(device)
        self.link.data.name = device.name

    class Monitor(QtBaseDevice.Monitor):
        class Data(QtBaseDevice.Monitor.Data):
            name: str = ""
    
        def start(self, widget, data):
            widget.name.setText(str(data.name)) 
    
    class Connector(QtBaseDevice.Connector):
        def connect(self, widget, device):
            pass

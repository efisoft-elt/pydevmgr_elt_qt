
from pydevmgr_core import BaseDevice
from systemy import storedproperty
from pydevmgr_qt import QtDevice, Connector, QtFormular

class QtEltDevice(QtDevice):
    Widget = None 
    @classmethod
    def get_widget_class(cls):
        return cls.Widget 
    @storedproperty
    def feedback(self):
        return None
    # def link(self, 
    #         device: BaseDevice, 
    #         connection: Connector,
    #         )-> None:
    #     super().link( device, connection) 

    #     for action in self.find( QtFormular ):
    #         action.link_action(device)


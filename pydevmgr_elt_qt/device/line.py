from pydevmgr_core  import BaseDevice, storedproperty
from pydevmgr_qt.api import  QtTextFeedback, QtInterface, QtNodeFactory,  PairingType, Connector
from pydevmgr_elt.base.eltstat import StateInfo
from .base import QtEltDevice 
from .actions import ChangeState, TogleIgnore 
from pydevmgr_elt_qt import nodes # make sure it is imported 

class QtMenuFeedback(QtTextFeedback):
    def error(self, err):
        self.node.widget.setItemText(0, "!!ERROR!!")
    def clear(self, msg):
        self.node.widget.setItemText(0, "")

class QtEltDeviceLine(QtEltDevice):
    feedback = QtMenuFeedback.Config( node=QtNodeFactory( vtype=str ,widget="state_action") ) 

    class Stat(QtInterface):
        class Config:
            pairing_type = PairingType.source
            implicit_pairing = True
        substate_info = QtNodeFactory(vtype=StateInfo, widget="substate")
    
    stat = Stat.Config( pair="stat")
    is_ignored = QtNodeFactory( vtype=bool, pair="is_ignored", widget="check", reverse=True)

    name = QtNodeFactory( vtype=str, widget="name")

    # actions  
    change_state = ChangeState.Config( actioner="state_action", feedback=feedback) 
    togle_ignore = TogleIgnore.Config( actioner="check")   
    
    def link(self, device: BaseDevice, connection: Connector)-> None:
        super().link(device, connection)
        self.name.set( device.name )


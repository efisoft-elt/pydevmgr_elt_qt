from pydevmgr_core  import BaseDevice
from pydevmgr_qt.api import (
        QtInterface,
        QtNodeFactory,
        QtTextFeedback,
        Connector,
        PairingType)
from pydevmgr_elt.base.eltstat import StateInfo

from .base import QtEltDevice 
from .actions import ChangeState , TogleIgnore
from .. import nodes # do no remove 


QNF = QtNodeFactory
class QtEltDeviceCtrl(QtEltDevice):
    feedback = QtTextFeedback.Config(
            node=QtNodeFactory( vtype=str, widget="rpc_feedback")
        )

    class Stat(QtInterface):
        class Config:
            pairing_type = PairingType.source 
            implicit_pairing = True 

        state_info = QNF(vtype=StateInfo, widget="state")
        substate_info = QNF(vtype=StateInfo, widget="substate")
        error_info = QNF(vtype=StateInfo, widget="error_txt")

    stat = Stat.Config(pair="stat")
    is_ignored = QNF( vtype=bool, pair="is_ignored", widget="check", reverse=True)
    name = QNF( vtype=str, widget="name")

    # actions  
    change_state = ChangeState.Config( actioner="state_action", feedback=feedback) 
    togle_ignore = TogleIgnore.Config( actioner="check")   
    
    def link(self, device: BaseDevice, connection: Connector)-> None:
        super().link(device, connection)
        self.name.set( device.name )


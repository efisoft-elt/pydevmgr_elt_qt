
from pydevmgr_qt.api import (
        QtFormular, 
        QtTextFeedback, 
        QtNodeFactory,
        Action, ActionEnum
    )
from pydevmgr_elt import EltDevice 
from enum import Enum 

class STATE_COMMAND(int, Enum):
    _ = -1
    INIT = 0 
    ENABLE = 1 
    DISABLE = 2
    RESET = 3


class ChangeState(QtFormular):
    class Config:
         
        menu = QtNodeFactory(vtype=(STATE_COMMAND, STATE_COMMAND._ ), widget="state_action", clear=True)

    def link_action(self, device: EltDevice):
        def reset_menu():
            self.actioner.setCurrentIndex(0)
        
        feedback = self.feedback
        state_action = ActionEnum( after=reset_menu)
        state_action.add_action( STATE_COMMAND.INIT, Action(device.init, feedback=feedback))
        state_action.add_action( STATE_COMMAND.ENABLE, Action(device.enable, feedback=feedback))
        state_action.add_action( STATE_COMMAND.DISABLE, Action(device.disable, feedback=feedback))
        state_action.add_action( STATE_COMMAND.RESET, Action(device.reset, feedback=feedback))
        self.set_action( state_action) 

class TogleIgnore(QtFormular):
    is_ignored = QtNodeFactory( vtype=bool,  widget="check", reverse=True, set_default=False)

    def link_action(self, device:EltDevice):
        action  = Action( device.is_ignored.set , [self.is_ignored] )
        self.set_action(action) 



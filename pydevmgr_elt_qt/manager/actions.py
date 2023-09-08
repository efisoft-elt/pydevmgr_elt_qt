from enum import Enum
from PyQt5.QtWidgets import QComboBox
from pydevmgr_elt import EltManager

from pydevmgr_qt.api import (
        QtFormular, 
        QtNodeFactory, 
        Action, 
        ActionEnum
)

class MANAGER_COMMAND(Enum):
    INIT = 0 
    ENABLE = 1 
    DISABLE = 2
    RESET = 3



class ChangeState(QtFormular):
    class Config:
        menu = QtNodeFactory(vtype=MANAGER_COMMAND, widget="actionMenu" )

    def link_action(self, manager: EltManager):
        self.menu 
        if isinstance( self.actioner, QComboBox):
            def after():
                self.actioner.setCurrentIndex(0)
        else:
            after = None 
       
        feedback = self.feedback 
        change_state = ActionEnum( after=after )
        change_state.add_action( MANAGER_COMMAND.INIT, Action(manager.init, feedback=feedback))
        change_state.add_action( MANAGER_COMMAND.ENABLE, Action(manager.enable, feedback=feedback))
        change_state.add_action( MANAGER_COMMAND.DISABLE, Action(manager.disable, feedback=feedback))
        change_state.add_action( MANAGER_COMMAND.RESET, Action(manager.reset, feedback=feedback))
        self.set_action(change_state)
        
        


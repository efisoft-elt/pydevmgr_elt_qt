from enum import Enum
from pydevmgr_elt import Shutter
from pydevmgr_qt.api import (
        ActionEnum, Action , 
        PairingType, QtFormular, 
        QtNodeFactory as QNF 
    )

class SHUTTER_COMMAND(int, Enum):
    _ = 0
    OPEN   = 10
    CLOSE = 11

class Open(QtFormular):
    def link_action(self, shutter: Shutter):
        self.set_action(Action( shutter.open, feedback=self.feedback )) 

class Close(QtFormular):
    def link_action(self, shutter: Shutter):
        self.set_action(Action( shutter.close, feedback=self.feedback )) 

class ShutterCommands(QtFormular):
    class Config:
        menu = QNF( vtype=SHUTTER_COMMAND,  widget="state_action")

    def link_action(self, shutter: Shutter)->None:
        feedback = self.feedback 

        def reset_menu():
            self.actioner.setCurrentIndex(0)
        
        lamp_action = ActionEnum( after=reset_menu)
        lamp_action.add_action( 
                    SHUTTER_COMMAND.OPEN, 
                    Action(shutter.open, feedback=feedback)
                    )

        lamp_action.add_action( 
                    SHUTTER_COMMAND.CLOSE, 
                    Action(shutter.close, feedback=feedback)
                    )
        self.set_action(lamp_action)


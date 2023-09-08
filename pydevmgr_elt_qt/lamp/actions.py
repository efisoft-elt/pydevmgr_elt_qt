from enum import Enum
from pydevmgr_elt.devices.lamp import Lamp
from pydevmgr_qt.api  import (
        ActionEnum,
        Action,
        PairingType,
        QtFormular,
        QtNodeFactory as QNF 
    )

class LAMP_COMMAND(int, Enum):
    _ = 0 
    SWITCH_ON  = 10
    SWITCH_OFF = 11

class SwitchOn(QtFormular):
    class Config:
        intensity = QNF(vtype=(float,1.0), widget="input_intensity")
        time = QNF(vtype=(float,10), widget="input_time")
        pairing_type = PairingType.none 
        
    def link_action(self, lamp: Lamp):
        self.set_action(Action( lamp.switch_on, [self.intensity, self.time], feedback=self.feedback )) 

class SwitchOff(QtFormular):
    def link_action(self, lamp: Lamp):
        self.set_action(Action( lamp.switch_off, feedback=self.feedback )) 

class LampCommands(QtFormular):
    class Config:
        intensity = SwitchOn.intensity 
        time = SwitchOn.time 
        menu = QNF( vtype=LAMP_COMMAND,  widget="state_action")

    def link_action(self, lamp: Lamp)->None:
        feedback = self.feedback 

        def reset_menu():
            self.actioner.setCurrentIndex(0)
        
        lamp_action = ActionEnum( after=reset_menu)
        lamp_action.add_action( 
                    LAMP_COMMAND.SWITCH_ON, 
                    Action(lamp.switch_on, [self.intensity, self.time], feedback=feedback)
                    )

        lamp_action.add_action( 
                    LAMP_COMMAND.SWITCH_OFF, 
                    Action(lamp.switch_off, feedback=feedback)
                    )
        self.set_action(lamp_action)


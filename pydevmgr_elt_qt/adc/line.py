from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QFrame, QLabel, QLineEdit
from pydantic.fields import Field

from pydevmgr_elt.devices.adc import Adc
from PyQt5 import uic, QtWidgets
from ..io import find_ui
from pydevmgr_core_qt import  (ActionMap, BaseFeedback, Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.line as base 
from pydevmgr_elt_qt.io import find_ui

Base = base.EltDeviceLine

class ActionMenuName(str, Enum):
    STOP = "STOP"
    MOVE_ANGLE = "MOVE ANGLE"
    START_TRACK = "START TRACK"
    STOP_TRACK = "STOP TRACK"

    

class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class Proc(base.Proc):
   ... 

class Widget(base.Widget):
    trak_mode: QLabel
    motor1_pos_actual: QLabel
    motor2_pos_actual: QLabel
    input_angle: QLineEdit 

    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('adc_line_frame.ui'), self) 
    

class Data(base.Data):
    track_mode_txt: NodeVar[str] = Field("", node="stat.track_mode_txt")
    motor1_pos_actual: NodeVar[float] = Field(0.0, node="motor1.stat.pos_actual")
    motor2_pos_actual: NodeVar[float] = Field(0.0, node="motor2.stat.pos_actual")

@dataclass
class Args(base.Args):
    input_angle: Callable = None

Actions = base.Actions

##############################################################  

def set_widget(widget: Widget, adc: Adc):
    base.set_widget(widget, adc)

    Proc.pos_setter.set(widget.input_angle, 0.0)

    wa = widget.state_action
    wa.addItems( ActionMenuName )

def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    Proc.text_setter.set( w.track_mode_txt, data.track_mode_txt)
    Proc.pos_setter.set( w.motor1_pos_actual, data.motor1_pos_actual)
    Proc.pos_setter.set( w.motor2_pos_actual, data.motor2_pos_actual)



def set_args(args: Args, widget)-> Args:
    base.set_args(args, widget)
    args.input_angle = lambda : Proc.float_getter.get(widget.input_angle)


def set_actions(actions: Actions, adc: Adc, args: Args)-> Actions:
    base.set_actions(actions, adc, args)

    feedback = args.feedback
    
    command = actions.command 
    command.add_action(ActionMenuName.STOP,  Action(adc.stop, [], feedback) )

    command.add_action(  ActionMenuName.MOVE_ANGLE, 
            Action(adc.move_angle, 
                   [args.input_angle], 
                   feedback
                   )
            )
               
    command.add_action( ActionMenuName.START_TRACK, 
            Action(adc.start_track, 
                   [args.input_angle], 
                   feedback
                   )
            )
    command.add_action(ActionMenuName.STOP_TRACK, 
            Action(adc.stop_track, 
                   [], 
                   feedback
                   )
            )

connect_action = base.connect_action
disconnect_action = base.disconnect_action



####################################################################################

@record_qt(Adc, "line")
class AdcLine(Base):
    Widget = Widget
        
    class Monitor(Base.Monitor):
        Data = Data
        _update_data = staticmethod(update_data)

    class Connector(Base.Connector):
        Args = Args
        Actions = Actions 
        
        _set_widget        = staticmethod(set_widget)
        _set_args          = staticmethod(set_args)
        _set_actions       = staticmethod(set_actions)
        _connect_action    = staticmethod(connect_action)
        _disconnect_action = staticmethod(disconnect_action)

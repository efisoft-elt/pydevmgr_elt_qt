from dataclasses import dataclass
from enum import IntEnum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit
from pydantic.fields import Field
from pydantic.main import BaseModel
from pydevmgr_core.base.node_alias import NodeAlias
from pydevmgr_core_ui import feedback

from pydevmgr_elt.devices.adc import Adc
from .elt_device_line import EltDeviceLine, MenuErrorFeedback
from PyQt5 import uic, QtWidgets
from .io import find_ui
from pydevmgr_core_qt import  (ActionMap, BaseFeedback, Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 

Base = EltDeviceLine


class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class Proc(Base.Proc):
    pos_setter =   get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")

class AdcLineWidget(Base.Widget):
    trak_mode: QLabel
    motor1_pos_actual: QLabel
    motor2_pos_actual: QLabel
    input_angle: QLineEdit 

    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('adc_line_frame.ui'), self) 
    

class AdcLineData(Base.Monitor.Data):
    track_mode_txt: NodeVar[str] = Field("", node="stat.track_mode_txt")
    motor1_pos_actual: NodeVar[float] = Field(0.0, node="motor1.stat.pos_actual")
    motor2_pos_actual: NodeVar[float] = Field(0.0, node="motor2.stat.pos_actual")



class AdcLineSetter(Base.Monitor.DataSetter):
    def set(self, w, data):
        super().set(w, data)
        Proc.text_setter.set( w.track_mode_txt, data.track_mode_txt)
        Proc.pos_setter.set( w.motor1_pos_actual, data.motor1_pos_actual)
        Proc.pos_setter.set( w.motor2_pos_actual, data.motor2_pos_actual)


def set_adc_line_widget(widget):
    Proc.pos_setter.set(widget.input_angle, 0.0)

    wa = widget.state_action
    wa.addItems( ["MOVE ANGLE", "START TRACK", "STOP TRACK" ])


@dataclass
class AdcLineArgs:
    input_angle: Callable
    feedback:  BaseFeedback
    reset : Callable

def adc_line_args(widget)-> AdcLineArgs:
    return AdcLineArgs( 
                input_angle = lambda : Proc.float_getter.get(widget.input_angle), 
                feedback = MenuErrorFeedback(widget.state_action), 
                reset = lambda: widget.state_action.setCurrentIndex(0)
        )


@dataclass
class AdcLineActions:
    command: ActionMap

def adc_line_actions(adc: Adc, args: AdcLineArgs)-> AdcLineActions:
    feedback = args.feedback
    
    command = ActionMap(after = args.reset)
    command.add_action("STOP",  Action(adc.stop, [], feedback) )

    command.add_action(  "MOVE ANGLE", 
            Action(adc.move_angle, 
                   [args.input_angle], 
                   feedback
                   )
            )
               
    command.add_action( "START TRACK", 
            Action(adc.start_track, 
                   [args.input_angle], 
                   feedback
                   )
            )
    command.add_action("STOP TRACK", 
            Action(adc.stop_track, 
                   [], 
                   feedback
                   )
            )
    
    return AdcLineActions(command = command) 




def adc_line_connect(widget, adc):
    set_adc_line_widget(widget)
    args = adc_line_args(widget)
    actions = adc_line_actions(adc, args)
    Proc.menu_connector.connect( widget.state_action, actions.command)
    widget.adc_line_actions = actions     


@record_qt(Adc, "line")
class AdcLine(Base):
    Widget = AdcLineWidget
    Proc = Proc
    class Monitor(Base.Monitor):
        Data = AdcLineData
        DataSetter = AdcLineSetter
        data_setter = DataSetter()
               
        def update(self, widget, data):
            super().update(widget, data)
  

    class Connector(Base.Connector):
        def connect(self, widget, adc):
            super().connect(widget, adc)
            adc_line_connect(widget, adc)


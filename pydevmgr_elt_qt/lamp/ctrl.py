from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydevmgr_core_ui.getter import get_getter_class

from pydevmgr_elt import Lamp
from PyQt5 import uic, QtWidgets
from pydevmgr_elt_qt.io import find_ui
from pydevmgr_core_qt import  ( Action, get_setter_class, record_qt) 
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.ctrl as base 

Base = base.EltDeviceCtrl
Device =  Lamp


class Widget(base.Widget):
    time_left: QLabel
    intensity: QLabel
    
    input_intensity: QLineEdit
    input_time: QLineEdit
    on: QPushButton
    off: QPushButton

    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('lamp_ctrl_frame.ui'), self) 

class Proc(base.Proc):
    time_setter   = get_setter_class(QtWidgets.QLabel, float)(format="%.0f")
    intensity_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.1f")
       

class Data(base.Data):
    class Stat(Base.Monitor.Data.Stat):
        time_left: NodeVar[float] = 0.0
        intensity: NodeVar[float] = 0.0
    
    stat: Stat = Stat()


@dataclass
class Args(base.Args):
    # e.g. pos_target: Callable
    intensity: Callable = None 
    time: Callable = None 
    
@dataclass
class Actions(base.Actions):
    # e.g. stop: Action
    switch_on:  Action = None 
    switch_off: Action = None 

##############################################################  

def set_widget(widget: Widget, device: Device):
    base.set_widget(widget, device)

    Proc.time_setter.set(widget.input_time, 10)
    Proc.intensity_setter.set(widget.input_intensity, 1.0)

def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    s = data.stat
    Proc.time_setter.set( w.time_left, s.time_left)
    Proc.intensity_setter.set( w.intensity, s.intensity)

def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)
    args.intensity = lambda: Proc.float_getter.get(widget.input_intensity)
    args.time = lambda: Proc.float_getter.get(widget.input_time)

def set_actions(actions: Actions, device: Device, args: Args)-> Actions:
    base.set_actions(actions, device, args)
    actions.switch_on = Action(device.switch_on, [args.intensity, args.time], args.feedback)
    actions.switch_off = Action(device.switch_off, [], args.feedback)
    
def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    Proc.button_connector.connect( widget.on , actions.switch_on)
    Proc.button_connector.connect( widget.off , actions.switch_off)

def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)
    Proc.button_connector.disconnect( widget.on )
    Proc.button_connector.disconnect( widget.off )



######################################################################
@record_qt(Lamp, "ctrl")
class LampCtrl(Base):
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

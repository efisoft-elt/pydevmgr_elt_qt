
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable
from PyQt5.QtWidgets import QFrame, QLabel, QLineEdit
from pydantic.fields import Field
from pydevmgr_core.base.node_alias import NodeAlias

from pydevmgr_elt import Lamp


from PyQt5 import uic, QtWidgets
from pydevmgr_core_qt import  (Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar
from pydevmgr_elt_qt.io import find_ui
import pydevmgr_elt_qt.device.line as base 

Base = base.EltDeviceLine
Device = Lamp


class ActionMenuName(str, Enum):
    ON = "ON"
    OFF = "OFF"
    # more action menu related to the device 

##############################################################

class Widget(base.Widget):
    time_left: QLabel
    input_intensity: QLineEdit
    input_time: QLineEdit

    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('lamp_line_frame.ui'), self) 

class Proc(base.Proc):
    time_setter   = get_setter_class(QtWidgets.QLabel, float)(format="%.0f")
    intensity_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.1f")
   

class Data(base.Data):
    class Stat(base.Data.Stat):
        time_left: NodeVar[float] = 0.0
        intensity: NodeVar[float] = 0.0
    
    stat: Stat = Stat()


@dataclass
class Args(base.Args):
    time: Callable = None

@dataclass
class Actions(base.Actions):
    ...

##############################################################  


        
def set_widget(widget: Widget, device: Device) -> None:
    base.set_widget(widget, device)
     
    Proc.intensity_setter.set(widget.input_intensity, 1.0)
    Proc.time_setter.set(widget.input_time, 10.0)    
    wa = widget.state_action
    wa.insertSeparator(wa.count()) 
    wa.addItems( ActionMenuName )

def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    s = data.stat
    Proc.time_setter.set( w.time_left, s.time_left)
   

def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)
    args.intensity = lambda: Proc.float_getter.get(widget.input_intensity)
    args.time = lambda: Proc.float_getter.get(widget.input_time)


def set_actions(actions: Actions, device: Device, args: Args)-> Actions:
    base.set_actions(actions, device, args)
    feedback = args.feedback
    command = actions.command
    command.add_action( ActionMenuName.ON, Action(device.switch_on, [args.intensity, args.time], feedback))
    command.add_action( ActionMenuName.OFF, Action(device.switch_off, [], feedback))
 
    
connect_action = base.connect_action 
disconnect_action = base.disconnect_action 


##############################################################  

@record_qt(Lamp, "line")
class LampLine(Base):
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


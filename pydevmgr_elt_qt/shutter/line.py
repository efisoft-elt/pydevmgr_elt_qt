# use this file has a template to build line widget

from dataclasses import dataclass
from enum import Enum
from typing import Callable
from PyQt5.QtWidgets import QFrame

from pydevmgr_elt import Shutter
from pydevmgr_elt_qt.io import find_ui

from PyQt5 import uic
from pydevmgr_core_qt import  (Action, record_qt)
import pydevmgr_elt_qt.device.line as base 

Base = base.EltDeviceLine

Device = Shutter


class ActionMenuName(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"

    
class Widget(base.Widget):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('shutter_line_frame.ui'), self) 


Proc = base.Proc
Data = base.Data
Args = base.Args
Actions = base.Actions
#################################################3

def set_widget(widget: Widget, device: Shutter) -> None:
    base.set_widget(widget, device)
    wa = widget.state_action
    wa.insertSeparator( wa.count())
    wa.addItems( ActionMenuName )

update_data = base.update_data
set_args = base.set_args


def set_actions(actions: Actions, device: Shutter, args: Args)-> Actions:
    base.set_actions(actions, device, args)
    feedback = args.feedback
    command = actions.command
    command.add_action( ActionMenuName.OPEN, Action(device.open, [], feedback)) 
    command.add_action( ActionMenuName.CLOSE, Action(device.close, [], feedback)) 

connect_action = base.connect_action 
disconnect_action = base.disconnect_action 

##############################################################  

@record_qt(Shutter, "line")
class ShutterLine(Base):
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


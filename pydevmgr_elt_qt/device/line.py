# use this file has a template to build line widget

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable, Tuple
from PyQt5.QtWidgets import QCheckBox, QComboBox, QFrame, QLabel
from pydantic.main import BaseModel
from pydevmgr_elt import EltDevice

from PyQt5 import uic, QtWidgets
from pydevmgr_core_qt import  (ActionMap, BaseFeedback, Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.base.device as base

Base = base.QtBase
Device = EltDevice


class ActionMenuName(str, Enum):
    ...
    # more action menu related to the device 

@dataclass
class MenuErrorFeedback:
    widget: QComboBox
    def error(self,  err: Exception):
        self.widget.setItemText(0, "!!ERROR!!")
    def clear(self,  msg: str):
        self.widget.setItemText(0, "")

    
class Widget(Base.Widget):
    substate: QLabel
    state_action: QComboBox
    check: QCheckBox
    
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(base.find_ui('devie_line_frame.ui'), self) 

class Proc(base.Proc):
    pos_setter =   get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")

class Data(base.Data):
    class Stat(BaseModel):
        substate_info: NodeVar[Tuple] = (0,'','')
        
    stat: Stat = Stat()
    is_ignored: NodeVar[bool] = False
    

@dataclass
class Args:
    feedback:  BaseFeedback = None
    reset : Callable = None
    is_ignored: Callable = None 


@dataclass
class Actions:
    command: ActionMap = None
    check: Action = None


##############################################################  

def set_widget(widget: Widget, device: Device) -> None:
    base.set_widget( widget, device)

    wa = widget.state_action
    wa.addItems( e.name for e in ActionMenuName )
    Proc.text_setter.set(widget.name, device.name)



def update_data( w: Widget, data: Data) -> None:
    base.update_data(w, data)
    Proc.code_text_setter.set(w.substate, data.stat.substate_info)   

    

def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)

    args.feedback = MenuErrorFeedback(widget.state_action)
    args.reset = lambda: widget.state_action.setCurrentIndex(0)
    args.is_ignored = lambda: not widget.check.isChecked()


def set_actions(actions: Actions, device: Device, args: Args)-> Actions:
    base.set_actions(actions, device, args)
    
    feedback = args.feedback
    command_actions = dict(
        INIT = Action(device.init,       [], feedback), 
        ENABLE = Action(device.enable,   [], feedback), 
        DISABLE = Action(device.disable, [], feedback), 
        RESET = Action(device.reset,     [], feedback)
    )

    actions.command = ActionMap(command_actions, after=args.reset)
    actions.check = Action(device.is_ignored.set, [args.is_ignored]) 

def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    
    Proc.menu_connector.connect(widget.state_action, actions.command)
    Proc.check_connector.connect(widget.check, actions.check)
    

def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)
    Proc.menu_connector.disconnect(widget.state_action)
    Proc.check_connector.disconnect(widget.check)


##############################################################  


# @record_qt(Device, "ctrl")
class EltDeviceLine(Base):
    Widget = Widget
   
    class Monitor(Base.Monitor):
        Data = Data
        _update_data = staticmethod(update_data)
        
        show_ignore_check_box: bool = True 

        def update(self, widget: Widget, data: Data)-> None:
            super().update(widget, data)
            if self.show_ignore_check_box:
                if widget.check.isChecked() == data.is_ignored:             
                    widget.check.setChecked(not data.is_ignored)    

    class Connector(Base.Connector):
        Args = Args
        Actions = Actions

        _set_widget        = staticmethod(set_widget)
        _set_args          = staticmethod(set_args)
        _set_actions       = staticmethod(set_actions)
        _connect_action    = staticmethod(connect_action)
        _disconnect_action = staticmethod(disconnect_action)
        




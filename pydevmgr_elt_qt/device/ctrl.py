from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable, Tuple
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydantic.main import BaseModel
from pydevmgr_core_ui.feedback import BaseFeedback
from pydevmgr_core_ui.getter import get_getter_class

from pydevmgr_elt import EltDevice
from PyQt5 import uic, QtWidgets
from pydevmgr_core_qt import  (ActionMap, QtTextFeedback,  Action, get_setter_class, record_qt) 
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.base.device as base

Base = base.QtBase 
Device = EltDevice

class Proc(base.Proc):
    pos_setter   = get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")


class Widget(base.Widget):
    #  e.g.  pos_actual: QLabel
    state: QLabel 
    substate: QLabel
    error_txt: QLabel
    name: QLabel
    state_action: QComboBox
    rpc_feedback: QLabel

    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(base.find_ui('device_ctrl_frame.ui'), self) 

 

NT, D = NodeVar[Tuple[int,str,str]],  (0,'','')
class Data(base.Data):
    class Stat(BaseModel):
        state_info: NT    = D
        substate_info: NT = D
        error_info: NT    = D
    
    stat: Stat = Stat()
    is_ignored: NodeVar[bool] = False
del NT, D

@dataclass
class Args(base.Args):
    # e.g. pos_target: Callable
    feedback: BaseFeedback = None # handle any action rrors   
    reset: Callable = None
    is_ignored: Callable = None 

@dataclass
class Actions(base.Actions):
    command: ActionMap = None
    check: Action = None


##################################################################

def update_data(w: Widget, data: Data):
    base.update_data(w,data)
    s = data.stat 
    Proc.code_text_setter.set( w.state, s.state_info)
    Proc.code_text_setter.set( w.substate, s.substate_info)
    Proc.code_text_setter.set( w.error_txt, s.error_info)

def set_widget(widget: Widget, device: Device):
    base.set_widget(widget, device)
    wa = widget.state_action
    wa.clear()
    wa.addItems( ["", "INIT", "ENABLE", "DISABLE", "RESET"] )
    Proc.text_setter.set(widget.name, device.name)

def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)
    args.feedback = QtTextFeedback( widget.rpc_feedback )
    args.reset = lambda: widget.state_action.setCurrentIndex(0)
    args.is_ignored = lambda: not widget.check.isChecked()

def set_actions(actions: Actions, device: Device, args: Args)-> Actions:
    base.set_actions(actions, device, args)
    feedback = args.feedback
    
    actions.command = ActionMap(
            dict(
                INIT    = Action(device.init,    [], feedback), 
                ENABLE  = Action(device.enable,  [], feedback),
                DISABLE = Action(device.disable, [], feedback), 
                RESET   = Action(device.reset,   [], feedback)
            ), after=args.reset)
    actions.check = Action(device.is_ignored.set, [args.is_ignored]) 

def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    
    Proc.menu_connector.connect(widget.state_action, actions.command)
    Proc.check_connector.connect(widget.check, actions.check)
    
def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)
    
    Proc.menu_connector.disconnect(widget.state_action)
    Proc.check_connector.disconnect(widget.check)
       

######################################################################


# @record_qt(Device, "ctrl")
class EltDeviceCtrl(Base):
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
        



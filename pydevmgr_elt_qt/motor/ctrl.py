from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydevmgr_core_ui.feedback import BaseFeedback
from pydevmgr_core_ui.getter import get_getter_class

from pydevmgr_elt import Motor
from PyQt5 import uic, QtWidgets
from ..io import find_ui
from pydevmgr_core_qt import  (ActionMap, QtTextFeedback,  Action, get_setter_class, record_qt) 
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.ctrl as base 



Base = base.EltDeviceCtrl
Device = Motor

class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2


class Widget(base.Widget):
    pos_actual: QLabel
    pos_error: QLabel
    pos_name: QLabel
    pos_target: QLabel
    vel_actual: QLabel
    input_pos_target: QLineEdit
    input_velocity: QLineEdit
    move_mode: QComboBox
    move: QPushButton
    stop: QPushButton
    move_by_posname: QComboBox
    
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('motor_ctrl_frame.ui'), self) 

class Proc(base.Proc):
    move_mode_getter = get_getter_class( QComboBox, Enum)(MOVE_MODE)
   

class Data(base.Data):
    class Stat(base.Data.Stat):
        pos_actual: NodeVar[float] = 0.0
        pos_error:  NodeVar[float] = 0.0
        pos_name:   NodeVar[str] =   "" 
        pos_target: NodeVar[float] = 0.0
        vel_actual: NodeVar[float] = 0.0
    stat: Stat = Stat()


@dataclass
class Args(base.Args):
    pos_target: Callable = None
    velocity:   Callable  = None
    move_mode:  Callable = None
    
    feedback: BaseFeedback = None # handle any action rrors   
    reset_posname: Callable = None


@dataclass
class Actions(base.Actions):
    stop: Action = None
    move: Action = None 
    move_posname: ActionMap = None 




##################################################################


def set_widget(widget: Widget, motor: Motor):
    base.set_widget(widget, motor)

    if motor.is_connected():
        Proc.float_setter.set(widget.input_pos_target,motor.stat.pos_actual.get()) 
    else:
        Proc.float_setter.set(widget.input_pos_target, 0.0)
    Proc.float_setter.set(widget.input_velocity, motor.ctrl_config.velocity)
            
    widget.move_mode.clear()
    for a in MOVE_MODE:
        widget.move_mode.addItem(a.name)
    
    widget.move_by_posname.addItem("")
    for posname in motor.posnames:
        widget.move_by_posname.addItem(posname)


def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    s = data.stat
    Proc.pos_setter.set(w.pos_actual, s.pos_actual)
    Proc.error_setter.set(w.pos_error, s.pos_error)
    Proc.text_setter.set(w.posname, s.pos_name)
    Proc.pos_setter.set(w.pos_target, s.pos_target)
    Proc.pos_setter.set(w.vel_actual, s.vel_actual)

def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)

    args.pos_target = lambda: Proc.float_getter.get(widget.input_pos_target) 
    args.velocity =  lambda: Proc.float_getter.get(widget.input_velocity) 
    args.move_mode = lambda: Proc.move_mode_getter.get(widget.move_mode) 
    args.feedback= QtTextFeedback( widget.rpc_feedback ) 
    args.reset_posname = lambda: widget.move_by_posname.setCurrentIndex(0)


def set_actions(actions: Actions, motor: Motor, args: Args)-> Actions:
    base.set_actions(actions, motor, args)
    

    feedback = args.feedback
    
    def move(mode, pos, vel):
        if mode == MOVE_MODE.ABSOLUTE:
            motor.move_abs(pos, vel)
        elif mode == MOVE_MODE.RELATIVE:
            motor.move_rel(pos, vel)
        elif mode == MOVE_MODE.VELOCITY:
            motor.move_vel(vel)
    
    move_posname = ActionMap(after=args.reset_posname)
    for posname in motor.posnames:
        move_posname.add_action(
                posname,
                Action(motor.move_name, [posname, args.velocity], feedback),
            )
     
    actions.stop = Action(motor.stop, [], feedback)
    actions.move = Action(move, [args.move_mode, args.pos_target, args.velocity], feedback)
    actions.move_posname = move_posname


def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    Proc.button_connector.connect( widget.move, actions.move)
    Proc.button_connector.connect( widget.stop, actions.stop)
    Proc.menu_connector.connect(widget.move_by_posname, actions.move_posname) 
   
def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)
    Proc.button_connector.disconnect( widget.stop )
    Proc.button_connector.disconnect( widget.move )
    Proc.menu_connector.disconnect(widget.move_by_posname)


######################################################################


@record_qt(Motor, "ctrl")
class MotorCtrl(Base):
    Widget = Widget
        
    class Monitor(Base.Monitor):
        Data = Data
        _update_data = staticmethod(update_data)

        def update(self, widget, data):
            # super is updating all data with a widget link defined
            super().update(widget, data)
            if widget.move_mode.currentIndex()==MOVE_MODE.VELOCITY:
                widget.input_pos_target.setEnabled(False)
            else:
                widget.input_pos_target.setEnabled(True)


    class Connector(Base.Connector):
        Args = Args
        Actions = Actions
       
        _set_widget        = staticmethod(set_widget)
        _set_args          = staticmethod(set_args)
        _set_actions       = staticmethod(set_actions)
        _connect_action    = staticmethod(connect_action)
        _disconnect_action = staticmethod(disconnect_action)

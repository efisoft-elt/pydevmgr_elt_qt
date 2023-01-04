from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydevmgr_core_ui.feedback import BaseFeedback
from pydevmgr_core_ui.getter import get_getter_class

from pydevmgr_elt import Drot
from PyQt5 import uic, QtWidgets
from ..io import find_ui
from pydevmgr_core_qt import (ActionMap, QtTextFeedback,  Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.ctrl as base 



Base = base.EltDeviceCtrl
Device = Drot



class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class TRACK_MODE(IntEnum):
    SKY = 2
    ELEV = 3
    USER = 4

##############################################################  

class Widget(base.Widget):
    pos_actual: QLabel
    pos_error: QLabel
    pos_name: QLabel
    pos_target: QLabel
    vel_actual: QLabel
    angle_on_sky: QLabel
    track_mode_txt: QLabel
    
    input_pos_target: QLineEdit
    input_velocity: QLineEdit
    move_mode: QComboBox
    track_mode: QComboBox
    move: QPushButton
    stop: QPushButton
    move_by_posname: QComboBox
    
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('drot_ctrl_frame.ui'), self) 

class Proc(base.Proc):
    move_mode_getter = get_getter_class( QComboBox, Enum)(MOVE_MODE)
    track_mode_getter = get_getter_class( QComboBox, Enum)(TRACK_MODE)


class Data(base.Data):
    class Stat(base.Data.Stat):
        track_mode_txt: NodeVar[str] = ""
            
        pos_actual: NodeVar[float] = 0.0
        pos_error:  NodeVar[float] = 0.0
        pos_target: NodeVar[float] = 0.0
        vel_actual: NodeVar[float] = 0.0
        angle_on_sky: NodeVar[float] = 0.0

    stat: Stat = Stat()


@dataclass
class Args(base.Args):
    pos_target: Callable = None
    velocity: Callable  = None
    move_mode: Callable = None
    input_angle: Callable = None
    track_mode: Callable  = None

@dataclass
class Actions(base.Actions):
    stop: Action = None
    move: Action = None
    move_angle: Action = None
    start_track: Action = None
    stop_track: Action = None



##################################################################

def set_widget( widget: Widget, drot: Drot) -> None:
    base.set_widget(widget, drot)

    if drot.is_connected():
        Proc.float_setter.set(widget.input_pos_target,drot.stat.pos_actual.get()) 
    else:
        Proc.float_setter.set(widget.input_pos_target, 0.0)
    Proc.float_setter.set(widget.input_velocity, drot.ctrl_config.velocity)
    Proc.float_setter.set(widget.input_angle, 0.0)
            
    widget.move_mode.clear()
    widget.move_mode.addItems( a.name for a in MOVE_MODE )
    
    widget.track_mode.clear()
    widget.track_mode.addItems( a.name for a in TRACK_MODE)
    

def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    s = data.stat
    Proc.text_setter.set( w.track_mode_txt, s.track_mode_txt)
    
    Proc.pos_setter.set(w.pos_actual, s.pos_actual)
    Proc.error_setter.set(w.pos_error, s.pos_error)
    Proc.pos_setter.set(w.pos_target, s.pos_target)
    Proc.pos_setter.set(w.vel_actual, s.vel_actual)
    Proc.pos_setter.set(w.angle_on_sky, s.angle_on_sky)


def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)
    args.pos_target = lambda: Proc.float_getter.get(widget.input_pos_target) 
    args.velocity =  lambda: Proc.float_getter.get(widget.input_velocity) 
    args.move_mode = lambda: Proc.move_mode_getter.get(widget.move_mode) 
    args.input_angle = lambda: Proc.float_getter.get(widget.input_angle)
    args.track_mode = lambda: Proc.track_mode_getter.get(widget.track_mode)
   
def set_actions(actions: Actions, drot: Drot, args: Args)-> Actions:
    base.set_actions(actions, drot, args)
    feedback = args.feedback
    
    def move(mode, pos, vel):
        if mode == MOVE_MODE.ABSOLUTE:
            drot.move_abs(pos, vel)
        elif mode == MOVE_MODE.RELATIVE:
            drot.move_rel(pos, vel)
        elif mode == MOVE_MODE.VELOCITY:
            drot.move_vel(vel)

    actions.stop = Action(drot.stop, [], feedback)
    actions.move = Action(move, [args.move_mode, args.pos_target, args.velocity], feedback) 
    actions.start_track = Action( drot.start_track, [args.track_mode, args.input_angle], feedback)
    actions.stop_track = Action( drot.stop_track, [], feedback) 
    actions.move_angle = Action( drot.move_angle, [args.input_angle], feedback)



def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)

    Proc.button_connector.connect( widget.move, actions.move)
    Proc.button_connector.connect( widget.stop, actions.stop)
    Proc.button_connector.connect( widget.move_angle, actions.move_angle)
    Proc.button_connector.connect( widget.stop_track, actions.stop_track)
    Proc.button_connector.connect( widget.start_track, actions.start_track)
    

def disconnect_action(widget: Widget) -> None:
    Proc.button_connector.disconnect( widget.stop )
    Proc.button_connector.disconnect( widget.move )
    Proc.button_connector.disconnect( widget.stop_track)
    Proc.button_connector.disconnect( widget.start_track)


##############################################################################

@record_qt(Drot, "ctrl")
class DrotCtrl(Base):
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




from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydantic.main import BaseModel
from pydevmgr_core_ui.feedback import BaseFeedback
from pydevmgr_core_ui.getter import get_getter_class

from pydevmgr_elt import Drot
from .elt_device_ctrl import EltDeviceCtrl
from PyQt5 import uic, QtWidgets
from .io import find_ui
from pydevmgr_core_qt import (ActionMap, QtTextFeedback,  Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 
from pydantic import Field

Base = EltDeviceCtrl


class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class TRACK_MODE(IntEnum):
    SKY = 2
    ELEV = 3
    USER = 4

class DrotCtrlWidget(Base.Widget):
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

class Proc(Base.Proc):
    pos_setter   = get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")
    text_setter  = get_setter_class(QtWidgets.QLabel, str)()
    move_mode_getter = get_getter_class( QComboBox, Enum)(MOVE_MODE)
    track_mode_getter = get_getter_class( QComboBox, Enum)(TRACK_MODE)


class DrotCtrlData(Base.Monitor.Data):
    class Stat(Base.Monitor.Data.Stat):
        track_mode_txt: NodeVar[str] = ""
            
        pos_actual: NodeVar[float] = 0.0
        pos_error:  NodeVar[float] = 0.0
        pos_target: NodeVar[float] = 0.0
        vel_actual: NodeVar[float] = 0.0
        angle_on_sky: NodeVar[float] = 0.0

    stat: Stat = Stat()


class DrotCtrlSetter(Base.Monitor.DataSetter):
    def set(self, w, data):
        super().set(w, data)
        s = data.stat
        Proc.text_setter.set( w.track_mode_txt, s.track_mode_txt)
        
        Proc.pos_setter.set(w.pos_actual, s.pos_actual)
        Proc.error_setter.set(w.pos_error, s.pos_error)
        Proc.pos_setter.set(w.pos_target, s.pos_target)
        Proc.pos_setter.set(w.vel_actual, s.vel_actual)
        Proc.pos_setter.set(w.angle_on_sky, s.angle_on_sky)


@dataclass
class DrotCtrlArgs:
    pos_target: Callable
    velocity: Callable 
    move_mode: Callable
    input_angle: Callable
    track_mode: Callable 
    feedback: BaseFeedback # handle any action rrors   
    reset_posname: Callable

def drot_ctrl_args(widget)-> DrotCtrlArgs:
    return DrotCtrlArgs( 
        pos_target = lambda: Proc.float_getter.get(widget.input_pos_target), 
        velocity =  lambda: Proc.float_getter.get(widget.input_velocity), 
        move_mode = lambda: Proc.move_mode_getter.get(widget.move_mode), 
        input_angle = lambda: Proc.float_getter.get(widget.input_angle),
        track_mode = lambda: Proc.track_mode_getter.get(widget.track_mode),

        feedback= QtTextFeedback( widget.rpc_feedback ), 
        reset_posname = lambda: widget.move_by_posname.setCurrentIndex(0)
    )


@dataclass
class DrotCtrlActions:
    stop: Action
    move: Action
    move_angle: Action
    start_track: Action
    stop_track: Action


def drot_ctrl_actions(drot, args: DrotCtrlArgs)-> DrotCtrlActions:
    feedback = args.feedback
    
    def move(mode, pos, vel):
        if mode == MOVE_MODE.ABSOLUTE:
            drot.move_abs(pos, vel)
        elif mode == MOVE_MODE.RELATIVE:
            drot.move_rel(pos, vel)
        elif mode == MOVE_MODE.VELOCITY:
            drot.move_vel(vel)
    
    move_posname = ActionMap(after=args.reset_posname)
    for posname in drot.posnames:
        move_posname.add_action(
                posname,
                Action(drot.move_name, [posname, args.velocity], feedback),
            )
    
    return DrotCtrlActions(
        stop = Action(drot.stop, [], feedback),
        move = Action(move, [args.move_mode, args.pos_target, args.velocity], feedback), 
        start_track = Action( drot.start_track, [args.track_mode, args.input_angle], feedback),
        stop_track = Action( drot.stop_track, [], feedback), 
        move_angle = Action( drot.move_angle, [args.input_angle], feedback)
    )

def set_drot_ctrl_widget( widget, drot):
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
    


def drot_ctrl_connect(widget, drot):
    set_drot_ctrl_widget(widget, drot)
    args = drot_ctrl_args(widget)
    actions = drot_ctrl_actions(drot, args)
    
    Proc.button_connector.connect( widget.move, actions.move)https://en.wikipedia.org/wiki/Incremental_encoder
    Proc.button_connector.connect( widget.stop, actions.stop)
    Proc.button_connector.connect( widget.move_angle, actions.move_angle)

    Proc.button_connector.connect( widget.stop_track, actions.stop_track)
    Proc.button_connector.connect( widget.start_track, actions.start_track)
    
    widget.drot_ctrl_actions = actions # need to be saved (weakref)

def drot_ctrl_disconnect(widget):
    Proc.button_connector.disconnect( widget.stop )
    Proc.button_connector.disconnect( widget.move )
    Proc.button_connector.disconnect( widget.stop_track)
    Proc.button_connector.disconnect( widget.start_track)




@record_qt(Drot, "ctrl")
class DrotCtrl(Base):
    Proc = Proc
    Widget = DrotCtrlWidget
        
    class Monitor(Base.Monitor):
        Data = DrotCtrlData
        DataSetter = DrotCtrlSetter
        data_setter = DataSetter()             
        
        def update(self, widget, data):
            # super is updating all data with a widget link defined
            super().update(widget, data)
            if widget.move_mode.currentIndex()==MOVE_MODE.VELOCITY:
                widget.input_pos_target.setEnabled(False)
            else:
                widget.input_pos_target.setEnabled(True)


    class Connector(Base.Connector):

        def connect(self, widget, drot):
            super().connect(widget, drot)
            drot_ctrl_connect(widget, drot) 

        def disconnect(self, widget):
            super().disconnect(widget)
            drot_ctrl_disconnect(widget)


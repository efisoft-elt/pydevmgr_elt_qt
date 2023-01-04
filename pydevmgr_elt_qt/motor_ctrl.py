from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydantic.main import BaseModel
from pydevmgr_core_ui.feedback import BaseFeedback
from pydevmgr_core_ui.getter import get_getter_class
from pydevmgr_core_ui.setter import UiInterfaces, DataToWidgetSetter

from pydevmgr_elt import Motor
from .elt_device_ctrl import EltDeviceCtrl
from PyQt5 import uic, QtWidgets
from .io import find_ui
from pydevmgr_core_qt import  (ActionMap, QtTextFeedback,  Action, get_setter_class, record_qt, QtInterface) 
from pydevmgr_core import NodeVar 
from pydantic import Field

Base = EltDeviceCtrl


class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2


class MotorCtrlWidget(Base.Widget):
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

class Proc(Base.Proc):
    pos_setter   = get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")
    text_setter  = get_setter_class(QtWidgets.QLabel, str)()
    move_mode_getter = get_getter_class( QComboBox, Enum)(MOVE_MODE)
   

class MotorCtrlData(Base.Monitor.Data):
    class Stat(Base.Monitor.Data.Stat):
        pos_actual: NodeVar[float] = 0.0
        pos_error:  NodeVar[float] = 0.0
        pos_name:   NodeVar[str] =   "" 
        pos_target: NodeVar[float] = 0.0
        vel_actual: NodeVar[float] = 0.0
    stat: Stat = Stat()

class MotorCtrlSetter(Base.Monitor.DataSetter): 
    def set(self, w, data):
        super().set(w, data)
        s = data.stat
        Proc.pos_setter.set(w.pos_actual, s.pos_actual)
        Proc.error_setter.set(w.pos_error, s.pos_error)
        Proc.text_setter.set(w.posname, s.pos_name)
        Proc.pos_setter.set(w.pos_target, s.pos_target)
        Proc.pos_setter.set(w.vel_actual, s.vel_actual)
        

@dataclass
class MotorCtrlArgs:
    pos_target: Callable
    velocity: Callable 
    move_mode: Callable
    
    feedback: BaseFeedback # handle any action rrors   
    reset_posname: Callable


@dataclass
class MotorCtrlActions:
    stop: Action
    move: Action 
    move_posname: ActionMap 


def motor_ctrl_args(widget)-> MotorCtrlArgs:
    return MotorCtrlArgs( 
        pos_target = lambda: Proc.float_getter.get(widget.input_pos_target), 
        velocity =  lambda: Proc.float_getter.get(widget.input_velocity), 
        move_mode = lambda: Proc.move_mode_getter.get(widget.move_mode), 

        feedback= QtTextFeedback( widget.rpc_feedback ), 
        reset_posname = lambda: widget.move_by_posname.setCurrentIndex(0)
    )

def motor_ctrl_actions(motor, args: MotorCtrlArgs)-> MotorCtrlActions:
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
    
    return MotorCtrlActions(
        stop = Action(motor.stop, [], feedback),
        move = Action(move, [args.move_mode, args.pos_target, args.velocity], feedback), 
        move_posname = move_posname
    )

def set_motor_ctrl_widget( widget, motor):
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

def motor_ctrl_connect(widget, motor):
    set_motor_ctrl_widget(widget, motor)
    args = motor_ctrl_args(widget)
    actions = motor_ctrl_actions(motor, args)
    
    Proc.button_connector.connect( widget.move, actions.move)
    Proc.button_connector.connect( widget.stop, actions.stop)
    Proc.menu_connector.connect(widget.move_by_posname, actions.move_posname) 
    widget.motor_actions = actions # need to be saved (weakref)

def motor_ctrl_disconnect(widget):
    Proc.button_connector.disconnect( widget.stop )
    Proc.button_connector.disconnect( widget.move )
    Proc.menu_connector.disconnect(widget.move_by_posname)



@record_qt(Motor, "ctrl")
class MotorCtrl(Base):
    Proc = Proc
    Widget = MotorCtrlWidget
        
    class Monitor(Base.Monitor):
        Data = MotorCtrlData
        DataSetter = MotorCtrlSetter
        data_setter = DataSetter()            
        
        def update(self, widget, data):
            # super is updating all data with a widget link defined
            super().update(widget, data)
            if widget.move_mode.currentIndex()==MOVE_MODE.VELOCITY:
                widget.input_pos_target.setEnabled(False)
            else:
                widget.input_pos_target.setEnabled(True)


    class Connector(Base.Connector):

        def connect(self, widget, motor):
            super().connect(widget, motor)
            motor_ctrl_connect(widget, motor) 

        def disconnect(self, widget):
            super().disconnect(widget)
            motor_ctrl_disconnect(widget)


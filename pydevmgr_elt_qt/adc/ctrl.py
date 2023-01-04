from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton, QWidget
from pydantic import  BaseModel
from pydevmgr_core_ui import BaseFeedback, get_getter_class
from pydevmgr_elt import  Adc
from PyQt5 import uic, QtWidgets
from pydevmgr_elt_qt.io import find_ui
from pydevmgr_core_qt import  (QtTextFeedback,  Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.ctrl as base 


Base = base.EltDeviceCtrl
Device = Adc


class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2
    
class AXES(IntEnum):
    BOTH = 0
    AXIS1 = 1
    AXIS2 = 2

class Widget(base.Widget):
    adc_ctrl_actions: "Actions" = None
    motor1_pos_actual: QLabel
    motor1_pos_error: QLabel
    motor1_pos_target: QLabel
    motor1_vel_actual: QLabel

    motor2_pos_actual: QLabel
    motor2_pos_error: QLabel
    motor2_pos_target: QLabel
    motor2_vel_actual: QLabel
    
    track_mode_txt: QLabel
    rpc_feedback: QLabel

    input_axis: QComboBox
    input_pos_target: QLineEdit
    input_velocity: QLineEdit
    mode: QComboBox
    input_angle: QLineEdit
    
    stop: QPushButton
    start_track: QPushButton
    stop_track: QPushButton
    move: QPushButton
    move_angle: QPushButton
   
    
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('adc_ctrl_frame.ui'), self) 

class Proc(Base.Proc):
    pos_setter =   get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")
    text_setter  = get_setter_class(QtWidgets.QLabel, str)()
    axis_getter = get_getter_class( QComboBox, Enum)(AXES)
    move_mode_getter = get_getter_class( QComboBox, Enum)(MOVE_MODE)



class Data(base.Data):
    class Stat(base.Data.Stat):
        track_mode_txt : NodeVar[str] = ""
    
    class Motor1Data(BaseModel):
        class Stat(BaseModel):
            pos_actual: NodeVar[float] = 0.0 
            pos_error:  NodeVar[float] = 0.0 
            pos_target: NodeVar[float] = 0.0 
            vel_actual: NodeVar[float] = 0.0 

        stat: Stat = Stat()
    class Motor2Data(BaseModel):
        class Stat(BaseModel):
            pos_actual: NodeVar[float] = 0.0 
            pos_error:  NodeVar[float] = 0.0 
            pos_target: NodeVar[float] = 0.0 
            vel_actual: NodeVar[float] = 0.0 

        stat: Stat = Stat()
    #--------------------------------
    stat: Stat = Stat()
    motor1: Motor1Data = Motor2Data()
    motor2: Motor2Data = Motor2Data()
# ------------------------------------


@dataclass
class Args(base.Args):
    axis: Callable = None
    pos_target: Callable = None
    velocity: Callable = None
    mode: Callable = None
    input_angle: Callable = None
    feedback: BaseFeedback = None
    


@dataclass
class Actions(base.Actions):
    stop: Action = None
    start_track: Action = None
    stop_track: Action = None
    move: Action = None
    move_angle: Action  = None





##################################################################
        
def set_widget(widget: Widget, adc: Adc) -> None:
    base.set_widget(widget, adc) 
    if adc.is_connected():
        Proc.float_setter.set(widget.input_velocity, adc.motor1.cfg.velocity.get())
    else:
        Proc.float_setter.set(widget.input_velocity, adc.motor1.config.ctrl_config.velocity)
    
    for m in MOVE_MODE:
        widget.move_mode.addItem(m.name) 
    for a in AXES:
        widget.input_axis.addItem(a.name)
        
    widget.input_pos_target.setText("0.0")
    widget.input_angle.setText("0.0")


def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    Proc.text_setter.set( w.track_mode_txt, data.stat.track_mode_txt)
    
    s = data.motor1.stat
    Proc.pos_setter.set(w.motor1_pos_actual, s.pos_actual)
    Proc.error_setter.set(w.motor1_pos_error, s.pos_error)
    Proc.pos_setter.set(w.motor1_pos_target, s.pos_target)
    Proc.pos_setter.set(w.motor1_vel_actual, s.vel_actual)
    
    s = data.motor2.stat
    Proc.pos_setter.set(w.motor2_pos_actual, s.pos_actual)
    Proc.error_setter.set(w.motor2_pos_error, s.pos_error)
    Proc.pos_setter.set(w.motor2_pos_target, s.pos_target)
    Proc.pos_setter.set(w.motor2_vel_actual, s.vel_actual)


def set_args(args: Args, widget: Widget)-> Args:
    base.set_args(args, widget)
    args.axis = lambda: Proc.axis_getter.get( widget.input_axis)
    args.pos_target = lambda: Proc.float_getter.get( widget.input_pos_target)
    args.velocity = lambda: Proc.float_getter.get( widget.input_velocity)
    args.mode = lambda: Proc.move_mode_getter.get(widget.move_mode)
    args.input_angle = lambda:  Proc.float_getter.get(widget.input_angle)
    args.feedback = QtTextFeedback( widget.rpc_feedback )

def set_actions(actions: Actions, adc: Adc, args: Args)-> Actions:
    base.set_actions(actions, adc, args)

    feedback = args.feedback
    def move(mode, axis, pos, vel):
        if mode == MOVE_MODE.ABSOLUTE:
            adc.move_abs(axis, pos, vel)
        elif mode == MOVE_MODE.RELATIVE:
            adc.move_rel(axis, pos, vel)
        elif mode == MOVE_MODE.VELOCITY:
            adc.move_vel(axis, vel)

    actions.stop = Action( adc.stop, [], feedback)
    actions.start_track = Action( adc.start_track, [args.input_angle], feedback)
    actions.stop_track = Action( adc.stop_track, [], feedback)
    actions.move = Action(move, 
                         [args.mode, args.axis, args.pos_target, args.velocity], 
                        feedback 
                )
    actions.move_angle = Action( adc.move_angle, [args.input_angle], feedback)



def connect(widget: Widget, adc: Adc):
    set_widget(widget, adc)

def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    Proc.button_connector.connect( widget.stop, actions.stop)
    Proc.button_connector.connect( widget.start_track, actions.start_track)
    Proc.button_connector.connect( widget.stop_track, actions.stop_track)
    Proc.button_connector.connect( widget.move, actions.move)
    Proc.button_connector.connect( widget.move_angle, actions.move_angle) 

def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)
    Proc.button_connector.disconnect( widget.stop)
    Proc.button_connector.disconnect( widget.start_track)
    Proc.button_connector.disconnect( widget.stop_track)
    Proc.button_connector.disconnect( widget.move)
    Proc.button_connector.disconnect( widget.move_angle) 


####################################################################################

@record_qt(Adc, "ctrl")
class AdcCtrl(Base):
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

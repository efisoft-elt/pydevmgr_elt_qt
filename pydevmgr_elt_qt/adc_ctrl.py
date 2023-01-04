from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton, QWidget
from pydantic import Field, BaseModel
from pydevmgr_core_ui import BaseFeedback, get_getter_class
from pydevmgr_elt import  Adc
from .elt_device_ctrl import EltDeviceCtrl 
from PyQt5 import uic, QtWidgets
from .io import find_ui
from pydevmgr_core_qt import  (QtTextFeedback,  Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 

Base = EltDeviceCtrl

class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2
    
class AXES(IntEnum):
    BOTH = 0
    AXIS1 = 1
    AXIS2 = 2

class AdcCtrlWidget(Base.Widget):
    adc_ctrl_actions: "AdcCtrlActions" = None
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




class AdcCtrlData(Base.Monitor.Data):
    class Stat(Base.Monitor.Data.Stat):
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


class AdcCtrlSetter(Base.Monitor.DataSetter):
    def set(self, w, data):
        super().set(w, data)
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

        

def set_adc_ctrl_widget(widget, adc):
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

@dataclass
class AdcCtrlArgs:
    axis: Callable
    pos_target: Callable
    velocity: Callable
    mode: Callable
    input_angle: Callable
    feedback: BaseFeedback
    

def adc_ctrl_args( widget ) -> AdcCtrlArgs:
    return AdcCtrlArgs(
        axis = lambda: Proc.axis_getter.get( widget.input_axis),
        pos_target = lambda: Proc.float_getter.get( widget.input_pos_target),
        velocity = lambda: Proc.float_getter.get( widget.input_velocity),
        mode = lambda: Proc.move_mode_getter.get(widget.move_mode),
        input_angle = lambda:  Proc.float_getter.get(widget.input_angle), 
        feedback = QtTextFeedback( widget.rpc_feedback )

    )


@dataclass
class AdcCtrlActions:
    stop: Action
    start_track: Action
    stop_track: Action
    move: Action
    move_angle: Action 

     
def adc_ctrl_actions(adc, args: AdcCtrlArgs) -> AdcCtrlActions:
    feedback = args.feedback
    
    def move(mode, axis, pos, vel):
            if mode == MOVE_MODE.ABSOLUTE:
                adc.move_abs(axis, pos, vel)
            elif mode == MOVE_MODE.RELATIVE:
                adc.move_rel(axis, pos, vel)
            elif mode == MOVE_MODE.VELOCITY:
                adc.move_vel(axis, vel)

    return AdcCtrlActions(
        stop = Action( adc.stop, [], feedback),
        start_track = Action( adc.start_track, [args.input_angle], feedback),
        stop_track = Action( adc.stop_track, [], feedback),
        move = Action(move, 
                [args.mode, args.axis, args.pos_target, args.velocity], 
                feedback ),
        move_angle = Action( adc.move_angle, [args.input_angle], feedback)
    )

def adc_ctrl_connect(widget: AdcCtrlWidget, adc: Adc):
    set_adc_ctrl_widget(widget, adc)
    args = adc_ctrl_args(widget)
    actions = adc_ctrl_actions(adc, args)
    Proc.button_connector.connect( widget.stop, actions.stop)
    Proc.button_connector.connect( widget.start_track, actions.start_track)
    Proc.button_connector.connect( widget.stop_track, actions.stop_track)
    Proc.button_connector.connect( widget.move, actions.move)
    Proc.button_connector.connect( widget.move_angle, actions.move_angle) 
    widget.adc_ctrl_actions = actions # need to be saved somewhere (weakref)

def adc_ctrl_disconnect(widget: AdcCtrlWidget)-> None:
    Proc.button_connector.disconnect( widget.stop)
    Proc.button_connector.disconnect( widget.start_track)
    Proc.button_connector.disconnect( widget.stop_track)
    Proc.button_connector.disconnect( widget.move)
    Proc.button_connector.disconnect( widget.move_angle) 

record_qt(Adc, "ctrl")
class AdcCtrl(Base):
    Proc = Proc
    Widget = AdcCtrlWidget   

    class Monitor(Base.Monitor):
        Data = AdcCtrlData
        DataSetter = AdcCtrlSetter
        data_setter = DataSetter()

        def update(self, widget: QWidget, data: Data):
            super().update( widget, data)
            if widget.move_mode.currentIndex()==MOVE_MODE.VELOCITY:
                widget.input_pos_target.setEnabled(False)
            else:
                widget.input_pos_target.setEnabled(True)

    class Connector(Base.Connector):
        
        def connect(self, widget, adc):
            super().connect(widget, adc)
            adc_ctrl_connect(widget, adc)

        def disconnect(self, widget):
            super().disconnect(widget)
            adc_ctrl_disconnect(widget)

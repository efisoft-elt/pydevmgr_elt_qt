from dataclasses import dataclass
from enum import IntEnum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame
from pydantic.fields import Field
from pydantic.main import BaseModel
from pydevmgr_core.base.node_alias import NodeAlias
from pydevmgr_core_ui import feedback

from pydevmgr_elt.devices.motor import Motor
from .elt_device_line import EltDeviceLine, MenuErrorFeedback
from PyQt5 import uic, QtWidgets
from .io import find_ui
from pydevmgr_core_qt import  (ActionMap, BaseFeedback, Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 

Base = EltDeviceLine



class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class Proc(Base.Proc):
    pos_setter =   get_setter_class(QtWidgets.QLabel, float)(format="%.3f")
    error_setter = get_setter_class(QtWidgets.QLabel, float)(format="%.3E")


class FormatedPos(NodeAlias):
    class Config:
        format: str = "%.3f"
    def fget(self, pos, posname):
        if posname:
            return posname 
        else:
            return self.config.format%pos

class MotorLineData(Base.Monitor.Data):
    class Stat(Base.Monitor.Data.Stat):
        pos: NodeVar[str] =  Field("", 
                    node=FormatedPos.Config(nodes=["pos_actual", "pos_name"]) 
                )

        pos_actual: NodeVar[float] = 0.0
        pos_name: NodeVar[str]     = ""
    stat: Stat = Stat()


class MotorLineSetter(Base.Monitor.DataSetter):
    
    def set(self, w, data):
        super().set(w, data)
        Proc.text_setter.set(w.pos_actual, data.stat.pos)
        
    

def set_motor_line_widget(widget, motor):
    if motor.is_connected():
        Proc.pos_setter.set(widget.input_pos_target,motor.stat.pos_actual.get()) 
    else:
        Proc.pos_setter.set(widget.input_pos_target, 0.0)
    Proc.pos_setter.set(widget.input_velocity, motor.ctrl_config.velocity)

    wa = widget.state_action
    wa.addItems( ["STOP", "MOVE ABS", "MOVE REL", "MOVE VEL"])
    wa.insertSeparator(wa.count())
    wa.addItems( motor.posnames)



@dataclass
class MotorLineArgs:
    pos_target: Callable
    velocity: Callable
    feedback:  BaseFeedback
    reset : Callable
def motor_line_args(widget)-> MotorLineArgs:
    return MotorLineArgs( 
                pos_target = lambda : Proc.float_getter.get(widget.input_pos_target), 
                velocity = lambda : Proc.float_getter.get(widget.input_velocity),
                feedback = MenuErrorFeedback(widget.state_action), 
                reset = lambda: widget.state_action.setCurrentIndex(0)
        )



@dataclass
class MotorLineActions:
    command: ActionMap

def motor_line_actions(motor: Motor, args: MotorLineArgs)-> MotorLineActions:
    feedback = args.feedback
    
    command = ActionMap(after = args.reset)
    command.add_action( Action(motor.stop, [], feedback), "STOP" )

    command.add_action(  "MOVE ABS", 
            Action(motor.move_abs, 
                   [args.pos_target, args.velocity], 
                   feedback
                   )
            )
               
    command.add_action( "MOVE REL", 
            Action(motor.move_rel, 
                   [args.pos_target, args.velocity], 
                   feedback
                   )
            )
    command.add_action("MOVE VEL", 
            Action(motor.move_vel, 
                   [ args.velocity], 
                   feedback
                   )
            )
    
    for posname in motor.posnames:
        command.add_action(posname,  
                Action(motor.move_name, [posname, args.velocity], feedback)
            ) 
    return MotorLineActions(command = command) 




def motor_line_connect(widget, motor):
    set_motor_line_widget(widget, motor)
    args = motor_line_args(widget)
    actions = motor_line_actions(motor, args)
    Proc.menu_connector.connect( widget.state_action, actions.command)
    widget.motor_line_actions = actions     




@record_qt(Motor, "line")
class MotorLine(Base):
    
    class Widget(Base.Widget):
        def __init__(self,*args, **kwargs):
            QFrame.__init__(self, *args, **kwargs)
            uic.loadUi(find_ui('motor_line_frame.ui'), self) 
        
    class Monitor(Base.Monitor):
        Data = MotorLineData
        DataSetter = MotorLineSetter 

        data_setter = DataSetter() 
               
        def update(self, widget, data):
            super().update(widget, data)
  

    class Connector(Base.Connector):

        def connect(self, widget, motor):
            super().connect(widget, motor)
            motor_line_connect(widget, motor)


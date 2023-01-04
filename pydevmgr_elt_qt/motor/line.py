from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable, List
from PyQt5.QtWidgets import QFrame, QLabel, QLineEdit
from pydantic.fields import Field
from pydevmgr_core.base.node_alias import NodeAlias

from pydevmgr_elt.devices.motor import Motor
from PyQt5 import uic, QtWidgets
from pydevmgr_core_qt import  (ActionMap, BaseFeedback, Action, get_setter_class, record_qt)
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.line as base 
from pydevmgr_elt_qt.base import find_ui

Base = base.EltDeviceLine


class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2


class ActionMenuName(str, Enum):
    STOP = "STOP"
    MOVE_ABS = "MOVE ABS"
    MOVE_REL = "MOVE REL"
    MOVE_VEL = "MOVE VEL"


class FormatedPos(NodeAlias):
    class Config:
        format: str = "%.3f"
        nodes: List =["pos_actual", "pos_name"]
    def fget(self, pos, posname):
        if posname:
            return posname 
        else:
            return self.config.format%pos

##############################################################  

class Widget(base.Widget):
    pos_actual: QLabel
    input_pos_target: QLineEdit
    input_velocity: QLineEdit

    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('motor_line_frame.ui'), self) 

Proc = base.Proc

class Data(base.Data):
    class Stat(base.Data.Stat):
        pos: NodeVar[str] =  Field("", node=FormatedPos.Config())

        pos_actual: NodeVar[float] = 0.0
        pos_name: NodeVar[str]     = ""
    stat: Stat = Stat()



@dataclass
class Args(base.Args):
    pos_target: Callable = None
    velocity: Callable = None 

@dataclass
class Actions(base.Actions):
    ...



##############################################################  

def set_widget(widget: Widget, motor: Motor):
    base.set_widget(widget, motor)
    if motor.is_connected():
        Proc.pos_setter.set(widget.input_pos_target,motor.stat.pos_actual.get()) 
    else:
        Proc.pos_setter.set(widget.input_pos_target, 0.0)
    Proc.pos_setter.set(widget.input_velocity, motor.ctrl_config.velocity)

    wa = widget.state_action
    wa.addItems( ActionMenuName )
    wa.insertSeparator(wa.count())
    wa.addItems( motor.posnames)


def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    Proc.text_setter.set(w.pos_actual, data.stat.pos)

def set_args(args: Args, widget)-> Args:
    base.set_args(args, widget)

    args.pos_target = lambda : Proc.float_getter.get(widget.input_pos_target) 
    args.velocity = lambda : Proc.float_getter.get(widget.input_velocity)


def set_actions(actions: Actions, motor: Motor, args: Args)-> Actions:
    base.set_actions(actions, motor, args)

    feedback = args.feedback
    # actions.more_commands = ActionMap(after=args.reset)
    # command = actions.more_commands 
    command = actions.command 
    
    command.add_action(
        ActionMenuName.STOP  , Action(motor.stop, [], feedback) 
    )
    command.add_action(
        ActionMenuName.MOVE_ABS, Action(motor.move_abs, [args.pos_target, args.velocity], feedback)
    )
    command.add_action(
        ActionMenuName.MOVE_REL, Action(motor.move_rel, [args.pos_target, args.velocity], feedback)
    )
    command.add_action(
        ActionMenuName.MOVE_VEL, Action( motor.move_vel, [args.velocity], feedback) 
    )
    
    
    for posname in motor.posnames:
        command.add_action(posname,  
                Action(motor.move_name, [posname, args.velocity], feedback)
            ) 

def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    # Proc.menu_connector.connect( widget.state_action,  actions.more_commands) 
    # widget.motor_actions = actions

def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)



##############################################################  

@record_qt(Motor, "line")
class MotorLine(Base):
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

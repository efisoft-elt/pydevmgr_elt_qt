from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Callable
from PyQt5.QtWidgets import  QFrame, QLabel, QLineEdit

from pydevmgr_elt.devices import Drot
from PyQt5 import uic
from pydevmgr_core_qt import  (Action, record_qt)
from pydevmgr_core import NodeVar 

import pydevmgr_elt_qt.device.line as base 
from pydevmgr_elt_qt.base import find_ui

Base = base.EltDeviceLine
Device = Drot 

class MOVE_MODE(IntEnum):
    ABSOLUTE = 0
    RELATIVE = 1
    VELOCITY = 2

class TRACK_MODE(IntEnum):
    SKY = 2
    ELEV = 3
    USER = 4

class ActionMenuName(str, Enum):
    STOP = "STOP"
    MOVE_ANGLE = "MOVE ANGLE"
    TRK_ELEV = "TRK ELEV"
    TRK_SKY  = "TRK SKY"
    TRK_USER = "TRK USER"
    STOP_TRK = "STOP TRK"

##############################################################  

class Proc(base.Proc):
    ...

class Widget(base.Widget):
    track_mode_txt: QLabel
    angle_on_sky: QLabel
    pos_actual: QLabel
    input_angle:  QLineEdit
    
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('drot_line_frame.ui'), self) 

class Data(base.Data):
    class Stat(base.Data.Stat):
        track_mode_txt: NodeVar[str] = ""     
        pos_actual: NodeVar[float] = 0.0 
        angle_on_sky: NodeVar[float] = 0.0

    stat: Stat = Stat()


@dataclass
class Args(base.Args):
    angle: Callable = None
    
Actions = base.Actions 

    
##############################################################  

def set_widget(widget: Widget , drot: Drot)-> None:
    base.set_widget(widget, drot)

    Proc.pos_setter.set(widget.input_angle, 0.0) 

    wa = widget.state_action
    wa.addItems(ActionMenuName)

def update_data(w: Widget, data: Data) -> None:
    base.update_data(w,data)
    Proc.text_setter.set(w.track_mode_txt, data.stat.track_mode_txt)        
    Proc.pos_setter.set(w.angle_on_sky, data.stat.angle_on_sky) 
    Proc.pos_setter.set(w.pos_actual, data.stat.pos_actual)

def set_args(args: Args, widget)-> Args:
    base.set_args(args, widget)
    args.angle = lambda : Proc.float_getter.get(widget.input_angle) 

def set_actions(actions: Actions, drot: Drot, args: Args)-> Actions:
    base.set_actions(actions, drot, args)
    feedback = args.feedback

    amap = [
        (ActionMenuName.STOP , Action(drot.stop, [], feedback)), 
        (ActionMenuName.MOVE_ANGLE, Action(drot.move_abs, [args.angle], feedback)), 
        (ActionMenuName.TRK_ELEV, Action(drot.start_track, [TRACK_MODE.ELEV, args.angle], feedback)), 
        (ActionMenuName.TRK_SKY,  Action(drot.start_track, [TRACK_MODE.SKY, args.angle], feedback)), 
        (ActionMenuName.TRK_USER, Action(drot.start_track, [TRACK_MODE.USER, args.angle], feedback)), 
        (ActionMenuName.STOP_TRK, Action(drot.stop_track, [], feedback)),
    ]

    for name, action in amap:
        actions.command.add_action(name, action)
    

connect_action = base.connect_action 
disconnect_action = base.disconnect_action 

##################################################################
@record_qt(Drot, "line")
class DrotLine(Base):
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


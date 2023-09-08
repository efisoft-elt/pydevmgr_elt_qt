
from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_core.base.node_alias import NodeAlias
from pydevmgr_core.base.vtype import VType

from pydevmgr_qt.api import (QtNodeFactory, register_qt_handler)

from pydevmgr_elt import Motor
from pydevmgr_elt_qt.device.line import QtEltDeviceLine
from pydevmgr_elt_qt.motor.actions import  MotorCommands, MoveByName
import pkg_resources, os

class PosOrPosName(NodeAlias):
    class Config:
        vtype: VType = str
        nodes: list  = ["pos_actual", "pos_name"]
        format: str = "%.3f" 
    def fget(self, pos, posname):
        if posname: return posname
        return self.format%(pos,) 


class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("motor", "uis", "motor_line_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)


QtBase = QtEltDeviceLine 

############################################################################### 
@register_qt_handler(Motor, "line")
class QtMotorLine(QtBase):
    Widget = Widget
    class Stat(QtBase.Stat):
        pos  = QtNodeFactory(vtype=str, widget="pos_actual",  
                pair=PosOrPosName.Config(format="%.3f"))
  
    stat = Stat.Config(pair="stat")

    move = MotorCommands.Config(actioner="state_action",      feedback = QtBase.feedback)
    move_by_name = MoveByName.Config(actioner="state_action", feedback = QtBase.feedback)

 ###############################################################################    
     
if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device, Motor 
    
    motor = open_elt_device("tins/motor1.yml(motor1)")
    test_widget( QtMotorLine, motor)
   

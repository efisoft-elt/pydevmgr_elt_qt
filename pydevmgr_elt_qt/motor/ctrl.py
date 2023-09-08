from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFrame
from pydevmgr_elt import Motor 
from pydevmgr_qt.api import (QtNodeFactory, register_qt_handler)
from pydevmgr_elt_qt.device.ctrl import QtEltDeviceCtrl
from pydevmgr_elt_qt.motor.actions import MoveByName, MOVE_MODE, Move, Stop
import pkg_resources 
import os


class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("motor", "uis", "motor_ctrl_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

QtBase = QtEltDeviceCtrl
QNF = QtNodeFactory 

@register_qt_handler(Motor, "ctrl")
class QtMotorCtrl(QtBase):
    class Stat(QtBase.Stat):
        pos_actual = QNF(vtype=float, widget="pos_actual", format="%.3f")
        pos_target = QNF(vtype=float, widget="pos_target", format="%.3f")
        pos_error  = QNF(vtype=float, widget="pos_error",  format="%.3f")
        vel_actual = QNF(vtype=float, widget="vel_actual", format="%.3f")
        pos_name   = QNF(vtype=str,   widget="posname")
        
    Widget = Widget
    stat = Stat.Config(pair="stat")
    name = QNF( vtype=str, widget="name")
    
    move = Move.Config( actioner="move", feedback=QtBase.feedback)
    stop = Stop.Config( widget="stop"  , feedback=QtBase.feedback)
    move_by_name = MoveByName.Config( actioner="move_by_posname", feedback=QtBase.feedback)
    
    def refresh(self):
        enable_pos = self.move.move_mode.get()!=MOVE_MODE.VELOCITY
        self.move.position.widget.setEnabled(enable_pos)
  
if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    motor =  open_elt_device("tins/motor1.yml(motor1)")
    test_widget( QtMotorCtrl, motor)
     

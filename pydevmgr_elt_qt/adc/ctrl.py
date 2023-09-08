from PyQt5 import uic
from PyQt5.QtWidgets import  QFrame
from pydevmgr_elt import Adc
from pydevmgr_qt.api import (QtInterface, QtNodeFactory, register_qt_handler)
from pydevmgr_elt_qt.device.ctrl import QtEltDeviceCtrl
from pydevmgr_elt_qt.adc.actions import MoveAngle, StartTrack, StopTrack, Move
from pydevmgr_elt_qt.motor.actions import  MOVE_MODE,  Stop
import pkg_resources 
import os


class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("adc", "uis", "adc_ctrl_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

class QNFM(QtNodeFactory):
    wvar: str 
    def build( self, parent=None, name=None):
        self.widget = f"motor{parent.mot_number}_{self.wvar}"
        args = dict(self) 
        args.pop("wvar")
        return QtNodeFactory( **args ).build(parent, name)  

class QtMotStat(QtInterface):
    class Config:
        mot_number: int 
        pos_actual = QNFM(vtype=float, wvar="pos_actual", format="%.3f")
        pos_actual = QNFM(vtype=float, wvar="pos_actual", format="%.3f")
        pos_target = QNFM(vtype=float, wvar="pos_target", format="%.3f")
        pos_error  = QNFM(vtype=float, wvar="pos_error",  format="%.3f")
        vel_actual = QNFM(vtype=float, wvar="vel_actual", format="%.3f")

QtBase = QtEltDeviceCtrl
QNF = QtNodeFactory 

@register_qt_handler(Adc, "ctrl")
class QtAdcCtrl(QtBase):
    class Stat(QtBase.Stat):
        track_mode_txt = QNF(vtype=str, widget="track_mode_txt")
        
    Widget = Widget
    stat = Stat.Config(pair="stat")
    mot1 = QtMotStat.Config( mot_number=1, pair="motor1.stat") 
    mot2 = QtMotStat.Config( mot_number=2, pair="motor2.stat") 
    

    move = Move.Config( actioner="move", feedback=QtBase.feedback)
    stop = Stop.Config( actioner="stop"  , feedback=QtBase.feedback)
    start_track = StartTrack.Config( actioner="start_track", feedback=QtBase.feedback)
    stop_track = StopTrack.Config( actioner="stop_track", feedback=QtBase.feedback)
    move_angle = MoveAngle.Config( actioner="move_angle", feedback=QtBase.feedback ) 
    
    def refresh(self):
        enable_pos = self.move.move_mode.get()!=MOVE_MODE.VELOCITY
        self.move.position.widget.setEnabled(enable_pos)
  
if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    adc =  open_elt_device("tins/adc1.yml(adc1)")
    test_widget( QtAdcCtrl, adc)
     

from PyQt5 import uic
from PyQt5.QtWidgets import  QFrame
from pydevmgr_elt import Drot 
from pydevmgr_elt_qt.device.ctrl import QtEltDeviceCtrl
from pydevmgr_qt.api import QtNodeFactory, register_qt_handler
from pydevmgr_elt_qt.drot.actions import MoveAngle, StartTrack, StopTrack
from pydevmgr_elt_qt.motor.actions import  MOVE_MODE, Move, Stop
import pkg_resources 
import os


class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("drot", "uis", "drot_ctrl_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

QtBase = QtEltDeviceCtrl
QNF = QtNodeFactory 

@register_qt_handler(Drot, "ctrl")
class QtDrotCtrl(QtBase):
    class Stat(QtBase.Stat):
        pos_actual = QNF(vtype=float, widget="pos_actual", format="%.3f")
        pos_target = QNF(vtype=float, widget="pos_target", format="%.3f")
        pos_error  = QNF(vtype=float, widget="pos_error",  format="%.3f")
        vel_actual = QNF(vtype=float, widget="vel_actual", format="%.3f")
        angle_on_sky = QNF(vtype=float, widget="angle_on_sky", format="%.3f")
        track_mode_txt = QNF(vtype=str, widget="track_mode_txt")
        # pos_name   = QNF(vtype=str,   widget="posname")
        
    Widget = Widget
    stat = Stat.Config(pair="stat")
    
    move = Move.Config( actioner="move", feedback=QtBase.feedback)
    stop = Stop.Config( actioner="stop"  , feedback=QtBase.feedback)
    start_track = StartTrack.Config( actioner="start_track", feedback=QtBase.feedback)
    stop_track = StopTrack.Config( actioner="stop_track", feedback=QtBase.feedback)
    move_angle = MoveAngle.Config( actioner="move_angle", feedback=QtBase.feedback ) 
    # move_by_name = MoveByName.Config( actioner="move_by_posname", feedback=QtBase.feedback)
    
    def refresh(self):
        enable_pos = self.move.move_mode.get()!=MOVE_MODE.VELOCITY
        self.move.position.widget.setEnabled(enable_pos)
  
if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    drot =  open_elt_device("tins/drot1.yml(drot1)")
    test_widget( QtDrotCtrl, drot)
     

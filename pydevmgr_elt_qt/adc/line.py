
from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_core import NodeAlias, VType
from pydevmgr_elt import Adc
from pydevmgr_qt.api import    QtNodeFactory, register_qt_handler
from pydevmgr_elt_qt.device.line import QtEltDeviceLine
from pydevmgr_elt_qt.adc.actions import  AdcCommands
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
        file = os.path.join("adc", "uis", "adc_line_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)


QtBase = QtEltDeviceLine 
QNF = QtNodeFactory

############################################################################### 
@register_qt_handler(Adc, "line")
class QtAdcLine(QtBase):
    Widget = Widget
    class Stat(QtBase.Stat):
        track_mode_txt = QNF(vtype=str, widget="track_mode_txt")
    
    motor1_pos_actual = QNF(vtype=float, widget="motor1_pos_actual", pair="motor1.stat.pos_actual")
    motor2_pos_actual = QNF(vtype=float, widget="motor2_pos_actual", pair="motor2.stat.pos_actual")

    stat = Stat.Config(pair="stat")
    
    move = AdcCommands.Config(actioner="state_action", feedback = QtBase.feedback)

 ###############################################################################    
     
if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device, adc 
    
    adc = open_elt_device("tins/adc1.yml(adc1)")
    test_widget( QtAdcLine, adc)
   

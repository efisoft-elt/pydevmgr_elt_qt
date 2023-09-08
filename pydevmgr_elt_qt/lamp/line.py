
from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_elt import Lamp
from pydevmgr_elt_qt.device.line import QtEltDeviceLine
from pydevmgr_elt_qt.lamp.actions import LampCommands 
from pydevmgr_qt.api import QtNodeFactory, register_qt_handler
import pkg_resources, os


class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("lamp", "uis", "lamp_line_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

Base = QtEltDeviceLine
QNF = QtNodeFactory 

@register_qt_handler(Lamp,"line")
class QtLampLine(Base):
    Widget = Widget
    class Stat(Base.Stat):
        time_left= QNF(vtype=float, widget="time_left")
    stat = Stat.Config(pair="stat", implicit_pairing=True)
    switch = LampCommands.Config(actioner="state_action", feedback = Base.feedback)


if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    lamp =  open_elt_device("tins/lamp1.yml(lamp1)")
    test_widget( QtLampLine, lamp)
     


from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_elt import Shutter
from pydevmgr_elt_qt.device.line import QtEltDeviceLine
from pydevmgr_elt_qt.shutter.actions import ShutterCommands 
from pydevmgr_qt.api import QtNodeFactory, register_qt_handler

import pkg_resources, os

class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("shutter", "uis", "shutter_line_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

Base = QtEltDeviceLine
QNF = QtNodeFactory 

@register_qt_handler(Shutter, "line")
class QtShutterLine(Base):
    Widget = Widget
    switch = ShutterCommands.Config(actioner="state_action", feedback = Base.feedback)


if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    shutter =  open_elt_device("tins/shutter1.yml(shutter1)")
    test_widget( QtShutterLine, shutter)
     

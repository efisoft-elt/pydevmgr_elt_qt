
from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_elt import Shutter
from pydevmgr_elt_qt.device.base import QtEltDevice
from pydevmgr_elt_qt.device.ctrl import QtEltDeviceCtrl
from pydevmgr_elt_qt.shutter.actions import Close, Open
from pydevmgr_qt.api import QtNodeFactory as QNF, register_qt_handler
import pkg_resources, os


class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("shutter", "uis", "shutter_ctrl_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

Base = QtEltDeviceCtrl

@register_qt_handler(Shutter, "ctrl")
class QtShutterCtrl(Base):
    Widget = Widget
    
    open = Open.Config(actioner="open", feedback = Base.feedback)
    close = Close.Config(actioner="close", feedback= Base.feedback)


if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    shutter =  open_elt_device("tins/shutter1.yml(shutter1)")
    test_widget( QtShutterCtrl, shutter)
     

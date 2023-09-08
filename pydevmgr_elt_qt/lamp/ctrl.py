
from PyQt5 import uic
from PyQt5.QtWidgets import QFrame
from pydevmgr_elt import Lamp
from pydevmgr_elt_qt.device.ctrl import QtEltDeviceCtrl
from pydevmgr_elt_qt.lamp.actions import SwitchOff, SwitchOn
from pydevmgr_qt.api import QtNodeFactory as QNF, register_qt_handler

import pkg_resources, os

class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("lamp", "uis", "lamp_ctrl_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

QtBase = QtEltDeviceCtrl

@register_qt_handler(Lamp, "ctrl")
class QtLampCtrl(QtBase):
    Widget = Widget
    class Stat(QtBase.Stat):
        time_left= QNF(vtype=float, widget="time_left")
        intensity= QNF(vtype=float, widget="intensity")
    stat = Stat.Config(pair="stat", implicit_pairing=True)

    switch_on = SwitchOn.Config(actioner="on", feedback = QtBase.feedback)
    switch_off = SwitchOff.Config(actioner="off", feedback= QtBase.feedback)




if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    lamp =  open_elt_device("tins/lamp1.yml(lamp1)")
    test_widget( QtLampCtrl, lamp)
     

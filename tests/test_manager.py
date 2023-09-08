

from pydevmgr_core import set_data_model
from pydevmgr_qt.api import ToLayout, QtDeviceFactory
from pydevmgr_elt_qt.manager.manager import QtManager
from pydevmgr_elt_qt.motor.ctrl import QtMotorCtrl
from pydevmgr_elt_qt import lamp

@set_data_model
class M(QtManager):
    # motor = QtMotorCtrl.Config( widget=QtMotorCtrl.Widget, appender=ToLayout(layout="mainLayout"), pair="motor1")
    motor1 = QtDeviceFactory(
            dtype="Motor", pair="motor1", appender=ToLayout("mainLayout")
        )
    lamp1 = QtDeviceFactory(
            dtype="Lamp", pair="lamp1", appender=ToLayout("mainLayout")
        )
     
if __name__ == "__main__":

    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_manager 
    tins =  open_elt_manager("tins/tins.yml")
    print( M.Data()) 
    # test_widget( M, tins)
     

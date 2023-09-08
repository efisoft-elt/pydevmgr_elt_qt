from typing import Dict
from PyQt5 import uic
from pydevmgr_core import BaseFactory, BaseNode, find_factories
from pydevmgr_qt.api import QtInterface, PairingType, register_qt_handler

from pydevmgr_elt.devices.motor import Motor
from pydevmgr_elt_qt.device.base import QtEltDevice
from pydevmgr_elt_qt.motor.actions import DownloadFromPlc, LoadInitialConfig, UploadToPlc
from pydevmgr_elt_qt.shared import QtIoFactory
from pydevmgr_elt_qt.motor.initseq import  QtInitSeqInterface 
from PyQt5.QtWidgets import QFrame

import pkg_resources, os

class Widget(QFrame):
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        file = os.path.join("motor", "uis", "motor_cfg_frame.ui")
        uic.loadUi(pkg_resources.resource_filename("pydevmgr_elt_qt",file), self)

# dynamicaly create the Cfg Interface
ioFactories: Dict[str,BaseFactory] = {"init_seqences": QtInitSeqInterface.Config(pair=".") } #
for attr, f in find_factories(Motor.Cfg, BaseNode):
    if attr.startswith("init_"): continue 
    if attr in ["velocity"]: continue 
    ioFactories[attr] = QtIoFactory( vtype=f.vtype , name=attr)

Cfg = type("QtMotorConfigInterface", (QtInterface,), dict(ioFactories) )



################################################################################

QtBase = QtEltDevice
@register_qt_handler(Motor, "cfg")
class QtMotorCfg(QtBase):
    Widget = Widget 
    Cfg = Cfg
    cfg = Cfg.Config( pair="cfg", pairing_type = PairingType.source, implicit_pairing=True)
    
    download_from_plc = DownloadFromPlc.Config( 
            actioner="in_download_from", cfg=cfg
        ) 
    
    upload_to_plc = UploadToPlc.Config( 
            actioner="in_upload_to",cfg=cfg 
        )
    load_initial_config = LoadInitialConfig.Config( 
            actioner="in_from_config_file", cfg=cfg
        )  
    

################################################################################


if __name__ == "__main__":
    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_device 
    motor =  open_elt_device("tins/motor1.yml(motor1)")
    test_widget( QtMotorCfg, motor)
     

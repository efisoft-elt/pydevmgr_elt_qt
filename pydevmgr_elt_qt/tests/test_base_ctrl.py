import time
from pydevmgr_elt_qt.elt_device_ctrl import EltDeviceCtrl
from pydevmgr_elt import Motor 
from pydevmgr_core import Downloader, open_device
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

import sys 



if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    
    device = open_device("tins/motor1.yml(motor1)")
    downloader = Downloader()
    
    ui = EltDeviceCtrl(device)
    ui.show()
    ui.connect(downloader)
    
    ui2 = EltDeviceCtrl(device)
    ui2.show()
    ui2.connect(downloader)

    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    
    with device:    
        timer.start(100)
        sys.exit(app.exec_())
        # print(device.is_ignored.get())

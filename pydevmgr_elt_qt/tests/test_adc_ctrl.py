import time
from pydevmgr_elt_qt.adc import AdcCtrl
from pydevmgr_core import Downloader, open_device
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

import sys 



if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    
    device = open_device("tins/adc1.yml(adc1)")
    downloader = Downloader()
    
    ui = AdcCtrl(device)
    ui.show()
    ui.connect_downloader(downloader)
    
  
    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    
    with device:    
        timer.start(100)
        sys.exit(app.exec_())
        # print(device.is_ignored.get())

import time
from pydevmgr_elt_qt.shutter import ShutterLine
# from pydevmgr_elt import Lamp    
from pydevmgr_core import Downloader, open_device
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore

import sys 

online = True

if __name__ == "__main__":
    

    app = QApplication(sys.argv)
    
    device = open_device("tins/shutter1.yml(shutter1)")
    downloader = Downloader()
    
    ui = ShutterLine(device)
    ui.show()
    ui.connect_downloader(downloader)
    
  
    timer = QtCore.QTimer()
    timer.timeout.connect(downloader.download)
    if online: 
        with device:    
            timer.start(100)
            sys.exit(app.exec_())
    else:
        ui.link.data.stat.pos_name = "YO!"
        ui.update() 
        sys.exit(app.exec_())
        # print(device.is_ignored.get())

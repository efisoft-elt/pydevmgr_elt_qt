from PyQt5.QtWidgets import QAction, QLabel, QMainWindow, QMenu, QVBoxLayout, QWidget
from pydevmgr_elt.base.eltstat import StateInfo
from pydevmgr_qt.api import (PairingType,  QtInterface, QtNodeFactory)
from pydevmgr_elt_qt.device.base import QtEltDevice

from pydevmgr_elt_qt.manager.actions import ChangeState
from pydevmgr_elt_qt import nodes



class ManagerWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main = QWidget()
        
        self.actionMenu = QMenu("&Action", self)
        self.menuBar().addMenu(self.actionMenu)
        
        self.actionMenu.addAction( QAction("Test", self)  )
        self.setCentralWidget( self.main )
        
        self.mainLayout = QVBoxLayout()
        self.main.setLayout( self.mainLayout)

        self.state = QLabel()
        self.mainLayout.addWidget( self.state )


class QtManager(QtEltDevice):
    Widget = ManagerWidget 
    
    class Stat(QtInterface):
        class Config:
            pairing_type = PairingType.source
            implicit_pairing = True
            state_info = QtNodeFactory( vtype=StateInfo, widget = "state" )

    stat = Stat.Config(pair="stat")
    change_state = ChangeState.Config( actioner= "actionMenu", __setup__={"menu.widget":"actionMenu"}) 
    
    
if __name__ == "__main__":

    from pydevmgr_elt_qt.shared import test_widget 
    from pydevmgr_elt import open_elt_manager 
    tins =  open_elt_manager("tins/tins.yml")
    test_widget( QtManager, tins)
     

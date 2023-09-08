from PyQt5.QtWidgets import QLabel
from pydevmgr_qt.api import BaseQtNode , get_style, register_qtnode
from pydevmgr_elt.base.eltstat import StateInfo

@register_qtnode(QLabel, StateInfo) 
class QtStatInfoNode(BaseQtNode):
    def fset(self, ctg: StateInfo ):
        code, text, group = ctg 
        self.widget.setText( f"{code}: {text}" )
        self.widget.setStyleSheet(get_style(group))   
    def fget(self):
        text = self.widget.text() 
        c,t, *_ = text.split(":")
        return StateInfo( int(c), t)


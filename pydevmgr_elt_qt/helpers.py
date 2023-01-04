from dataclasses import dataclass
from typing import Tuple
from PyQt5.QtWidgets import QWidget
from pydevmgr_core_ui import BaseSetter
from pydevmgr_core_qt.style import Style, get_style
from pydevmgr_elt.base.config import GROUP
from pydevmgr_elt.base.tools import get_enum_txt, get_enum_group
from enum import Enum 

class CodeTextGroupSetter(BaseSetter):
    def set(self, widget: QWidget, ctg: Tuple[int,str,str] ):
        code, text, group = ctg 
        widget.setText( f"{code}: {text}" )
        widget.setStyleSheet(get_style(group))   

        
@dataclass
class EnumTextGroupSetter(BaseSetter):
    enum: Enum 
    def set(self, widget: QWidget, code: int):
        text = get_enum_txt(self.enum, code,f"UNKNOWN ({code})")
        group = get_enum_group( self.enum, code, GROUP.UNKNOWN)
        widget.setText( f"{code}: {text}" )
        widget.setStyleSheet(get_style(group))   


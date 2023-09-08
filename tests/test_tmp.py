from PyQt5.QtWidgets import QCheckBox
from pydevmgr_qt.qtobjects.nodes import get_qtnode_factory_class ,QtNodeCheck 
F = get_qtnode_factory_class( QCheckBox, bool)
print ( type(F()) ) 

print( QtNodeCheck.Config())




from dataclasses import Field, dataclass, field
from os import wait
from typing import Dict, Iterable, List, Optional, Union
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from pydantic.main import BaseModel
from pydevmgr_core import Downloader
from pydevmgr_core import BaseDevice
from pydevmgr_core_qt import get_qt_class

from PyQt5.QtWidgets import QBoxLayout, QGridLayout, QHBoxLayout, QLayout, QWidget
from pydevmgr_core_qt.device import QtBaseDevice

from pydevmgr_elt import EltDevice
from pydevmgr_elt_qt.base.device import QtBase 
from pydevmgr_elt_qt.io import find_ui
from typing import Type
import glob 


# ###################################################################

# Data user interface for views 

# #################################################################
class ViewSetupConfig(BaseModel):
    """
     configuration of one view setup 

    Args:
        layout (str) : name of the layout in the ui used to publish widget (default is 'ly_devices')
        dev_type (iterable, str): Accepted device type names, e.g. ["Motor", "Drot"]
        alt_dev_type (str, None) : If not found look at a widget defined for a `alt_dev_type`
        exclude_device (str, iterable): exclude the device with the given names
        exclude_dev_type (str, iterable): exclude device with the given types
        widget_kind (str): string defining the widget kind (default, 'ctrl')
        alt_layout (iterable, str): Alternative layout name if `layout` is not found
        
        column, row, columnSpan, rowSpan, stretch, alignment : for layout placement. 
                The use depend of the nature of the layout (Grid, HBox, VBox) 
    """
    layout: str = "ly_devices" 
    device: Union[str, Iterable] = "*"
    dev_type: Union[str, Iterable]  = "*"
    alt_dev_type: Optional[List[str]] = None

    exclude_device: Union[str, Iterable] = ""
    exclude_dev_type: Union[str, Iterable]  = ""
    
    widget_kind: str = "ctrl"
    alt_layout: Union[str,Iterable] = [] 
    column: int = 0
    row: int = 0
    columnSpan: int = 1
    rowSpan: int = 1
    
    stretch: int = 0
    alignment: int = 0


class ViewConfig(BaseModel):
    setup: List[ViewSetupConfig] = ViewSetupConfig()
    size: Optional[List] = None
    ui_file: Optional[str] = None


class ViewsConfig(BaseModel):
    views: Dict[str, ViewConfig] = {} 




class Widget(QWidget):
    main_layout:  QHBoxLayout
    
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        
        self.main_layout = QHBoxLayout(objectName="main_layout")
        self.setLayout(self.main_layout)

def _get_device_widget_list(container: QWidget, layout: str):
    device_widget_loockup = _get_device_loockup(container)
    return device_widget_loockup.setdefault(layout, [])

def _get_device_loockup(container: QWidget):
    try:
        device_widget_loockup = container.__device_widget_loockup__
    except AttributeError:
        device_widget_loockup = {} 
        container.__device_widget_loockup__ = device_widget_loockup
    return device_widget_loockup


def _clear_layout(layout):
    for i in reversed(range(layout.count())):
        w: QWidget = layout.itemAt(i).widget()
        if hasattr( w, "__device_widget_loockup__"):
            for  dwl in w.__device_widget_loockup__.values():
                for dw in dwl:
                    dw.disconnect_downloader()
                    dw.kill()
        for sub_layout in w.findChildren(QLayout):
            _clear_layout(sub_layout)
            
        w.setParent(None)
            
@dataclass 
class DeviceAppender:
    """ The role of this class is to append device widget to a container's layout """
    layout: str = "ly_devices"
    alt_layout: List[str] = field(default_factory=list)
    stretch: int = 0
    alignment: int = 0 
    row: int = 0
    column: int = 0 
    rowSpan: int = 1 
    columnSpan: int = 1
    widget_kind: str = "ctrl"
    downloader: Optional[Downloader] = None 

    def append(self, container: QWidget, device: BaseDevice, widget_kind: Optional[str] = None) -> None:
        """ Append one device to the container at configured layout """
        QtDevice: Type[QtBase] = get_qt_class(type(device), widget_kind or self.widget_kind)
        device_widget: QtBase = QtDevice(device)
        
        if widget_kind is None:
            widget_kind = self.widget_kind
        
        if self.downloader: 
            device_widget.connect_downloader(self.downloader)

        self._append_widget(container, device_widget.widget)
        self._store_device_widget( container, device_widget)
    
    
    def extend(self, container: QWidget, devices: Iterable[BaseDevice], widget_kind: Optional[str] = None) -> None:
        for device in devices:
            self.append( container, device, widget_kind)
    

    def replace(self, container, devices: Iterable[BaseDevice], widget_kind: Optional[str] = None)-> None:
        self.clear(container)
        self.extend( container, devices, widget_kind)


    def clear(self, container: QWidget):
        device_widget_list = _get_device_widget_list( container, self.layout) 

        for device_widget in device_widget_list:
            device_widget.disconnect_downloader()
            device_widget.kill()
        device_widget_list.clear()
    
    def get_device_widgets(self, container):
        return _get_device_widget_list( container, self.layout) 
    
    def connect_downloader(self, downloader):
        self.downloader = downloader

    def _store_device_widget(self, container: QWidget, device_widget: QtBase):
        device_widget_list = _get_device_widget_list(container, self.layout)
        device_widget_list.append(device_widget)


    def _append_widget(self, container, widget: QWidget)-> None:
        layout = self._find_layout(container) 
        
        if isinstance(layout, QBoxLayout): 
            layout.addWidget(widget, self.stretch, QtCore.Qt.AlignmentFlag(self.alignment))
        elif isinstance(layout, QGridLayout):
            layout.addWidget(widget, self.row, self.column, self.rowSpan, self.columnSpan)
        else:
            layout.addWidget(widget)      
    
    def _find_layout(self, container: QWidget):
            """ find a layout from the container config 
            
            Look for a layout named as .layout properties. If not found look inside 
            the .alt_layout list property. 
            """
            layout = container.findChild(QLayout, self.layout or "")
            if layout is None:
                for ly_name in self.alt_layout:
                    layout = container.findChild(QLayout, ly_name)
                    if layout: break
                else:
                    raise ValueError(f"Cannot find layout with the name {self.layout!r} or any alternatives")
            return layout




def _obj_to_match_func(obj):
    if not obj:
        return lambda name: False 
    if isinstance(obj, str):
        return lambda name: glob.fnmatch.fnmatch(name, obj)
    elif hasattr(obj, "__iter__"): 
        return  lambda name: name in obj



@dataclass
class DeviceFilter:
    device: Union[str, Iterable] = "*"
    dev_type: Union[str, Iterable]  = "*"
    alt_dev_type: Optional[List[str]] = None

    exclude_device: Union[str, Iterable] = ""
    exclude_dev_type: Union[str, Iterable]  = ""   
    
    def filter(self, devices : Iterable[BaseDevice]) -> Iterable[BaseDevice]:
        output_devices = []
        match_device = _obj_to_match_func(self.device)
        match_type   = _obj_to_match_func(self.dev_type)
        
        exclude_match_device = _obj_to_match_func(self.exclude_device)
        exclude_match_type   = _obj_to_match_func(self.exclude_dev_type)
        for device in devices:        
            if exclude_match_device(device.name): continue
            if exclude_match_type(device.config.type): continue
            if match_device(device.name) and match_type(device.config.type):
                output_devices.append(device)  
        return output_devices
   

@dataclass
class DeviceFilteredAppander:
    appender: DeviceAppender = DeviceAppender()
    filter: DeviceFilter = DeviceFilter()
    
    downloader: Optional[Downloader] = None
    def __post_init__(self):
        if self.downloader:
            self.connect_downloader(self.downloader) 
   
    def append(self, container: QWidget,device: BaseDevice) -> None:
        devices = self.filter.filter( [device])
        if devices:
            self.appender.append( container, devices[0] )
    def extend(self, container: QWidget, devices: Iterable[BaseDevice]) -> None:
        devices = self.filter.filter(devices)
        self.appender.extend( container, devices)
    
    def replace(self, container: QWidget, devices: Iterable[BaseDevice]) -> None:
        devices = self.filter.filter(devices)
        self.appender.replace( container, devices)
    
    def clear(self, container: QWidget) -> None:
        self.appender.clear(container)
    
    def connect_downloader(self, downloader: Downloader) -> None:
        self.appender.connect_downloader( downloader) 
        self.downloader = downloader
        
    @classmethod
    def from_config(cls, config: ViewSetupConfig):
        if isinstance(config, dict):
            config = ViewSetupConfig(config)
        filter_args = set(["device", "dev_type", "alt_dev_type", "exclude_device", "exclude_dev_type"])
        return cls( 
            appender = DeviceAppender( *config.dict( exclude=filter_args ) ), 
            filter = DeviceFilter( *config.dict( include=filter_args ))
        )

@dataclass
class DeviceDispatcher:
    """ Dispatch devices in widget layouts according to an appender associated with a filter 

    Warning: If a downloader is given it will overwrite all downloader of the appenders 
    """
    filter_appenders: List[DeviceFilteredAppander] = field(default_factory=list)
    downloader: Optional[Downloader] = None
    def __post_init__(self):
        if self.downloader:
            self.connect_downloader(self.downloader) 
    def append(self, container: QWidget,device: BaseDevice) -> None:
        for fa in self.filter_appenders:
            fa.append( container, device)

    def extend(self, container: QWidget, devices: Iterable[BaseDevice]) -> None:
       for fa in self.filter_appenders:
            fa.extend( container, devices)
    
    def replace(self, container: QWidget, devices: Iterable[BaseDevice]) -> None:
        for fa in self.filter_appenders:
            fa.replace( container, devices)

    def clear(self, container: QWidget) -> None:
        for fa in self.filter_appenders:
            fa.clear( container )
    
    def connect_downloader(self,downloader: Downloader)-> None:
        for fa in self.filter_appenders:
            fa.connect_downloader(downloader)
        self.downloader = downloader



class DefaultViewWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ly_devices = QHBoxLayout(objectName="ly_devices")
        self.setLayout(self.ly_devices)


@dataclass
class ViewMaker:
    layout: str = "main_layout"
    setup: DeviceDispatcher = DeviceDispatcher()
    ui_file: Optional[str] = None
    DefaultWidget: QWidget = DefaultViewWidget    
    downloader: Optional[Downloader] = None
    
    def __post_init__(self):
        if self.downloader:
            self.connect_downloader(self.downloader) 

    def make(self, container: QWidget, devices: Iterable[BaseDevice]) -> None:
        main_layout = self._find_layout(container)
        _clear_layout(main_layout)    
        
        widget  =  self.new_widget()
        self.setup.replace(widget, devices)   
        

    def new_widget(self):
        if self.ui_file:
            return loadUi(find_ui(self.ui_file))
        else:
            return self.DefaultWidget()
    
    def connect_downloader(self, downloader: Downloader) -> None:
        self.setup.connect_downloader( downloader) 
        self.downloader = downloader
        
    def _find_layout(self, container: QWidget):
        """ find a layout from the container config 
        
        Look for a layout named as .layout properties. If not found look inside 
        the .alt_layout list property. 
        """
        
        layout = container.findChild(QLayout, self.layout or "")
        if layout is None:
            raise ValueError(f"Cannot find layout with the name {self.layout!r} or any alternatives")
        return layout



_default_views = {
    "ctrl": ViewMaker()
}
@dataclass
class ViewSwitcher:
    views: Dict[str,ViewMaker] = field(default_factory= _default_views.copy)
    downloader: Optional[Downloader] = None
    
    def __post_init__(self):
        if self.downloader:
            self.connect_downloader(self.downloader) 

    def switch( self, view, container: QWidget, devices: Iterable[BaseDevice])-> None:
        view = self.views[view]
        view.make( container, devices)
    
    def connect_downloader(self,downloader: Downloader)-> None:
        for vm in self.views.values():
            vm.connect_downloader(downloader)
        self.downloader = downloader

    

from PyQt5.QtWidgets import QComboBox
from pydevmgr_qt import ( QtFormular,  QtNodeFactory)
from pydevmgr_elt import Drot
from pydevmgr_qt.api import Action, ActionEnum
from pydevmgr_elt_qt.motor.actions import MotorCommands 
from enum import Enum, auto 


class TRACK_MODE(int, Enum):
    SKY = 2
    ELEV = 3
    USER = 4

class DROT_COMMAND(str, Enum):
    START_TRACK = auto()
    STOP_TRACK  = auto()
    MOVE_ANGLE = auto() 
    

class StartTrack(QtFormular):
    class Config:
        track_mode = QtNodeFactory(
                vtype=(TRACK_MODE,TRACK_MODE.SKY), 
                widget="track_mode"
            )
        angle = QtNodeFactory(
                vtype=float, 
                widget="input_angle"
            )
    def link_action(self, drot: Drot):
        track = Action( drot.start_track, 
                       [self.track_mode, self.angle],
                       feedback=self.feedback  
            )
        self.set_action( track )

class StopTrack(QtFormular):

    def link_action( self, drot:Drot):
        stop = Action(drot.stop_track, feedback=self.feedback)
        self.set_action(stop)

class MoveAngle(QtFormular):
    angle = StartTrack.angle 
    def link_action(self, drot:Drot):
        move = Action(drot.move_angle, [self.angle], feedback = self.feedback)
        self.set_action( move) 

class DrotCommands(QtFormular):
    class Config:
        angle = StartTrack.angle 
        track_mode = StartTrack.track_mode 
        
        menu_drot = QtNodeFactory(vtype=DROT_COMMAND, widget="state_action") 

    def link_action(self, drot: Drot)->None:
        if isinstance(self.actioner, QComboBox):
            def after():
                self.actioner.setCurrentIndex(0)
        else:
            after = None

        drot_action = ActionEnum( after=after)
        drot_action.add_action( 
                    DROT_COMMAND.START_TRACK, 
                    Action( drot.start_track, 
                           [self.track_mode, self.angle], 
                           feedback=self.feedback
                    )
                )
        drot_action.add_action( 
                    DROT_COMMAND.STOP_TRACK, 
                    Action(drot.stop_track, 
                           feedback=self.feedback
                    )
                )
        drot_action.add_action( 
                    DROT_COMMAND.MOVE_ANGLE, 
                    Action(drot.move_angle, 
                        [self.angle], 
                        feedback=self.feedback
                    )
                )
        self.set_action( drot_action) 


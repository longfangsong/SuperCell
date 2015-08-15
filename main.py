from threading import Timer

from ground import GroundViewController, GameDelegate
from user_control import *


class SuperCellViewController(UserControlDelegate, GameDelegate):
    def __init__(self):
        self.view = tkinter.Tk()
        self.ground = GroundViewController(self.view, self)
        self.ground.view.grid(0, 0)
        self.user_control_interface = UserControlView(self, self.view)
        self.user_control_interface.pack(1, 0)
        self.timer = None
        self.speed_changed(0)
        self.view.mainloop()

    def speed_changed(self, speed_val):
        if speed_val == 0:
            self.timer = None
        else:
            self.timer = Timer(1 / speed_val, self.on_timer)
            self.timer.start()


    def can_add_cell(self):
        return self.timer is None

    def cell_added(self):
        pass

    def on_timer(self):
        self.ground.on_timer()
        self.speed_changed(self.user_control_interface.get_speed())


c = SuperCellViewController()
from ground import GroundViewController
from user_control import *


class SuperCellViewController(UserControlDelegate):
    def __init__(self):
        self.view = tkinter.Tk()
        self.ground = GroundViewController(self.view)
        self.ground.view.grid(0, 0)
        self.user_control_interface = UserControlView(self, self.view)
        self.user_control_interface.pack(1, 0)
        self.view.mainloop()


c = SuperCellViewController()
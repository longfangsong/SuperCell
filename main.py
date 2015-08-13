import tkinter
from ground import GroundViewController


class SuperCellViewDelegate:
    @property
    def sub_view(self):
        return None


class SuperCellViewController:
    def __init__(self):
        self.view = tkinter.Tk()
        self.ground = GroundViewController(self.view)
        self.ground.view.grid(0, 0)
        self.view.mainloop()


c = SuperCellViewController()


from threading import Timer
from math import ceil
import pickle

from ground import GroundViewController
from user_control import *


class SuperCellViewController:
    def __init__(self):
        self.__money = 100
        self.view = tkinter.Tk()
        self.ground = GroundViewController(self.view, self)
        self.ground.view.grid(0, 0)
        self.user_control_interface = UserControlView(self, self.view)
        self.view.bind('<KeyPress-,>', lambda _: self.user_control_interface.slower())
        self.view.bind('<KeyPress-.>', lambda _: self.user_control_interface.faster())
        self.view.bind('<KeyPress- >', lambda _: self.user_control_interface.pause())
        self.user_control_interface.grid(1, 0)
        self.timer = None
        self.load()
        self.view.mainloop()

    def speed_changed(self, speed_val):
        if self.timer is not None:
            self.timer.cancel()
        if speed_val == 0:
            self.timer = None
            self.dump()
        else:
            self.timer = Timer(5 / speed_val, self.on_timer)
            self.timer.start()

    def can_add_cell(self):
        return self.timer is None and self.money >= 10

    def cell_added(self):
        self.__money -= 10
        self.user_control_interface.redraw()

    def on_timer(self):
        self.__money += ceil(self.ground.count_cells(("good", "alive")) / 2)
        self.ground.on_timer()
        self.user_control_interface.redraw()
        self.speed_changed(self.user_control_interface.get_speed())

    @property
    def money(self):
        return self.__money

    def can_move_cell(self, distance):
        return self.__money >= distance

    def cell_moved(self, distance):
        self.__money -= distance
        self.user_control_interface.redraw()

    def dump(self):
        with open('save.sav', 'wb') as file:
            pickle.dump(self.__money, file)
            self.ground.dump(file)

    def load(self):
        try:
            with open('save.sav', 'rb') as file:
                self.__money = pickle.load(file)
                self.ground.load(file)
                self.ground.view.redraw()
                self.user_control_interface.redraw()
        except FileNotFoundError:
            pass


c = SuperCellViewController()
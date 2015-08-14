import tkinter


class UserControlDelegate:
    def speed_changed(self, speed_val):
        pass


class UserControlView():
    def __init__(self, delegate_, master_=None):
        assert isinstance(delegate_, UserControlDelegate)
        self.view = tkinter.Frame(master_)
        self.delegate = delegate_
        self.toggle_speed = tkinter.Scale(self.view, orient=tkinter.HORIZONTAL, from_=0, to=100, resolution=1,
                                          label="卷动速度")
        self.toggle_speed.grid(column=0, columnspan=3, row=0)
        slower_button = tkinter.Button(self.view, text="减速", command=self.slower)
        slower_button.grid(column=0, row=1)
        pause_button = tkinter.Button(self.view, text="暂停", command=self.pause)
        pause_button.grid(column=1, row=1)
        faster_button = tkinter.Button(self.view, text="加速", command=self.faster)
        faster_button.grid(column=2, row=1)

    def pause(self):
        self.toggle_speed.set(0)
        self.delegate.speed_changed(0)

    def slower(self):
        self.toggle_speed.set(self.toggle_speed.get() - 5)
        self.delegate.speed_changed(self.toggle_speed.get())

    def faster(self):
        self.toggle_speed.set(self.toggle_speed.get() + 5)
        self.delegate.speed_changed(self.toggle_speed.get())

    def pack(self, col, row_):
        self.view.grid(column=col, row=row_)

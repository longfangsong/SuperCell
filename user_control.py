import tkinter


class UserControlDelegate:
    def speed_changed(self, speed_val):
        pass

    @property
    def money(self):
        return 0


class UserControlView():
    def __init__(self, delegate_, master_=None):
        assert isinstance(delegate_, UserControlDelegate)
        self.view = tkinter.Frame(master_)
        self.delegate = delegate_
        self.toggle_speed = tkinter.Scale(self.view, orient=tkinter.HORIZONTAL, from_=0, to=10, resolution=1,
                                          label="卷动速度",
                                          command=lambda event: self.delegate.speed_changed(self.toggle_speed.get()))
        self.toggle_speed.grid(column=0, columnspan=3, row=1)
        slower_button = tkinter.Button(self.view, text="减速", command=self.slower)
        slower_button.grid(column=0, row=2)
        pause_button = tkinter.Button(self.view, text="暂停", command=self.pause)
        pause_button.grid(column=1, row=2)
        faster_button = tkinter.Button(self.view, text="加速", command=self.faster)
        faster_button.grid(column=2, row=2)
        money_prefix = tkinter.Label(self.view, text="$")
        money_prefix.grid(column=0, row=0)
        self.money_label = tkinter.Label(self.view)
        self.money_label.grid(column=1, columnspan=2, row=0)
        self.redraw()

    def pause(self):
        self.toggle_speed.set(0)

    def slower(self):
        self.toggle_speed.set(self.toggle_speed.get() - 1)

    def faster(self):
        self.toggle_speed.set(self.toggle_speed.get() + 1)

    def grid(self, col, row_):
        self.view.grid(column=col, row=row_)

    def get_speed(self):
        return self.toggle_speed.get()

    def redraw(self):
        self.money_label["text"] = "%d" % self.delegate.money

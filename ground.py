import random
import tkinter
from math import sqrt, degrees, asin

import cell


class Ground:
    """
    场地的Model部分
    """
    MAX_COL = 15  # y
    MAX_ROW = 15  # x

    def __init__(self):
        self.__cells = []
        for i in range(0, Ground.MAX_ROW):
            self.__cells.append([])
            for j in range(0, Ground.MAX_COL):
                self.__cells[i].append(None)

    def add_cell(self, x, y, new_cell=None):
        if new_cell is None:
            new_cell = cell.Cell()
        assert 0 <= x < Ground.MAX_ROW and 0 <= y < Ground.MAX_COL
        assert self.__cells[x][y] is None
        self.__cells[x][y] = new_cell

    def __count_cells_around(self, x, y, count_what="all"):
        assert self.__cells[x][y] is not None
        ret = 0
        for xx in range(x - 1 if x - 1 >= 0 else 0, (x + 1 if x + 1 < Ground.MAX_ROW else Ground.MAX_ROW - 1) + 1):
            for yy in range(y - 1 if y - 1 >= 0 else 0, (y + 1 if y + 1 < Ground.MAX_COL else Ground.MAX_COL - 1) + 1):
                if self.__cells[xx][yy]:
                    if count_what == "all":
                        if self.__cells[xx][yy]:
                            ret += 1
                    elif count_what == "enemy":
                        if self.__cells[xx][yy] and self.__cells[xx][yy].bad != self.__cells[x][y].bad:
                            ret += 1
                    elif count_what == "friend":
                        if self.__cells[xx][yy] and self.__cells[xx][yy].bad == self.__cells[x][y].bad:
                            ret += 1
                    else:
                        raise ValueError
        return ret if count_what == "enemy" else ret - 1  # 数全部和我方时需要除去自己

    def __empty_grid_near(self, x, y):
        ret = []
        for xx in range(x - 1 if x - 1 >= 0 else 0, x + 1 if x + 1 < Ground.MAX_ROW else Ground.MAX_ROW - 1):
            for yy in range(y - 1 if y - 1 >= 0 else 0, y + 1 if y + 1 < Ground.MAX_COL else Ground.MAX_COL - 1):
                if self.__cells[xx][yy] is None:
                    ret.append((xx, yy))
        return ret

    def __do_life_game_rule(self, x, y):
        if self.__count_cells_around(x, y, "friend") <= 3:
            self.__cells[x][y].minus_hp(3 - self.__count_cells_around(x, y, "friend"))
        elif self.__count_cells_around(x, y, "friend") >= 5:
            self.__cells[x][y].minus_hp(self.__count_cells_around(x, y, "friend") - 5)
        else:
            self.__cells[x][y].add_hp(1)

    def __find_random_nearby_enemy_cell(self, x, y):
        enemies = []
        for xx in range(x - 1 if x - 1 >= 0 else 0, (x + 1 if x + 1 < Ground.MAX_ROW else Ground.MAX_ROW - 1) + 1):
            for yy in range(y - 1 if y - 1 >= 0 else 0, (y + 1 if y + 1 < Ground.MAX_COL else Ground.MAX_COL - 1) + 1):
                if self.__cells[xx][yy] and self.__cells[xx][yy].bad != self.__cells[x][y].bad:
                    enemies.append((xx, yy))
        return random.sample(enemies, 1)[0] if enemies else None

    def __fight(self, x, y):
        if not self.__find_random_nearby_enemy_cell(x, y):
            return
        xx, yy = self.__find_random_nearby_enemy_cell(x, y)
        self.__cells[xx][yy].hurt(self.__cells[x][y].attack)
        self.__cells[x][y].minus_energy(self.__cells[x][y].attack)

    def __find_random_nearby_cell_to_breed(self, x, y):
        to_breed = []
        for xx in range(x - 1 if x - 1 >= 0 else 0, (x + 1 if x + 1 < Ground.MAX_ROW else Ground.MAX_ROW - 1) + 1):
            for yy in range(y - 1 if y - 1 >= 0 else 0, (y + 1 if y + 1 < Ground.MAX_COL else Ground.MAX_COL - 1) + 1):
                if (xx, yy) != (x, y) \
                        and self.__cells[xx][yy] is not None and self.__cells[xx][yy].bad == self.__cells[x][y].bad and \
                        self.__cells[xx][yy].can_breed:
                    to_breed.append((xx, yy))
        return random.sample(to_breed, 1)[0] if to_breed else None

    def __find_random_nearby_empty_grid(self, x, y, passed=None):
        grid = []
        for xx in range(x - 1 if x - 1 >= 0 else 0, x + 1 if x + 1 < Ground.MAX_ROW else Ground.MAX_ROW - 1):
            for yy in range(y - 1 if y - 1 >= 0 else 0, y + 1 if y + 1 < Ground.MAX_COL else Ground.MAX_COL - 1):
                if self.__cells[xx][yy] is None and (True if passed is None else (xx, yy) not in passed):
                    grid.append((xx, yy))
        return random.sample(grid, 1)[0] if grid else None

    def __try_breed(self, x, y):
        b = self.__find_random_nearby_cell_to_breed(x, y)
        t = self.__find_random_nearby_empty_grid(x, y)
        if b is None or t is None:
            return
        bx, by = b
        tx, ty = t
        assert self.__cells[bx][by].bad == self.__cells[x][y].bad and self.__cells[tx][ty] is None
        self.__cells[tx][ty] = cell.Cell(self.__cells[x][y], self.__cells[bx][by])

    def __move(self, x, y):
        passed = set()
        d = self.__cells[x][y].movable_distance
        for step in range(0, d):
            if self.__find_random_nearby_empty_grid(x, y, passed):
                xx, yy = self.__find_random_nearby_empty_grid(x, y, passed)
                self.__cells[x][y], self.__cells[xx][yy] = None, self.__cells[x][y]
                passed.add((xx, yy))
                x, y = xx, yy
                self.__cells[x][y].minus_energy(1)

    def round(self):
        for x, row in enumerate(self.__cells):
            for y, the_cell in enumerate(row):
                if the_cell is not None:
                    the_cell.round()
                    self.__fight(x, y)
                    self.__do_life_game_rule(x, y)
                    if the_cell.really_dead:
                        self.__cells[x][y] = None
                        continue
                    if self.__cells[x][y].can_breed:
                        self.__try_breed(x, y)
                    self.__move(x, y)

    def get_cell_info_at(self, x, y):
        if self.__cells[x][y] is None:
            return None
        return (not self.__cells[x][y].bad), self.__cells[x][y].hp_percent

    def is_empty(self, x, y):
        return self.__cells[x][y] is None

    def count_cells(self, option):
        count = 0
        for l in self.__cells:
            for c in l:
                if c is None:
                    continue
                if "good" in option:
                    if "alive" in option:
                        if not c.bad and not c.nearly_dead:
                            count += 1
                    elif "dead" in option:
                        if not c.bad and c.nearly_dead:
                            count += 1
                    else:
                        if not c.bad:
                            count += 1
                elif "bad" in option:
                    if "alive" in option:
                        if c.bad and not c.nearly_dead:
                            count += 1
                    elif "dead" in option:
                        if c.bad and c.nearly_dead:
                            count += 1
                    else:
                        if c.bad:
                            count += 1
        return count


class GroundViewDelegate:
    def get_size(self):
        pass

    def get_cell_info_at(self, x, y):
        pass

    @staticmethod
    def model_coord(x, y):
        pass

    @staticmethod
    def view_coord(x, y):
        pass

    def on_click(self, event):
        pass


class GroundView:
    CELL_RADIUS = 20

    def __init__(self, delegate, master_):
        self.delegate = delegate
        assert isinstance(self.delegate, GroundViewDelegate)
        size = self.delegate.get_size()
        self.__canvas = tkinter.Canvas(master_, width=(GroundView.CELL_RADIUS * 1.2 * 2 + 1) * 15 + 11,
                                       height=(GroundView.CELL_RADIUS * 1.2 * 2 + 1) * 15 + 11, bg='white')
        self.__canvas.bind('<Button-1>', delegate.on_click)
        for x in range(size[0] + 1):
            self.__canvas.create_line(5, x * GroundView.CELL_RADIUS * 1.2 * 2 + 5,
                                      15 * GroundView.CELL_RADIUS * 1.2 * 2 + 5,
                                      x * GroundView.CELL_RADIUS * 1.2 * 2 + 5)
        for y in range(size[1] + 1):
            self.__canvas.create_line(y * GroundView.CELL_RADIUS * 1.2 * 2 + 5, 5,
                                      y * GroundView.CELL_RADIUS * 1.2 * 2 + 5,
                                      15 * GroundView.CELL_RADIUS * 1.2 * 2 + 5)
        self.__canvas.grid(row=1, column=1)

    def draw_cell(self, x, y, is_good, percent):
        arc_coord = x - GroundView.CELL_RADIUS, y - GroundView.CELL_RADIUS, x + GroundView.CELL_RADIUS, y + GroundView.CELL_RADIUS
        delta_h = 2 * GroundView.CELL_RADIUS * abs(percent) - GroundView.CELL_RADIUS
        delta_x = sqrt(abs(GroundView.CELL_RADIUS * GroundView.CELL_RADIUS - delta_h * delta_h))
        self.__canvas.create_oval(arc_coord, fill='white')
        if percent >= 0.1:
            if percent >= 0.99:
                self.__canvas.create_oval(arc_coord, fill='green', outline='black' if is_good else 'red')
            else:
                r = (int(510 - 510 * percent) if percent >= 0.5 else 255) * 16 * 16 * 16 * 16
                g = int(255 if percent >= 0.5 else percent * 2 * 255) * 16 * 16
                c = '#%06x' % (r + g)
                tri_coord = x - delta_x, y - delta_h, \
                            x + delta_x, y - delta_h, \
                            x, y
                self.__canvas.create_arc(arc_coord, start=degrees(asin(2 * percent - 1)),
                                         extent=-180 - 2 * degrees(asin(2 * percent - 1)), fill=c,
                                         outline=c)
                self.__canvas.create_polygon(tri_coord, fill=c if percent >= 0.5 else 'white',
                                             outline=c if percent >= 0.5 else 'white', width=1 if percent > 0.5 else 2)
        elif percent <= -0.1:
            if percent <= - 0.99:
                self.__canvas.create_oval(arc_coord, fill='grey', outline='black' if is_good else 'red')
            else:
                tri_coord = x - delta_x, y + delta_h, \
                            x + delta_x, y + delta_h, \
                            x, y
                self.__canvas.create_arc(arc_coord, start=-degrees(asin(2 * -percent - 1)),
                                         extent=180 + 2 * degrees(asin(2 * -percent - 1)), fill='grey', outline='grey')
                self.__canvas.create_polygon(tri_coord, fill='grey' if -percent >= 0.5 else 'white',
                                             outline='grey' if -percent >= 0.5 else 'white',
                                             width=1 if abs(percent) > 0.5 else 3)
        self.__canvas.create_oval(arc_coord, outline='black' if is_good else 'red')

    def clear(self, x, y):
        arc_coord = x - GroundView.CELL_RADIUS, y - GroundView.CELL_RADIUS, x + GroundView.CELL_RADIUS, y + GroundView.CELL_RADIUS
        self.__canvas.create_oval(arc_coord, fill='white', outline='white', width=3)

    def redraw(self):
        size = self.delegate.get_size()
        for x in range(size[0]):
            for y in range(size[1]):
                x_, y_ = self.delegate.view_coord(x, y)
                if self.delegate.get_cell_info_at(x, y) is None:
                    self.clear(x_, y_)
                else:
                    good, percent = self.delegate.get_cell_info_at(x, y)
                    self.draw_cell(x_, y_, good, percent)

    def grid(self, raw, col):
        self.__canvas.grid(column=col, row=raw)


class GameDelegate:
    def can_add_cell(self):
        pass

    def cell_added(self):
        pass


class GroundViewController(GroundViewDelegate):
    def on_timer(self):
        print("Called")
        self.__model.round()
        self.view.redraw()

    def __init__(self, master_view, delegate_):
        assert isinstance(delegate_, GameDelegate)
        self.__model = Ground()
        self.view = GroundView(self, master_view)
        self.delegate = delegate_

    def get_size(self):
        return self.__model.MAX_ROW, self.__model.MAX_COL

    def get_cell_info_at(self, x, y):
        return self.__model.get_cell_info_at(x, y)

    @staticmethod
    def model_coord(x, y):
        return int((x - 5) // (GroundView.CELL_RADIUS * 1.2 * 2)), int((y - 5) // (GroundView.CELL_RADIUS * 1.2 * 2))

    @staticmethod
    def view_coord(x, y):
        return x * GroundView.CELL_RADIUS * 1.2 * 2 + GroundView.CELL_RADIUS * 1.2 + 5, y * GroundView.CELL_RADIUS * 1.2 * 2 + GroundView.CELL_RADIUS * 1.2 + 5

    def on_click(self, event):
        mx, my = self.model_coord(event.x, event.y)
        if self.delegate.can_add_cell() and self.__model.is_empty(mx, my):
            self.__model.add_cell(mx, my)
            self.view.redraw()
            self.delegate.cell_added()

    def count_cells(self, option):
        return self.__model.count_cells(option)

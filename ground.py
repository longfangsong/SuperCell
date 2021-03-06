import random
import tkinter
import pickle
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
        """
        添加新细胞
        :param x: 添加的位置的x坐标
        :param y: 添加的位置的y坐标
        :param new_cell: 要添加的细胞，若为None（默认值）则会自动生成一个新细胞
        """
        assert 0 <= x < Ground.MAX_ROW and 0 <= y < Ground.MAX_COL
        assert self.__cells[x][y] is None
        if new_cell is None:
            new_cell = cell.Cell()
        self.__cells[x][y] = new_cell

    @staticmethod
    def __grids_near(x, y):
        """
        生成器，枚举某一个细胞附近所有的坐标
        :param x: 细胞的x坐标
        :param y: 细胞的y坐标
        :return: 生成器生成附近每一个细胞的坐标
        """
        for xx in range(x - 1 if x - 1 >= 0 else 0, x + 2 if x + 1 < Ground.MAX_ROW else Ground.MAX_ROW):
            for yy in range(y - 1 if y - 1 >= 0 else 0, y + 2 if y + 1 < Ground.MAX_COL else Ground.MAX_COL):
                if xx == x and yy == y:
                    continue
                else:
                    yield (xx, yy)

    def __count_cells_around(self, x, y, count_what="all"):
        """
        数某一个细胞附近符合条件的细胞
        :param x: 细胞的x坐标
        :param y: 细胞的y坐标
        :param count_what: 数的条件:
            all: 所有细胞
            enemy: 敌方细胞
            friend: 我方细胞
        :return: 符号条件的细胞个数
        """
        assert self.__cells[x][y] is not None
        ret = 0
        for xx, yy in Ground.__grids_near(x, y):
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
        return ret

    def __empty_grid_near(self, x, y):
        ret = []
        for xx, yy in Ground.__grids_near(x, y):
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
        for xx, yy in Ground.__grids_near(x, y):
            if self.__cells[xx][yy] is not None and self.__cells[xx][yy].bad != self.__cells[x][y].bad:
                enemies.append((xx, yy))
        return random.sample(enemies, 1)[0] if enemies else None

    def __fight(self, x, y):
        enemy = self.__find_random_nearby_enemy_cell(x, y)
        if enemy is None:
            return
        xx, yy = enemy
        self.__cells[xx][yy].hurt(self.__cells[x][y].attack)
        self.__cells[x][y].minus_energy(self.__cells[x][y].attack)

    def __find_random_nearby_cell_to_breed(self, x, y):
        to_breed = []
        for xx, yy in Ground.__grids_near(x, y):
            if self.__cells[xx][yy] is not None and self.__cells[xx][yy].bad == self.__cells[x][y].bad and \
                    self.__cells[xx][yy].can_breed:
                to_breed.append((xx, yy))
        return random.sample(to_breed, 1)[0] if to_breed else None

    def __find_random_nearby_empty_grid(self, x, y, passed):
        grid = []
        for xx, yy in Ground.__grids_near(x, y):
            if self.__cells[xx][yy] is None and (xx, yy) not in passed:
                grid.append((xx, yy))
        return random.sample(grid, 1)[0] if grid else None

    def __try_breed(self, x, y):
        breed_with = self.__find_random_nearby_cell_to_breed(x, y)
        birth_to = self.__find_random_nearby_empty_grid(x, y, set())
        if breed_with is None or birth_to is None:
            return
        else:
            bx, by = breed_with
            tx, ty = birth_to
            self.__cells[tx][ty] = cell.Cell(self.__cells[x][y], self.__cells[bx][by])

    def __move(self, x, y):
        passed = set()
        passed.add((x, y))
        d = self.__cells[x][y].movable_distance
        for step in range(0, d):
            grid_to_go = self.__find_random_nearby_empty_grid(x, y, passed)
            if grid_to_go is not None:
                xx, yy = grid_to_go
                self.__cells[x][y], self.__cells[xx][yy] = None, self.__cells[x][y]
                passed.add((xx, yy))
                x, y = xx, yy
                self.__cells[x][y].minus_energy(1)
            else:
                break

    def round(self):
        for x, row in enumerate(self.__cells):
            for y, the_cell in enumerate(row):
                if the_cell is not None:
                    the_cell.round()
                    self.__fight(x, y)
                    if not the_cell.bad:
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

    def move_cell(self, x0, y0, x, y):
        if self.__cells[x0][y0] is not None and self.__cells[x][y] is None and not self.__cells[x0][y0].bad:
            self.__cells[x0][y0], self.__cells[x][y] = None, self.__cells[x0][y0]
            return True
        return False


class GroundView:
    CELL_RADIUS = 20

    def __init__(self, delegate, master_):
        assert hasattr(delegate, 'get_size')
        assert hasattr(delegate, 'get_cell_info_at')
        assert hasattr(delegate, 'model_coord')
        assert hasattr(delegate, 'view_coord')
        assert hasattr(delegate, 'on_click')
        assert hasattr(delegate, 'on_drag_release')
        self.delegate = delegate
        size = self.delegate.get_size()
        grid_size = GroundView.CELL_RADIUS * 1.2 * 2
        self.__canvas = tkinter.Canvas(master_, width=(grid_size + 1) * 15 + 11,
                                       height=(grid_size + 1) * 15 + 11, bg='white')
        self.__canvas.bind('<Button-1>', self.delegate.on_click)
        self.__canvas.bind('<ButtonRelease-1>', self.delegate.on_drag_release)
        for x in range(size[0] + 1):
            self.__canvas.create_line(5, x * grid_size + 5,
                                      15 * grid_size + 5, x * grid_size + 5)
        for y in range(size[1] + 1):
            self.__canvas.create_line(y * grid_size + 5, 5,
                                      y * grid_size + 5, 15 * grid_size + 5)
        self.__canvas.grid(row=1, column=1)
        self.__buffer = []
        for i in range(0, size[0]):
            self.__buffer.append([])
            for j in range(0, size[1]):
                self.__buffer[i].append(None)

    def __draw_cell(self, x, y, is_good, percent):  # horrible graphic code,don't touch it unless you are very sure
        arc_coord = x - GroundView.CELL_RADIUS, y - GroundView.CELL_RADIUS, \
                    x + GroundView.CELL_RADIUS, y + GroundView.CELL_RADIUS
        delta_h = 2 * GroundView.CELL_RADIUS * abs(percent) - GroundView.CELL_RADIUS
        delta_x = sqrt(abs(GroundView.CELL_RADIUS * GroundView.CELL_RADIUS - delta_h * delta_h))
        self.__canvas.create_oval(arc_coord, fill='white')
        if percent >= 0.1:
            if percent >= 0.99:
                self.__canvas.create_oval(arc_coord, fill='green', outline='black' if is_good else 'red')
            else:
                r = (int(510 - 510 * percent) if percent >= 0.5 else 255) * 16 * 16 * 16 * 16
                g = int(255 if percent >= 0.5 else percent * 2 * 255) * 16 * 16
                color = '#%06x' % (r + g)
                tri_coord = x - delta_x, y - delta_h, \
                            x + delta_x, y - delta_h, \
                            x, y
                self.__canvas.create_arc(arc_coord, start=degrees(asin(2 * percent - 1)),
                                         extent=-180 - 2 * degrees(asin(2 * percent - 1)), fill=color,
                                         outline=color)
                self.__canvas.create_polygon(tri_coord, fill=color if percent >= 0.5 else 'white',
                                             outline=color if percent >= 0.5 else 'white',
                                             width=1 if percent > 0.5 else 2)
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

    def __clear(self, x, y):
        arc_coord = x - GroundView.CELL_RADIUS, y - GroundView.CELL_RADIUS, x + GroundView.CELL_RADIUS, y + GroundView.CELL_RADIUS
        self.__canvas.create_oval(arc_coord, fill='white', outline='white', width=3)

    def redraw(self):
        size = self.delegate.get_size()
        for x in range(size[0]):
            for y in range(size[1]):
                info = self.delegate.get_cell_info_at(x, y)
                if info == self.__buffer[x][y]:
                    continue
                self.__buffer[x][y] = info
                x_, y_ = self.delegate.view_coord(x, y)
                if info is None:
                    self.__clear(x_, y_)
                else:
                    good, percent = info
                    self.__draw_cell(x_, y_, good, percent)

    def grid(self, raw, col):
        self.__canvas.grid(column=col, row=raw)


class GroundViewController:
    def __init__(self, master_view, delegate_):
        assert hasattr(delegate_, 'can_add_cell')
        assert hasattr(delegate_, 'cell_added')
        assert hasattr(delegate_, 'can_move_cell')
        self.__model = Ground()
        self.view = GroundView(self, master_view)
        self.delegate = delegate_
        self.__drag_begin_pos = (-1, -1)

    def on_timer(self):
        self.__model.round()
        self.view.redraw()

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

    def on_drag_release(self, event):
        mx, my = GroundViewController.model_coord(event.x, event.y)
        if self.model_coord(self.__drag_begin_pos[0], self.__drag_begin_pos[1]) == self.model_coord(event.x, event.y):
            self.__drag_begin_pos = (-1, -1)
        elif self.delegate.can_move_cell(abs(self.__drag_begin_pos[0] - mx) + abs(self.__drag_begin_pos[1] - my)):
            if self.__model.move_cell(self.__drag_begin_pos[0], self.__drag_begin_pos[1],
                                      GroundViewController.model_coord(event.x, event.y)[0],
                                      GroundViewController.model_coord(event.x, event.y)[1]):
                self.delegate.cell_moved(abs(self.__drag_begin_pos[0] - mx) + abs(self.__drag_begin_pos[1] - my))
                self.__drag_begin_pos = (-1, -1)
                self.view.redraw()

    def on_click(self, event):
        mx, my = self.model_coord(event.x, event.y)
        if self.delegate.can_add_cell() and self.__model.is_empty(mx, my):
            self.__model.add_cell(mx, my)
            self.view.redraw()
            self.delegate.cell_added()
        elif not self.__model.is_empty(mx, my):
            self.__drag_begin_pos = mx, my

    def count_cells(self, option):
        return self.__model.count_cells(option)

    def dump(self, file):
        pickle.dump(self.__model, file, 2)

    def load(self, file):
        self.__model = pickle.load(file)

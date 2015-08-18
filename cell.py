import random


class Cell:
    """
    细胞的Model部分
    """
    max_experience = 65536

    def __init__(self, father=None, mother=None):
        self.__hp_max = 5
        self.__hp = 5
        self.__hp_variation_rate = 0.1
        self.__energy_max = 10
        self.__energy = 10
        self.__energy_variation_rate = 0.1
        self.__attack = 5
        self.__attack_variation_rate = 0.1
        self.__defence = 3
        self.__defence_variation_rate = 0.1
        self.__variation_rate = 0.01
        self.__breed_will = 1 / 20
        self.__experience = 0
        self.__level = 1
        self.__bad = False
        self.__harm_of_round = 0
        if father and mother:
            # 各项个体值随机来自某个亲本
            assert father.__bad == mother.__bad
            self.__hp_variation_rate = (father if random.randint(0, 1) == 0 else mother).__hp_variation_rate
            self.__energy_variation_rate = (father if random.randint(0, 1) == 0 else mother).__energy_variation_rate
            self.__attack_variation_rate = (father if random.randint(0, 1) == 0 else mother).__attack_variation_rate
            self.__defence_variation_rate = (father if random.randint(0, 1) == 0 else mother).__defence_variation_rate
            self.__breed_will = (father if random.randint(0, 1) == 0 else mother).__breed_will
            self.__variation_rate = (father if random.randint(0, 1) == 0 else mother).__variation_rate
            # 提升双亲能力值之和最高的那项的个体值
            elements = [
                father.__hp_max + mother.__hp_max,
                father.__energy_max + mother.__energy_max,
                father.__defence + mother.__defence,
                father.__attack + mother.__attack,
                father.__breed_will * 2 + mother.__breed_will * 2,
                father.__variation_rate * 10 + mother.__variation_rate * 10
            ]
            if max(elements) == elements[0]:  # hp
                self.__hp_variation_rate *= 1.1
            elif max(elements) == elements[1]:  # energy
                self.__energy_variation_rate *= 1.1
            elif max(elements) == elements[2]:  # defence
                self.__defence_variation_rate *= 1.1
            elif max(elements) == elements[3]:  # attack
                self.__attack_variation_rate *= 1.1
            elif max(elements) == elements[4]:  # breed_will
                self.__breed_will = (self.__breed_will * 2 * 1.1) / 2
            elif max(elements) == elements[5]:  # variation
                self.__variation_rate = (self.__variation_rate * 10 * 1.1) / 10
                if self.__variation_rate > 0.35:
                    self.__variation_rate = 0.35
            # 随机提升一项个体值
            element = random.randint(0, 5)
            if element == 0:
                self.__hp_variation_rate *= 1.05
            elif element == 1:
                self.__hp_variation_rate *= 1.05
            elif element == 2:
                self.__defence_variation_rate *= 1.05
            elif element == 3:
                self.__attack_variation_rate *= 1.05
            elif element == 4:
                self.__breed_will = (self.__breed_will * 2 * 1.05) / 2
            elif element == 5:
                self.__variation_rate = (self.__variation_rate * 10 * 1.05) / 10
            # 随机降低一项个体值
            element = random.randint(0, 5)
            if element == 0:
                self.__hp_variation_rate *= 0.95
            elif element == 1:
                self.__hp_variation_rate *= 0.95
            elif element == 2:
                self.__defence_variation_rate *= 0.95
            elif element == 3:
                self.__attack_variation_rate *= 0.95
            elif element == 4:
                self.__breed_will = (self.__breed_will * 2 * 0.95) / 2
            elif element == 5:
                self.__variation_rate = (self.__variation_rate * 10 * 0.95) / 10
            # 确保各项值都在范围内
            if self.__hp_variation_rate > 1:
                self.__hp_variation_rate = 1
            elif self.__hp_variation_rate < 0.0001:
                self.__hp_variation_rate = 0.0001

            if self.__energy_variation_rate > 1:
                self.__energy_variation_rate = 1
            elif self.__energy_variation_rate < 0.0001:
                self.__energy_variation_rate = 0.0001

            if self.__defence_variation_rate > 1:
                self.__defence_variation_rate = 1
            elif self.__defence_variation_rate < 0.0001:
                self.__defence_variation_rate = 0.0001

            if self.__attack_variation_rate > 1:
                self.__attack_variation_rate = 1
            elif self.__attack_variation_rate < 0.0001:
                self.__attack_variation_rate = 0.0001

            if self.__breed_will > 0.5:
                self.__breed_will = 0.5
            elif self.__breed_will < 0.01:
                self.__breed_will = 0.01

            if self.__variation_rate > 0.35:
                self.__variation_rate = 0.35
            elif self.__variation_rate < 0.00001:
                self.__variation_rate = 0.00001
            # 亲本体力减为0
            father.__energy = 0
            mother.__energy = 0

    @property
    def bad(self):
        return self.__bad

    @bad.setter
    def bad(self, val):
        """
        设置细胞的好坏
        :type val: bool
        """
        assert self.__bad != val
        if val:
            self.__bad = True
            self.__hp_max *= 2
            self.__hp *= 2
            self.__energy_max *= 2
            self.__energy *= 2
            self.__attack *= 3
            self.__defence //= 3
            self.__variation_rate *= 0.1
        else:
            self.__bad = False
            if random.randint(0, 100) != 0:
                self.__hp_max //= 2
                self.__hp //= 2
            if random.randint(0, 100) != 0:
                self.__energy_max //= 2
                self.__energy //= 2
            if random.randint(0, 200) != 0:
                self.__attack //= 3
            if random.randint(0, 300) != 0:
                self.__defence *= 3
            self.__variation_rate *= 9
            if self.__variation_rate > 0.35:
                self.__variation_rate = 0.35

    def hurt(self, harm):
        """
        对细胞进行攻击
        :param harm: 对细胞造成的伤害
        """
        harm -= self.__defence
        if harm <= 0:
            return
        else:
            self.__hp -= harm
            self.__harm_of_round = harm
            self.__variation_rate += harm / 1000
            if self.__variation_rate > 0.35:
                self.__variation_rate = 0.35

    @property
    def nearly_dead(self):
        """
        :return: 细胞是否处于濒死状态
        """
        return self.__hp <= 0

    @property
    def really_dead(self):
        """
        :return: 细胞是否处于死亡状态
        """
        return self.__hp < -self.hp_max

    @property
    def hp_percent(self):
        """
        :return: 细胞血量的百分比
        """
        return self.__hp / self.hp_max

    @property
    def hp(self):
        return self.__hp

    def minus_hp(self, val):
        """
        给细胞减血，绕过变异率的改变，但没有绕过回合伤害累计
        :param val: 减血的量
        """
        self.__hp -= val
        self.__harm_of_round += val

    def add_hp(self, val):
        self.__hp += val
        self.__variation_rate -= val / 1000
        if self.__variation_rate <= 0.001:
            self.__variation_rate = 0.001
        if self.__hp > self.hp_max:
            self.__hp = self.hp_max

    @property
    def usable_energy(self):
        return self.__energy if not self.nearly_dead else 0

    def minus_energy(self, val):
        """
        减少细胞的能量
        :param val: 减能量减少量
        """
        assert self.__energy >= val
        self.__energy -= val

    def add_energy(self, val):
        self.__energy += val
        if self.__energy > self.__energy_max:
            self.__energy = self.__energy_max

    @property
    def attack(self):
        return self.attack

    @property
    def __need_variation(self):
        return random.random() <= self.__variation_rate

    @property
    def __need_upgrade(self):
        if self.__level >= 100:
            return False
        return True if self.__experience >= 20 - 3.5 * (self.__level + 18) + 0.132 * (self.__level + 18) * (
            self.__level + 18) else False

    @property
    def level(self):
        return self.__level

    def upgrade(self):
        assert self.__need_upgrade
        self.__level += 1
        if random.random() < self.__hp_variation_rate:
            self.__hp += 1
        if random.random() < self.__energy_variation_rate:
            self.__energy += 1
        if random.random() < self.__attack_variation_rate:
            self.__attack += 1
        if random.random() < self.__defence_variation_rate:
            self.__defence += 1

    def add_experience(self, val):
        """
        :param val: 增加经验的量
        """
        self.__experience += val
        if self.__experience > Cell.max_experience:
            self.__experience = Cell.max_experience

    @property
    def hp_max(self):
        return self.__hp_max

    @property
    def energy_max(self):
        return self.__energy_max

    @property
    def attack(self):
        return self.__attack if self.usable_energy > self.__attack else self.usable_energy

    @property
    def defence(self):
        return self.__defence

    def round(self):
        # 增加能量，能量已满则加血
        if self.__energy == self.__energy_max:
            if self.__hp < self.__hp_max and random.randint(0, 1) == 0:
                self.__hp += 1
        else:
            self.__energy += 1
        # 变异
        if self.__need_variation:
            self.bad = not self.bad
        # 升级
        if self.__need_upgrade:
            self.upgrade()
        # 清当前回合损伤计数器
        self.__harm_of_round = 0

    @property
    def movable_distance(self):
        """
        细胞该回合可移动的距离
        :rtype : int
        """
        if self.nearly_dead:
            return 0
        else:
            return self.usable_energy if self.usable_energy < self.__harm_of_round else self.__harm_of_round

    @property
    def can_breed(self):
        return random.randint(0, int(
            1 / self.__breed_will)) == 0 and self.__harm_of_round == 0 and self.usable_energy == self.__energy_max
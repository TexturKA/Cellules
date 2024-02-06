import numpy as np
from PIL import Image


class Pos:
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y
        self.xy = self.x, self.y


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r, self.g, self.b = r, g, b
        self.rgb = self.r, self.g, self.b

    def hex(self):
        return "#" + "".join(map(lambda x: hex(x)[2:].rjust(2, "0"), self.rgb))


class Pixel:
    def __init__(self, pos: Pos, color: Color):
        self.pos = pos
        self.color = color

    def get(self):
        return self.pos.xy, self.color.rgb


class Picture:
    """
    Основные вычисления только с matrix,
    image только для отображения
    """
    def __init__(self, resolution: tuple[int, int]):
        self.image = Image.new('RGB', resolution, (0, 0, 0))
        self.matrix = self.update_matrix()

    def update_image(self):
        self.image = Image.fromarray(self.matrix)
        return self.image

    def update_matrix(self):
        self.matrix = np.array(self.image)
        return self.matrix

    def save_image(self, dir_path, file_name, ):
        self.image.save(f'{dir_path}/{file_name}.png', "PNG")


class Action:
    """Класс движения, отвечает за движения заданного объекта по координатной оси"""
    def __init__(self, action_object, direction: int):
        """Возможные стороны перемещения: 0-UL 1-U 2-UR 3-R 4-DR 5-D 6-DL 7-L"""
        # Объект, который будет двигаться
        self.obj = action_object
        self.steps_counter = 0

        # Направление движения
        if not 0 <= direction <= 7:
            raise
        self.dir = direction
        self.prt = 0
        self.ang = 0

        # Возможные стороны для перемещения объекта
        self.sides = [None] * 8
        self.set_sides()

    def turn_left(self):
        """Изменение направления движения на 1 пункт влево"""
        self.dir -= 1
        if self.dir < 0:
            self.dir = 7

    def turn_right(self):
        """Изменение направления движения на 1 пункт влево"""
        self.dir += 1
        if self.dir > 7:
            self.dir = 0

    def turn_course(self):
        course = 0
        while True:
            if self.dir + course < 4:
                course += 1
            elif self.dir + course > 4:
                course -= 1
            else:
                break
        if (self.prt + course) % 8 > 4:
            self.turn_right()
        else:
            self.turn_left()

    def step(self) -> Pos:
        """Перемещение объекта по координатной оси по направлению движения"""
        self.set_sides()
        old_object_pos = self.obj.pos
        for side in range(len(self.sides)):
            self.obj.pos = self.sides[side]
        self.steps_counter += 1
        return old_object_pos

    def set_priority(self, clan_pos):
        """Рассчёт направления движения к точке базирования объектов"""
        obj_pos = self.obj.pos
        n = Pos(obj_pos.x - clan_pos.x, obj_pos.y - clan_pos.y)
        if n.x != 0:
            a = np.ma.arctan(abs(n.y) / abs(n.x)) / np.pi * 180
        else:
            a = 90
        if n.x > 0 and n.y < 0:
            area = 0
        elif n.x > 0 and n.y > 0:
            area = 1
        elif n.x < 0 and n.y > 0:
            area = 2
        else:
            area = 3
        if 0 <= a < 22.5:
            if area in [0, 1]:
                self.prt = 6
            else:
                self.prt = 2
        elif 22.5 <= a < 67.5:
            if area == 0:
                self.prt = 5
            elif area == 1:
                self.prt = 7
            elif area == 2:
                self.prt = 1
            elif area == 3:
                self.prt = 3
        else:
            if area in [1, 2]:
                self.prt = 0
            else:
                self.prt = 4
        self.ang = a

    def set_sides(self):
        obj_pos = self.obj.pos
        self.sides = [
            Pos(obj_pos.x - 1, obj_pos.y - 1),
            Pos(obj_pos.x + 0, obj_pos.y - 1),
            Pos(obj_pos.x + 1, obj_pos.y - 1),
            Pos(obj_pos.x + 1, obj_pos.y + 0),
            Pos(obj_pos.x + 1, obj_pos.y + 1),
            Pos(obj_pos.x - 0, obj_pos.y + 1),
            Pos(obj_pos.x - 1, obj_pos.y + 1),
            Pos(obj_pos.x - 1, obj_pos.y - 0),
        ]


class Clan:
    def __init__(self, name: str, base_pos: Pos, color: Color):
        self.name = name
        self.pos = base_pos
        self.color = color


class Cell:
    def __init__(self, position: Pos, clan: Clan, species: dict = None):
        self.pos = position
        self.clan = clan
        self.species = species or {}
        self.action = Action(self, species.get("direction") or 0)

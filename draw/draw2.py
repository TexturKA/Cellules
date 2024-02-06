import numpy as np
from PIL import Image
from PySide6.QtCore import QThread

from general import CelluesApplication
from models import Picture, Cell, Clan, Pos, Pixel, Action, Color


def darkening(color: Color, degree: float) -> Color:
    return Color(*(round(i / degree) for i in color.rgb if i >= 0))


def random_color(threshold: int = 200) -> Color:
    return Color(
        np.random.randint(threshold, 256),
        np.random.randint(threshold, 256),
        np.random.randint(0, 256)
    )


def convert_base(num, to_base=10, from_base=10):
    n = int(num, from_base) if isinstance(num, str) else int(num)
    alph = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alph[n]
    return convert_base(n // to_base, to_base) + alph[n % to_base]


def operations(service: CelluesApplication, threads: list):
    spawn_point = Pos(
        np.random.randint(
            service.width // 4,
            service.width - (service.width // 4)),
        np.random.randint(
            service.height // 4,
            service.height - (service.height // 4))
    )
    spawn_clan = Clan('clan.FFFFFF', spawn_point, Color(255, 255, 255))
    spawn_cell = Cell(spawn_point, spawn_clan, {"direction": np.random.randint(0, 8)})
    service.cells.add(spawn_cell)

    service.picture.point(spawn_cell.pos, spawn_cell.clan.color)

    chance_turn_left = service.chances["chance_turn_left"]
    chance_turn_right = service.chances["chance_turn_right"] + chance_turn_left
    chance_turn_course = service.chances["chance_turn_course"] + chance_turn_right
    chance_divinity = service.chances["chance_divinity"]

    while threads:
        if service.enable_darkening:
            service.picture.image = Image.eval(service.picture.image, lambda x: x - 1)  # Затемнение
        clans = service.get_clans()

        for cell in service.cells.copy():
            step_value = np.random.randint(0, 100)
            cell.action.set_priority(cell.clan.pos)

            if step_value < chance_turn_left:
                cell.action.turn_left()
            elif step_value < chance_turn_right:
                cell.action.turn_right()
            elif step_value < chance_turn_course:
                if cell.action.dir != cell.action.prt:
                    cell.action.turn_course()

            expression = len(clans) * len(service.cells)
            divinity_expression = np.random.randint(
                0, np.random.randint(1, expression if expression > 1 else 2)) < 1 \
                                  and len(clans[cell.clan]) < 1000
            if divinity_expression:
                new_cell = Cell(cell.pos, cell.clan, cell.species)

                if np.random.randint(0, 100) < chance_divinity:
                    color = random_color()
                    position = Pos(np.random.randint(0, service.width),
                                   np.random.randint(0, service.height))
                    new_clan = Clan(f"clan.{color.hex().upper()}", position, color)
                    new_cell.clan = cell.clan = new_clan
                    new_cell.species = {"direction": np.random.randint(0, 8)}
                    service.cells.add(new_cell)
                    service.stat[new_clan.name] = 2
                else:
                    service.cells.add(new_cell)
                    service.stat[new_cell.clan.name] = len(clans[new_cell.clan])

            # if cell.action.dir != cell.action.prt:
            #     cell.action.dir = cell.action.prt

            passed_step = cell.action.step()

            service.picture.point(passed_step, darkening(
                cell.clan.color, service.darkening_degree))
            service.picture.point(cell.pos, cell.clan.color)

            if cell.action.steps_counter > service.lifetime:
                service.picture.point(cell.pos, darkening(cell.clan.color, 2))
                service.cells.remove(cell)
                service.stat["deaths"] += 1

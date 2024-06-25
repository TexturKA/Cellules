import numpy as np
from PIL import Image
from PySide6.QtCore import QThread

from general import CelluesApplication
from models import Picture, Cell, Clan, Pos, Pixel, Action, Color


def darkening(color: Color, degree: float) -> Color:
    if degree == 0:
        return Color(0, 0, 0)
    return Color(*(round(i / degree) for i in color.rgb if i >= 0))


def random_color(color_choice, threshold: int = 200) -> Color:
    base_color = np.random.choice(color_choice)
    return Color(
        np.random.randint(threshold if 'r' in base_color else 0, 256),
        np.random.randint(threshold if 'g' in base_color else 0, 256),
        np.random.randint(threshold if 'b' in base_color else 0, 256)
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
            service.picture.width // 4,
            service.picture.width - (service.picture.width // 4)),
        np.random.randint(
            service.picture.height // 4,
            service.picture.height - (service.picture.height // 4))
    )
    spawn_clan = Clan('clan.FFFFFF', spawn_point, Color(255, 255, 255))
    spawn_cell = Cell(spawn_point, spawn_clan, {"direction": np.random.randint(0, 8)})
    service.cells.add(spawn_cell)

    service.picture.point(spawn_cell.pos, spawn_cell.clan.color)

    color_threshold = service.settings["color_threshold"]
    color_choice = service.settings["color_choice"]
    darkening_tail = service.settings["darkening_tail"]
    darkening_degree = service.settings["darkening_degree"]
    chance_turn_left = service.settings["chance_turn_left"]
    chance_turn_right = service.settings["chance_turn_right"] + chance_turn_left
    chance_turn_course = service.settings["chance_turn_course"] + chance_turn_right
    chance_divinity = service.settings["chance_divinity"]
    enable_physics = bool(service.settings["enable_physics"])
    darkening_clean = bool(service.settings["darkening_clean"])

    while threads:
        QThread.usleep(1)
        service.stat["fps"] += 1
        if 0 < darkening_degree < 256:
            service.picture.matrix = np.abs(np.clip(
                service.picture.matrix, darkening_degree, 255
            ) - darkening_degree)
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

            expression = len(clans) * len(service.cells) * service.settings["ratio_divinity"]
            divinity_expression = np.random.randint(
                0, np.random.randint(1, expression if expression > 1 else 2)) < 1
            if divinity_expression and len(clans[cell.clan]) < service.settings["limit_clan_members"]:
                new_cell = Cell(cell.pos, cell.clan, cell.species)

                if np.random.randint(0, 100) < chance_divinity:
                    color = random_color(color_choice, threshold=color_threshold)
                    position = Pos(np.random.randint(0, service.picture.width),
                                   np.random.randint(0, service.picture.height))
                    new_clan = Clan(f"clan.{color.hex().upper()}", position, color)
                    new_cell.clan = cell.clan = new_clan
                    new_cell.species = {"direction": np.random.randint(0, 8)}
                    service.cells.add(new_cell)
                else:
                    service.cells.add(new_cell)

            # if cell.action.dir != cell.action.prt:
            #     cell.action.dir = cell.action.prt

            if enable_physics:
                cell.action.set_sides()
                detour = np.random.choice((cell.action.turn_left, cell.action.turn_right))
                for _ in range(8):
                    if np.max(service.picture.check(cell.action.sides[cell.action.dir])) < color_threshold:
                        passed_step = cell.action.step(dont_reset=True)
                        if darkening_tail != 0:
                            service.picture.point(passed_step, darkening(cell.clan.color, darkening_tail))
                        service.picture.point(cell.pos, cell.clan.color)
                        break
                    else:
                        detour()
            else:
                passed_step = cell.action.step()
                if darkening_tail != 0:
                    service.picture.point(passed_step, darkening(cell.clan.color, darkening_tail))
                service.picture.point(cell.pos, cell.clan.color)

            if cell.action.steps_counter > service.settings["lifetime"]:
                if darkening_clean:
                    cell.action.step()
                    [service.picture.point(pos, Color(0, 0, 0)) for pos in cell.history]
                else:
                    service.picture.point(cell.pos, darkening(cell.clan.color, 2))
                service.cells.remove(cell)
                service.stat["deaths"] += 1

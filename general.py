from logging import Logger

from tools import load_settings
from models import Picture, Cell, Clan


class CelluesApplication:
    def __init__(self, logger: Logger):
        self.log = logger.debug
        self.log_warning = logger.warning
        self.log_error = logger.error

        settings: dict = load_settings.run()
        self.width = int(settings['width'])
        self.height = int(settings['height'])
        self.resolution = self.width, self.height
        self.is_fullscreen = bool(settings.get("full_screen"))
        self.chances = {key: int(value) for key, value in settings.items()
                        if key.startswith("chance")}
        self.darkening_degree = settings["image_tail"]
        self.lifetime = settings["lifetime"]

        self.picture: Picture = Picture(self.resolution)
        self.stat: dict = {
            'population': 1,
            'max_population': 1,
            'deaths': 0,
            'clans': 1
        }
        self.cells: set[Cell] = set()

    def collect_info(self):
        self.stat['population'] = len(self.cells)
        if len(self.cells) > self.stat['max_population']:
            self.stat['max_population'] = len(self.cells)

        clans = self.get_clans()
        for title in self.stat:
            if title.startswith('clan.') and self.stat[title] == 0:
                del self.stat[title]
        self.stat['clans'] = len(clans)

        text = ''
        for item in self.stat:
            if item.startswith('clan.'):
                color = '#' + item.split('.')[1]
                text += f'<span style="color: lightgray">clan <span style="color: {color}">{color}</span>:\t{self.stat[item]}</span><br>'
            else:
                text += f'<span style="color: lightgray">{item}:\t{self.stat[item]}</span><br>'
        self.log(f"Collect info: {text}")
        return text

    def collect_image(self):
        self.log(f"Collect image. Population: {str(len(self.cells))}")
        return self.picture.update_image()

    def get_clans(self) -> dict[Clan, list[Cell]]:
        clans = {}
        for cell in self.cells:
            if cell.clan in clans:
                clans[cell.clan].append(cell)
            else:
                clans[cell.clan] = [cell]
        return clans

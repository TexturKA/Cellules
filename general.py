import sys
from logging import Logger

import numpy as np
from PySide6.QtWidgets import QApplication

from tools import load_settings
from models import Picture, Cell, Clan


class CelluesApplication:
    def __init__(self, logger: Logger):
        self.log = logger.debug
        self.log_warning = logger.warning
        self.log_error = logger.error

        self.settings: dict = load_settings.run()
        self.darkening_degree = self.settings["darkening_degree"]
        self.picture: Picture = Picture((self.settings['width'], self.settings['height']))
        self.stat: dict = {
            'population': 1,
            'max_population': 1,
            'deaths': 0,
            'clans': 1
        }
        self.cells: set[Cell] = set()

    def run(self):
        self.log(f"App launch with settings: {self.__dict__}")
        app = QApplication(sys.argv)
        return app

    def collect_info(self):
        self.stat['population'] = len(self.cells)
        if len(self.cells) > self.stat['max_population']:
            self.stat['max_population'] = len(self.cells)

        clans = self.get_clans()
        self.stat['clans'] = len(clans)
        for item in self.stat.copy():
            if item.startswith('clan.'):
                del self.stat[item]
        for clan in clans:
            self.stat[clan.name] = len(clans[clan])

        text = ''
        for item in self.stat:
            if item.startswith('clan.'):
                color = item.split('.')[1]
                text += f'<span style="color: lightgray">clan <span style="color: #{color}">#{color}</span>:\t{self.stat[item]}</span><br>'
            else:
                text += f'<span style="color: lightgray">{item}:\t{self.stat[item]}</span><br>'
        # self.log(f"Collect info: {text}")
        return text

    def collect_image(self):
        # self.log(f"Collect image. Population: {str(len(self.cells))}")
        return self.picture.update_image()

    def get_clans(self) -> dict[Clan, list[Cell]]:
        clans = {}
        for cell in self.cells:
            if cell.clan in clans:
                clans[cell.clan].append(cell)
            else:
                clans[cell.clan] = [cell]
        return clans

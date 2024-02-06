import os
from typing import List
from pathlib import Path


class FileManager:
    def __init__(self, dir_path: str, filename: str):
        self.__lines: List[str, ...] = []
        self.path: Path = Path(dir_path) / Path(filename)

    @property
    def lines(self):
        return self.__lines

    @staticmethod
    def hack(path: Path):
        if not path.exists():
            path.mkdir(parents=True)

    @staticmethod
    def get_survey(path: Path):
        file_survey = []
        for row in os.walk(path):
            for filename in row[2]:
                full_path: Path = Path(row[0]) / Path(filename)
                file_survey.append([path, filename, full_path.stat().st_mtime, full_path.stat().st_size])
        return file_survey

    def read(self):
        self.hack(self.path.parent)
        with self.path.open("r", encoding="utf-8") as file:
            self.__lines = [line.strip() for line in file if line.strip()]

    def write(self, lines: List[str]):
        self.hack(self.path.parent)
        with self.path.open("w", encoding="utf-8") as file:
            file.writelines(lines) and self.read()

    def append(self, line: str):
        self.hack(self.path.parent)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(line + "\n") and self.read()


if __name__ == "__main__":
    note_path = "./resources/notes/"
    fm = FileManager(note_path, "note.txt")
    fm.append("oh!")

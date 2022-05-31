import sys
import time
import math
import traceback
from random import randint as ri
from threading import Thread
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL import Image, ImageDraw

from window_start import Ui_window_start as UI_Start


# pyuic5 creator.ui -o creator.py

def convert_base(num, to_base=10, from_base=10):
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    alph = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alph[n]
    else:
        return convert_base(n // to_base, to_base) + alph[n % to_base]


# class Settings:
#     value = None
#     desc = None
#
#     def __init__(self, description, value=None):
#         self.desc = description
#         self.value = value
#         self.item = self.desc, self.value

class Tile:
    def __init__(self, name, value):
        self.name = name
        self.value = value


settings = {
    'screen_width': Tile('Ширина экрана', 640),
    'screen_height': Tile('Высота экрана', 480),
    'full_screen': Tile('Запуск на полный экран', False),
    'time_interval': Tile(None, 0),
    'image_eval': Tile('Постепенное затемнение', True),
    'image_tail': Tile('Степень прозрачности хвостов', 2)
}

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.array = self.x, self.y


class Picture:
    def __init__(self, image):
        self.image = image
        self.width = None
        self.height = None
        self.resolution = None, None

    def setResolution(self, width, height):
        self.width = width
        self.height = height
        self.resolution = width, height

    def resetResolution(self):
        self.setResolution(settings['screen_width'].value, settings['screen_height'].value)


class Gem:
    def __init__(self, point, direction=0, color=(255, 255, 255)):
        self.point = point
        self.mid = Point(pic.width // 2, pic.height // 2)

        self.dir = direction  # 0-UL 1-U 2-UR 3-R 4-DR 5-D 6-DL 7-L
        self.prior = 0

        self.steps = 0
        self.angle = 0
        self.color = color

        self.reset()

    def get(self):
        return self.point

    def set(self, point):
        self.point = point
        self.reset()

    def turn_left(self):
        self.dir -= 1
        if self.dir < 0:
            self.dir = 7

    def turn_right(self):
        self.dir += 1
        if self.dir > 7:
            self.dir = 0

    def step(self):
        self.reset()
        old_pos = self.get()
        if self.dir == 0:
            self.set(self.side.up)
        elif self.dir == 1:
            self.set(self.side.upright)
        elif self.dir == 2:
            self.set(self.side.right)
        elif self.dir == 3:
            self.set(self.side.downright)
        elif self.dir == 4:
            self.set(self.side.down)
        elif self.dir == 5:
            self.set(self.side.downleft)
        elif self.dir == 6:
            self.set(self.side.left)
        elif self.dir == 7:
            self.set(self.side.upleft)
        self.steps += 1
        return old_pos

    def priority(self):
        if self.point != self.mid:
            n = Point(self.point.x - self.mid.x, self.point.y - self.mid.y)
            if n.x != 0:
                a = math.atan(abs(n.y) / abs(n.x)) / math.pi * 180
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
                    self.prior = 6
                else:
                    self.prior = 2
            elif 22.5 <= a < 67.5:
                if area == 0:
                    self.prior = 5
                elif area == 1:
                    self.prior = 7
                elif area == 2:
                    self.prior = 1
                elif area == 3:
                    self.prior = 3
            else:
                if area in [1, 2]:
                    self.prior = 0
                else:
                    self.prior = 4
            self.angle = a

    def reset(self):
        self.side.up = Point(self.point.x, self.point.y - 1)
        self.side.upright = Point(self.point.x + 1, self.point.y - 1)
        self.side.right = Point(self.point.x + 1, self.point.y)
        self.side.downright = Point(self.point.x + 1, self.point.y + 1)
        self.side.down = Point(self.point.x, self.point.y + 1)
        self.side.downleft = Point(self.point.x - 1, self.point.y + 1)
        self.side.left = Point(self.point.x - 1, self.point.y)
        self.side.upleft = Point(self.point.x - 1, self.point.y - 1)

    class side:
        up = None
        upright = None
        right = None
        downright = None
        down = None
        downleft = None
        left = None
        upleft = None


def get_image():
    draw = ImageDraw.Draw(pic.image)

    def dark(color, deg):
        res = list()
        for j in range(3):
            if color[j] != 0:
                res.append(color[j] // deg)
            else:
                res.append(color[j])
        return res[0], res[1], res[2]

    def get_color():
        res = list()
        for j in range(3):
            res.append(ri(0, 256))
        if res[0] < 200 and res[1] < 200:
            res = get_color()
        return res[0], res[1], res[2]

    spawn = ri(pic.width // 4, pic.width - (pic.width // 4)), ri(pic.height // 4, pic.height - (pic.height // 4))
    white_clan = 'clan.FFFFFF'
    gems[white_clan] = [Gem(Point(spawn[0], spawn[1]))]
    stat[white_clan] = len(gems[white_clan])
    draw.point(gems[white_clan][0].get().array)
    while thread_work:
        # if settings['image_eval'].value != 0:
        #     pic.image = Image.eval(pic.image, (lambda x: x - 0.5))  # Затемнение
        draw = ImageDraw.Draw(pic.image)

        for clan in list(gems):
            for gem in range(len(gems[clan])):
                if gem >= len(gems[clan]):
                    continue

                lana = gems[clan][gem]
                lana.priority()

                step = ri(0, 100)

                if step in range(100)[:10]:
                    lana.turn_left()
                elif step in range(100)[:20]:
                    lana.turn_right()

                if step in range(100)[20:30]:
                    if lana.dir != lana.prior:
                        course = 0
                        while True:
                            if lana.dir + course < 4:
                                course += 1
                            elif lana.dir + course > 4:
                                course -= 1
                            else:
                                break
                        if (lana.prior + course) % 8 > 4:
                            lana.turn_right()
                        else:
                            lana.turn_left()

                if ri(0, ri(1, len(clan) * stat['pop'])) < 1 and len(gems[clan]) < 1000:
                    new_gem = Gem(lana.side.up)

                    if ri(0, 100) < 1:
                        new_gem.color = get_color()
                        new_gem.mid = Point(ri(0, pic.width), ri(0, pic.height))
                        lana.color = new_gem.color
                        lana.mid = new_gem.mid
                        new_clan = f'clan.{str(convert_base(new_gem.color[0] - 1, to_base=16)).rjust(2, "0")}' \
                                   f'{str(convert_base(new_gem.color[1] - 1, to_base=16)).rjust(2, "0")}' \
                                   f'{str(convert_base(new_gem.color[2] - 1, to_base=16)).rjust(2, "0")}'
                        gems[clan].remove(lana)
                        gems[new_clan] = [lana, new_gem]
                        stat[new_clan] = len(gems[new_clan])
                    else:
                        new_gem.color = lana.color
                        new_gem.mid = lana.mid
                        gems[clan].append(new_gem)
                    stat['born'] += 1

                # if lana.dir != lana.prior:
                #     lana.dir = lana.prior

                old = lana.step()

                draw.point(old.array, (dark(lana.color, settings['image_tail'].value)))
                draw.point(lana.get().array, lana.color)
                if lana.steps > 1000:
                    draw.point(lana.get().array, (dark(lana.color, 2)))
                    if lana in gems[clan]:
                        gems[clan].remove(lana)
                        stat['death'] += 1

        stat['pop'] = 0
        for clan in gems:
            stat['pop'] += len(gems[clan])
            stat[clan] = len(gems[clan])
        if stat['pop'] > stat['max']:
            stat['max'] = stat['pop']
        for item in list(stat):
            if item.startswith('clan.') and stat[item] == 0:
                del stat[item]


def collectInfo():
    text = ''
    for item in stat:
        if item.startswith('clan.'):
            color = '#' + item.split('.')[1]
            text += f'<span style="color: lightgray">clan <span style="color: {color}">{color}</span>:\t{stat[item]}</span><br>'
        else:
            text += f'<span style="color: lightgray">{item}:\t{stat[item]}</span><br>'
    return text


def collectImage():
    return pic.image


class Trd(QThread):
    def __init__(self, parent, func, signal=None, looptime=10):
        super(Trd, self).__init__(parent)
        self.signal = signal
        self.func = func
        self.looptime = looptime

    def run(self):
        if self.signal is not None:
            while thread_work:
                self.signal.emit(self.func())
                QThread.msleep(self.looptime)
        else:
            self.func()


class ShowImage(QMainWindow):
    imageSignal = pyqtSignal(Image.Image)
    infoSignal = pyqtSignal(str)

    def __init__(self):
        super(ShowImage, self).__init__()

        self.setWindowTitle("BestCeller by TexturKA")
        self.setGeometry(0, 0, pic.width, pic.height)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label.setGeometry(0, 0, pic.width, pic.height)

        self.info = QLabel(self)
        self.info.setAlignment(Qt.AlignTop | Qt.AlignTop)
        self.info.setGeometry(10, 10, 400, pic.height - 20)
        self.info.setFont(QFont('Consolas', 8))

        self.imageSignal.connect(self.showImage)
        self.infoSignal.connect(self.showInfo)

        mainStream = Trd(self, get_image)
        imageStream = Trd(self, collectImage, self.imageSignal, looptime=10)
        infoStream = Trd(self, collectInfo, self.infoSignal, looptime=500)

        mainStream.start()
        imageStream.start()
        infoStream.start()

        if settings['full_screen'].value:
            self.showFullScreen()
        else:
            self.show()

    def showImage(self, *args):
        self.image_qt = ImageQt(pic.image)
        pixmap = QPixmap(QImage(self.image_qt))
        self.label.setPixmap(pixmap)

    def showInfo(self, text):
        self.info.setText(text)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, *args, **kwargs):
        pass
        # print(f'{gems}\n{list(gems)}')


class StartWindow(UI_Start, QMainWindow):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.setupUi(self)
        self.app = None
        self.start_button.clicked.connect(self.start_handler)
        self.show()

        settings_text = ''
        for key in settings:
            if settings[key].name is not None:
                settings_text += f'{settings[key].name}: {settings[key].value}\n'
        self.settings.setText(settings_text)

    def start_handler(self):
        self.startApplication()

    def startApplication(self):

        if settings['full_screen'].value:
            settings['full_screen'].value = True
            screen_size = app.primaryScreen().size()
            width, height = screen_size.width(), screen_size.height()
        else:
            width, height = 640, 480
        settings['screen_width'].value = width
        settings['screen_height'].value = height
        pic.resetResolution()
        pic.image = Image.new('RGB', (width, height))
        self.app = ShowImage()
        print(f'windowed:\t{settings["full_screen"].value}\n'
              f'resolution:\t{width}x{height}\n'
              f'interval:\t{settings["time_interval"].value}')
        self.close()


def exceptlog(ex_cls, ex, tb):
    text = f'{ex_cls.__name__}: {ex}:\n'
    text += ''.join(traceback.format_tb(tb))
    print(text)
    quit()


if __name__ == "__main__":
    sys.excepthook = exceptlog
    app = QApplication(sys.argv)

    stat = {
        'pop': 1,
        'max': 1,
        'clan': 1,
        'born': 1,
        'death': 0
    }

    application = StartWindow()
    gems = dict()
    thread_work = True

    pic = Picture(None)

    sys.exit(app.exec_())

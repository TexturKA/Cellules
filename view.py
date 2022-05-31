import numpy
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QFont, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PIL import ImageQt
from cell2 import *
import sys


class ShowImage(QMainWindow):
    imageSignal = pyqtSignal(Image.Image)
    infoSignal = pyqtSignal(str)

    def __init__(self):
        super(ShowImage, self).__init__()

        self.setWindowTitle("BestCeller by TexturKA")
        self.setGeometry(0, 0, *Settings.resolution)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label.setGeometry(0, 0, *Settings.resolution)

        self.info = QLabel(self)
        self.info.setAlignment(Qt.AlignTop | Qt.AlignTop)
        self.info.setGeometry(10, 10, 400, Settings.height - 20)
        self.info.setFont(QFont('Consolas', 8))

        self.imageSignal.connect(self.show_image)
        self.infoSignal.connect(self.show_info)

        mainStream = Trd(self, get_image)
        imageStream = Trd(self, collect_image, self.imageSignal, looptime=10)
        infoStream = Trd(self, collect_info, self.infoSignal, looptime=500)

        mainStream.start()
        imageStream.start()
        infoStream.start()

        self.show()

    def show_image(self, *args):
        self.image_qt = ImageQt.ImageQt(pic.image)
        pixmap = QPixmap(QImage(self.image_qt))
        self.label.setPixmap(pixmap)

    def show_info(self, text):
        self.info.setText(text)

    @staticmethod
    def collect_info():
        text = ''
        for item in Settings.stat:
            if item.startswith('clan.'):
                color = '#' + item.split('.')[1]
                text += f'<span style="color: lightgray">clan <span style="color: {color}">{color}' \
                        f'</span>:\t{Settings.stat[item]}</span><br>'
            else:
                text += f'<span style="color: lightgray">{item}:\t{Settings.stat[item]}</span><br>'
        return text

    @staticmethod
    def collect_image():
        return pic.image

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, *args, **kwargs):
        pass
        # print(f'{gems}\n{list(gems)}')


if __name__ == "__main__":
    excepthook.activate()

    APP = QApplication(sys.argv)

    Settings.resolution = 640, 480
    Settings.width = Settings.resolution[0]
    Settings.height = Settings.resolution[1]
    Settings.stat = {
        'pop': 1,
        'max': 1,
        'clan': 1,
        'born': 1,
        'death': 0
    }

    CANVAS = numpy.array(Image.new('RGB', (Settings.width, Settings.height)))

    application = ShowImage()
    thread_work = True

    sys.exit(APP.exec_())
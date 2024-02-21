import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
from PIL import Image, ImageQt

from models import Picture
from general import CelluesApplication
from draw.draw3 import operations

threads: list[QtCore.QThread] = []


class Trd(QtCore.QThread):
    def __init__(self, parent, func, func_args=None, signal=None, looptime=10):
        super(Trd, self).__init__(parent)
        self.signal = signal
        self.func = func
        self.func_args = func_args or ()
        self.looptime = looptime

    def run(self):
        if self.signal is not None:
            while threads:
                self.signal.emit(self.func(*self.func_args))
                self.msleep(self.looptime)
        else:
            self.func(*self.func_args)


class ShowImage(QtWidgets.QMainWindow):
    imageSignal = QtCore.Signal(Image.Image)
    infoSignal = QtCore.Signal(str)

    def __init__(self, base: CelluesApplication):
        super(ShowImage, self).__init__()

        self.log = base.log
        self.picture: Picture = base.picture

        self.setWindowTitle("Cellules by TexturKA")
        self.setGeometry(0, 0, base.picture.width, base.picture.height)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.label.setGeometry(0, 0, base.picture.width, base.picture.height)

        self.info = QtWidgets.QLabel(self)
        self.info.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignTop)
        self.info.setGeometry(10, 10, 400, self.picture.image.height - 20)
        self.info.setFont(QtGui.QFont('Consolas', 8))

        self.imageSignal.connect(self.show_image)
        self.infoSignal.connect(self.show_info)

        thread = Trd(self, operations, func_args=(base, threads))
        thread.setPriority(QtCore.QThread.Priority.NormalPriority)
        threads.append(thread)

        thread = Trd(self, base.collect_info, signal=self.infoSignal, looptime=1000)
        thread.setPriority(QtCore.QThread.Priority.HighestPriority)
        threads.append(thread)

        thread = Trd(self, base.collect_image, signal=self.imageSignal, looptime=10)
        thread.setPriority(QtCore.QThread.Priority.HighPriority)
        threads.append(thread)

        self.log(f"Start threads {threads}")
        for thread in threads:
            thread.start()
        self.log("Window initialized")

    def show_image(self):
        # self.log("Image label updated")
        image_qt = ImageQt.ImageQt(self.picture.image)
        pixmap = QtGui.QPixmap.fromImage(image_qt)
        self.label.setPixmap(pixmap)

    def show_info(self, text):
        # self.log("Info label updated")
        self.info.setText(text)

    def keyPressEvent(self, e):
        self.log(f'Key {e.key()} pressed')
        if e.key() == QtCore.Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, *args, **kwargs):
        self.log(f'Close window')
        threads.clear()

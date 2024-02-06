import sys

from PyQt6.QtWidgets import QApplication

from tools import getLogger
from general import CelluesApplication
from windows import ShowImage

logger = getLogger()


if __name__ == "__main__":
    try:
        service = CelluesApplication(logger)
        service.log(f"App launch with settings: {service.__dict__}")
        app = QApplication(sys.argv)
        main_window = ShowImage(service)

        if service.is_fullscreen:
            main_window.showFullScreen()
        else:
            main_window.show()
    except BaseException as err:
        logger.exception(err)
    else:
        logger.debug("Exit!")
        sys.exit(app.exec())

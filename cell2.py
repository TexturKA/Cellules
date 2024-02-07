import sys

from tools import getLogger
from general import CelluesApplication
from windows import ShowImage

logger = getLogger()


if __name__ == "__main__":
    try:
        service = CelluesApplication(logger)
        app = service.run()
        main_window = ShowImage(service)

        if service.settings["full_screen"]:
            main_window.showFullScreen()
        else:
            main_window.show()
    except BaseException as err:
        logger.exception(err)
    else:
        logger.debug("Exit!")
        sys.exit(app.exec_())

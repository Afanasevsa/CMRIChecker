# Software configuration
from library import config as sw_cfg
# Connection widget
from library.connection.ConnectionUI import ConnectionUI

# System-specific parameters and functions
from sys import exit, argv
# Threading interface
from queue import Queue
from threading import Thread
# PyQt5 modules
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QSplashScreen, QMessageBox


class ProgramUI(QMainWindow):
    def __init__(self, parent=None):
        super(ProgramUI, self).__init__(parent)
        # Window title
        self.setWindowTitle(sw_cfg.program_title + " - Main window")
        # Program window dimensions
        hor_size = 909
        ver_size = 82
        self.resize(hor_size, ver_size)
        self.setMinimumSize(QSize(hor_size, ver_size))
        self.setMaximumSize(QSize(hor_size, ver_size))
        # Calling centering window function
        sw_cfg.program_center(self)
        # Setting the connection widget as a central widget
        self.setCentralWidget(ConnectionUI())
        # Stylesheet of the tooltip with the current transformer readings
        # self.setStyleSheet("QToolTip {background-color: black; color: white; border: black solid 1px}")
        # Application icon
        self.setWindowIcon(QIcon("icon\\burn.png"))

    # Actions when the program window closed
    def closeEvent(self, event):
        # Setting the stopping attribute of the polling thread and waiting for the completion
        try:
            sw_cfg.polling_thread.do_run = False
            sw_cfg.polling_thread.join()
        # Exception when the program window closed without starting the polling thread
        except AttributeError:
            pass
        # Closing the connection to the CMRI
        sw_cfg.cmri_dll.CMRI_PortClose()


if __name__ == "__main__":
    app = QApplication(argv)

    # Preparing and displaying the splash screen during software initialization
    splash_pix = QPixmap("icon\\logo.png")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.show()

    # Preparing and starting the software initialization thread
    queue = Queue()
    init_thread = Thread(target=sw_cfg.sw_init, daemon=True, args=(queue,))
    init_thread.start()

    # Process events during software initialization
    while init_thread.isAlive():
        app.processEvents()

    try:
        # Showing the main window GUI
        sw_cfg.main_app = ProgramUI()
        sw_cfg.main_app.show()
    except AttributeError:
        # Showing the message box with initialization error
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Initialization error")
        error_dialog.setText(queue.get())
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.show()

    # Hiding the splash screen after software initialization
    splash.finish(sw_cfg.main_app)
    exit(app.exec_())

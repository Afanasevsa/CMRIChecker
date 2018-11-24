# Finding the paths in the system according to the specified template
from glob import glob
# System-specific parameters and functions
from sys import platform
# Access to the GitLab server API
from gitlab import Gitlab
# Interaction with the configuration *.ini files
from configparser import ConfigParser
# Foreign C compatible data types for the current transformers library
from ctypes import windll, c_int, c_double
# Data exchange with CMRI via COM-port
from serial import Serial, SerialException
# PyQt5 modules
from PyQt5.QtCore import QSize, QObject, pyqtSignal, QEvent
from PyQt5.QtWidgets import QDesktopWidget


def program_center(self):
    """
    Centering the program window

    Args:
        :param self: ProgramUI QMainWindow class
        :type self: __main__.ProgramUI

    Returns:
        :return: None
    """

    # Get a rectangle that defines the geometry of the window
    rectangle = self.frameGeometry()
    # Get the current screen resolution and calculate the center point
    cp = QDesktopWidget().availableGeometry().center()
    # Setting the rectangle to the center of the screen
    rectangle.moveCenter(cp)
    # Moving the upper left corner of the program window to the top left corner of the rectangle - centering the window
    self.move(rectangle.topLeft())


def resize_window(self, stand_qty):
    """
    Resizing the software interface after completing the connection

    Args:
        :param self: ProgramUI QMainWindow class
        :type self: __main__.ProgramUI
        :param stand_qty: The number of stands
        :type stand_qty: int

    Returns:
        :return: None
    """

    # Updating program window dimensions
    hor_size = 909
    ver_size = 82 + stand_qty * 160
    self.resize(hor_size, ver_size)
    self.setMinimumSize(QSize(hor_size, ver_size))
    self.setMaximumSize(QSize(hor_size, ver_size))
    # Calling centering window function
    program_center(self)


def available_serial():
    """
    Getting the list of ports available for connection

    Returns:
        :return: List of ports available for connection
        :rtype: list
    """

    # Initializing an empty list of ports available for connection
    available_com = list()

    if platform.startswith("win"):
        com_list = ["COM%s" % (i + 1) for i in range(256)]
    elif platform.startswith("linux") or platform.startswith("cygwin"):
        com_list = glob("/dev/tty[A-Za-z]*")
    elif platform.startswith("darwin"):
        com_list = glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    for device in com_list:
        try:
            s = Serial(device)
            s.close()
            available_com.append(device)
        except (OSError, SerialException):
            pass
    return available_com


def get_auth_config():
    """
    Reading the configuration file for access to the GitLab server

    Returns:
        :return: Read configuration
        :rtype: ConfigParser
    """

    config = ConfigParser()
    config.read(["config.ini"], encoding="utf-8")
    return config


def get_git_config(config_raw):
    """
    Representing a configuration from the GitLab server in the ConfigParser format

    Args:
        :param config_raw: Read configuration
        :type config_raw: str

    Returns:
        :return: Configuration in the ConfigParser format
        :rtype: ConfigParser
    """

    config = ConfigParser()
    config.optionxform = str
    config.read_string(config_raw)
    return config


def clickable_widget(widget):
    """
    Setting mouse click events for widgets that do not support this function

    Args:
        :param widget: Processed widget

    Returns:
        :return: Widget with installed event filter
    """

    class Filter(QObject):
        clicked = pyqtSignal()

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True
            return False

    filt = Filter(widget)
    widget.installEventFilter(filt)
    return filt.clicked


def sw_init(queue):
    """
    Software initialization

    Returns:
        :return: None
    """

    # Loading the CMRI library
    global cmri_dll
    cmri_dll = windll.LoadLibrary("library\\dll\\cmridll.dll")

    # Getting the list of ports available for connection
    global avail_com
    avail_com = available_serial()
    # Reading the configuration file for access to the GitLab server
    global auth_config
    auth_config = get_auth_config()

    # Getting the settings for the connection to the GitLab server
    git_server = auth_config["AUTH"]["GIT_SERVER"]
    git_token = auth_config["AUTH"]["GIT_TOKEN"]
    git_api_version = auth_config["AUTH"]["GIT_API_VERSION"]
    git_proj_id = auth_config["AUTH"]["PROJ_ID"]

    try:
        # Initializing the connection to the GitLab server
        gitlab_auth = Gitlab(git_server, git_token, api_version=git_api_version)
        # Reading the project in the GitLab server
        project = gitlab_auth.projects.get(git_proj_id)
    except Exception as error:
        queue.put(str(error))
        return

    # Getting the configuration from the GitLab server
    raw = project.files.get(file_path="config.ini", ref="master").decode()
    raw = raw.decode("utf-8")

    # Representing a configuration from the GitLab server in the ConfigParser format
    global git_config
    git_config = get_git_config(raw)


# List of ports available for connection
avail_com = None
# Configuration file for access to the GitLab server
auth_config = None
# Configuration from the GitLab server in the ConfigParser format
git_config = None

# CMRI library
cmri_dll = None

# Software title
program_title = "CMRIChecker"
# Main window GUI
main_app = None

# List of stands when reconnecting during one session
stand_list = list()

# Primary polling thread
polling_thread = None
# Suspending execution of the polling thread for the given number of seconds
polling_time = 0

# Initializing pointers for CMRI library
# Voltage
GetVoltage_1 = c_double()
GetVoltage_2 = c_double()
GetVoltage_3 = c_double()
# Current
GetCurrent_1 = c_double()
GetCurrent_2 = c_double()
GetCurrent_3 = c_double()
# Status
GetStatus = c_int()
# Temperature
GetTemp = c_double()

# Default CMRI reset ID
reset_id = 0

# CMRI returned status bits
phase_bits = [1, 2, 4]

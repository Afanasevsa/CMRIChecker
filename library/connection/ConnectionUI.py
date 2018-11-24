# Software configuration
from library import config as sw_cfg
# Stand widget
from library.stand.StandUI import StandUI

# Looking for regular expression pattern
from re import search
# Foreign C compatible data types for the current transformers library
from ctypes import c_int
# PyQt5 modules
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QComboBox, QFrame, QPushButton


def reset_action():
    """
    Reset all current transformers

    Returns:
        :return: None
    """

    # Broadcast address
    sw_cfg.reset_id = 0
    # Setting the pause for the main polling thread
    sw_cfg.polling_thread.do_pause = True


class ConnectionUI(QWidget):
    # GUI widget objects
    interface = dict()
    # The flag of adding a stand widget
    stand_widget = None

    def __init__(self, parent=None):
        super(ConnectionUI, self).__init__(parent)

        # Setting the vertical layout of the widget objects
        self.interface["vertical_layout"] = QVBoxLayout(self)
        # Connection settings group
        self.interface["connection_box"] = QGroupBox("Connection settings", self)
        self.interface["connection_box"].setMaximumSize(QSize(891, 61))
        # COM-port
        self.interface["com_label"] = QLabel("Port:", self.interface["connection_box"])
        self.interface["com_label"].setGeometry(QRect(20, 20, 31, 22))
        self.interface["com_combo"] = QComboBox(self.interface["connection_box"])
        self.interface["com_combo"].setGeometry(QRect(60, 20, 71, 22))
        self.interface["com_combo"].addItems(sw_cfg.avail_com)
        if sw_cfg.auth_config["SETTING"]["DEFAULT_COM"] in sw_cfg.avail_com:
            com_id = sw_cfg.avail_com.index(sw_cfg.auth_config["SETTING"]["DEFAULT_COM"])
            self.interface["com_combo"].setCurrentIndex(com_id)
        # Spacer
        self.interface["spacer_1"] = QFrame(self.interface["connection_box"])
        self.interface["spacer_1"].setGeometry(QRect(140, 16, 16, 31))
        self.interface["spacer_1"].setFrameShape(QFrame.VLine)
        self.interface["spacer_1"].setFrameShadow(QFrame.Sunken)
        # Stand №1
        self.interface["stand_1_label"] = QLabel("№1:", self.interface["connection_box"])
        self.interface["stand_1_label"].setGeometry(QRect(160, 20, 31, 22))
        self.interface["stand_1_combo"] = QComboBox(self.interface["connection_box"])
        self.interface["stand_1_combo"].setGeometry(QRect(190, 20, 71, 22))
        self.interface["stand_1_combo"].addItem("No")
        self.interface["stand_1_combo"].addItems(sw_cfg.git_config.sections())
        # Stand №2
        self.interface["stand_2_label"] = QLabel("№2:", self.interface["connection_box"])
        self.interface["stand_2_label"].setGeometry(QRect(270, 20, 31, 22))
        self.interface["stand_2_combo"] = QComboBox(self.interface["connection_box"])
        self.interface["stand_2_combo"].setGeometry(QRect(300, 20, 71, 22))
        self.interface["stand_2_combo"].addItem("No")
        self.interface["stand_2_combo"].addItems(sw_cfg.git_config.sections())
        # Stand №3
        self.interface["stand_3_label"] = QLabel("№3:", self.interface["connection_box"])
        self.interface["stand_3_label"].setGeometry(QRect(380, 20, 31, 22))
        self.interface["stand_3_combo"] = QComboBox(self.interface["connection_box"])
        self.interface["stand_3_combo"].setGeometry(QRect(410, 20, 71, 22))
        self.interface["stand_3_combo"].addItem("No")
        self.interface["stand_3_combo"].addItems(sw_cfg.git_config.sections())
        # Stand №4
        self.interface["stand_4_label"] = QLabel("№4:", self.interface["connection_box"])
        self.interface["stand_4_label"].setGeometry(QRect(490, 20, 31, 22))
        self.interface["stand_4_combo"] = QComboBox(self.interface["connection_box"])
        self.interface["stand_4_combo"].setGeometry(QRect(520, 20, 71, 22))
        self.interface["stand_4_combo"].addItem("No")
        self.interface["stand_4_combo"].addItems(sw_cfg.git_config.sections())
        # Spacer
        self.interface["spacer_2"] = QFrame(self.interface["connection_box"])
        self.interface["spacer_2"].setGeometry(QRect(600, 16, 16, 31))
        self.interface["spacer_2"].setFrameShape(QFrame.VLine)
        self.interface["spacer_2"].setFrameShadow(QFrame.Sunken)
        # Connect/Disconnect button
        self.interface["connect_btn"] = QPushButton("Connect", self.interface["connection_box"])
        self.interface["connect_btn"].setGeometry(QRect(620, 20, 121, 23))
        self.interface["connect_btn"].setAutoDefault(False)
        self.interface["connect_btn"].clicked.connect(self.connect_action)
        # Reset all current transformers
        self.interface["reset_btn"] = QPushButton("Reset all", self.interface["connection_box"])
        self.interface["reset_btn"].setEnabled(False)
        self.interface["reset_btn"].setGeometry(QRect(750, 20, 121, 23))
        self.interface["reset_btn"].setAutoDefault(False)
        self.interface["reset_btn"].clicked.connect(reset_action)

        # Adding the connection settings group to the layout
        self.interface["vertical_layout"].addWidget(self.interface["connection_box"])

    # Actions when the connect button pressed
    def connect_action(self):
        # Checking stands selection when setting up the connection
        id_list = [self.interface["stand_{0}_combo".format(x)].currentIndex()
                   for x in range(1, 5) if self.interface["stand_{0}_combo".format(x)].currentIndex() > 0]
        if len(id_list) != len(set(id_list)):
            # TODO Highlighting of repeating stands in the connection settings group
            return None

        # Re-initializing the list of stands when reconnecting during one session
        sw_cfg.stand_list = list()
        # Setting connection to the CMRI
        sw_cfg.cmri_dll.CMRI_PortSetParams(c_int(9600), c_int(8), c_int(0), c_int(0))
        port = int(search(r"\d+(\.\d+)?", self.interface["com_combo"].currentText()).group(0))
        sw_cfg.cmri_dll.CMRI_PortOpen(c_int(port))

        # Setting a list of added stands based on connection settings
        for stand in range(1, 5):
            stand_name = self.interface["stand_{0}_combo".format(stand)].currentText()
            if stand_name != "No":
                sw_cfg.stand_list.append(stand_name)

        # Resizing the software interface after completing the connection
        sw_cfg.resize_window(sw_cfg.main_app, len(sw_cfg.stand_list))
        # Adding stands to the program window
        if len(sw_cfg.stand_list):
            self.stand_widget = StandUI()
            self.interface["vertical_layout"].addWidget(self.stand_widget)

        # Disabling connection settings
        self.interface["com_combo"].setEnabled(False)
        self.interface["stand_1_combo"].setEnabled(False)
        self.interface["stand_2_combo"].setEnabled(False)
        self.interface["stand_3_combo"].setEnabled(False)
        self.interface["stand_4_combo"].setEnabled(False)

        # Switching the connect/disconnect button
        self.interface["connect_btn"].setText("Disconnect")
        self.interface["connect_btn"].disconnect()
        self.interface["connect_btn"].clicked.connect(self.disconnect_action)
        # Enabling the reset button for all current transformers
        self.interface["reset_btn"].setEnabled(True)

    # Actions when the disconnect button pressed
    def disconnect_action(self):
        # Setting the stopping attribute of the polling thread and waiting for the completion
        sw_cfg.polling_thread.do_run = False
        sw_cfg.polling_thread.join()
        # Closing the connection to the CMRI
        sw_cfg.cmri_dll.CMRI_PortClose()

        # Enabling connection settings
        self.interface["com_combo"].setEnabled(True)
        self.interface["stand_1_combo"].setEnabled(True)
        self.interface["stand_2_combo"].setEnabled(True)
        self.interface["stand_3_combo"].setEnabled(True)
        self.interface["stand_4_combo"].setEnabled(True)

        # Removing previously added stands and updating the size of the program window
        self.stand_widget.deleteLater()
        sw_cfg.resize_window(sw_cfg.main_app, 0)

        # Switching the connect/disconnect button
        self.interface["connect_btn"].setText("Connect")
        self.interface["connect_btn"].disconnect()
        self.interface["connect_btn"].clicked.connect(self.connect_action)
        # Disabling the reset button for all current transformers
        self.interface["reset_btn"].setEnabled(False)

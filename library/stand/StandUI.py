# Software configuration
from library import config as sw_cfg
# LED status widget
from library.stand.led import LedWidget

# Suspending execution of the polling thread for the given number of seconds
from time import sleep
# Getting all possible combinations from the list
from itertools import combinations
# Foreign C compatible data types for the current transformers library
from ctypes import byref, c_int, c_long
# Threading interface
from threading import Thread, currentThread
# PyQt5 modules
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QWidget, QGroupBox, QHBoxLayout


def cmri_click(box):
    """
    Actions when the CMRI group pressed

    Args:
        :param box: CMRI group widget
        :type box: QGroupBox

    Returns:
        :return: None
    """

    # Getting the address of the device from the group title
    sw_cfg.reset_id = int(box.title().split(" ")[2], 16)
    # Setting the polling pause
    sw_cfg.polling_thread.do_pause = True


class StandUI(QWidget):
    # GUI widget objects
    interface = dict()

    def __init__(self, parent=None):
        super(StandUI, self).__init__(parent)
        # Setting the GUI
        # The initial Y coordinate of the rack group offset
        stand_y = 0
        for idx, stand in enumerate(sw_cfg.stand_list, start=1):
            self.interface["stand_{0}".format(idx)] = QGroupBox("Stand \"{0}\"".format(stand), self)
            self.interface["stand_{0}".format(idx)].setGeometry(QRect(0, stand_y, 891, 151))
            # The initial X coordinate of the row group offset
            row_x = 10
            # Initializing IDs for the CMRI seats
            id_top = 16
            id_bot = 1
            # Setting 8 devices per row
            for row in range(1, 9):
                # The initial Y coordinate of the column group offset
                col_y = 20
                # Setting 2 rows
                for col in range(1, 3):
                    # Setting IDs for the CMRI seats
                    if col % 2:
                        box_id = id_top
                    else:
                        box_id = id_bot

                    # CMRI group
                    self.interface["cmri_{0}{1}".format(stand, box_id)] = \
                        QGroupBox(str(box_id) + " - " + sw_cfg.git_config[stand][box_id],
                                  self.interface["stand_{0}".format(idx)])
                    self.interface["cmri_{0}{1}".format(stand, box_id)].setGeometry(QRect(row_x, col_y, 100, 60))
                    sw_cfg.clickable_widget(self.interface["cmri_{0}{1}".format(stand, box_id)]).connect(
                        lambda x=self.interface["cmri_{0}{1}".format(stand, box_id)]: cmri_click(x))
                    # Horizontal layout inside the group
                    self.interface["layout_{0}{1}".format(stand, box_id)] = \
                        QHBoxLayout(self.interface["cmri_{0}{1}".format(stand, box_id)])
                    # Phase №1
                    self.interface["L1_{0}{1}".format(stand, box_id)] = \
                        LedWidget(self.interface["cmri_{0}{1}".format(stand, box_id)])
                    self.interface["layout_{0}{1}".format(stand, box_id)].addWidget(
                        self.interface["L1_{0}{1}".format(stand, box_id)])
                    # Phase №2
                    self.interface["L2_{0}{1}".format(stand, box_id)] = \
                        LedWidget(self.interface["cmri_{0}{1}".format(stand, box_id)])
                    self.interface["layout_{0}{1}".format(stand, box_id)].addWidget(
                        self.interface["L2_{0}{1}".format(stand, box_id)])
                    # Phase №3
                    self.interface["L3_{0}{1}".format(stand, box_id)] = \
                        LedWidget(self.interface["cmri_{0}{1}".format(stand, box_id)])
                    self.interface["layout_{0}{1}".format(stand, box_id)].addWidget(
                        self.interface["L3_{0}{1}".format(stand, box_id)])
                    # Updating Y coordinate of the column group offset
                    col_y += 60
                # Updating X coordinate of the row group offset
                row_x += 110
                # Updating IDs for the CMRI seats
                id_top -= 1
                id_bot += 1
            # Updating Y coordinate of the rack group offset
            stand_y += 160
        # Setting the main polling thread and default attributes
        sw_cfg.polling_thread = Thread(target=self.device_polling, daemon=True)
        sw_cfg.polling_thread.do_run = True
        sw_cfg.polling_thread.do_pause = False
        sw_cfg.polling_thread.start()

    def device_polling(self):
        """
        Current transformer polling thread

        Returns:
            :return: None
        """

        # Getting the polling thread
        polling_thread = currentThread()
        # The primary polling cycle during the do_run = True
        while getattr(polling_thread, "do_run"):
            # Getting the data from current transformers during the do_pause = False
            while not getattr(polling_thread, "do_pause"):
                # Checking for the polling stop do_run = False
                if not getattr(polling_thread, "do_run"):
                    break
                # Continue polling
                for stand in sw_cfg.stand_list:
                    for place in sw_cfg.git_config[stand]:
                        # Checking for the polling stop do_run = False or the polling pause do_pause = True
                        if not getattr(polling_thread, "do_run") or getattr(polling_thread, "do_pause"):
                            break
                        # Highlighting of the current polling current transformer
                        self.interface["cmri_{0}{1}".format(stand, place)].setStyleSheet("color: rgb(255, 0, 0);")
                        # Setting the address of the polled current transformer
                        device = int(sw_cfg.git_config[stand][place], 16)

                        # Getting status
                        get_status = sw_cfg.cmri_dll.CMRI_GetStatus(byref(c_long(device)), byref(sw_cfg.GetStatus))
                        # Checking for the presence of a current transformer on the line
                        if get_status is not 0:
                            # Removing the highlight of the polled device and proceeding to the next one
                            self.interface["cmri_{0}{1}".format(stand, place)].setStyleSheet("")
                            continue

                        # Getting a list of phases with an error
                        phase_list = list()
                        for index in range(len(sw_cfg.phase_bits), 0, -1):
                            for sequence in combinations(sw_cfg.phase_bits, index):
                                if sum(sequence) == sw_cfg.GetStatus.value:
                                    for bit in list(sequence):
                                        phase_list.append(sw_cfg.phase_bits.index(bit) + 1)

                        # Setting the corresponding indication in the presence and absence of errors
                        for idx in range(1, 4):
                            if idx in phase_list:
                                self.interface["L{0}_{1}{2}".format(idx, stand, place)].setColor(QColor("red"))
                            else:
                                self.interface["L{0}_{1}{2}".format(idx, stand, place)].setColor(QColor("green"))

                        # Getting voltage
                        sw_cfg.cmri_dll.CMRI_GetVoltage(c_long(device), c_int(1), byref(sw_cfg.GetVoltage_1))
                        sw_cfg.cmri_dll.CMRI_GetVoltage(c_long(device), c_int(2), byref(sw_cfg.GetVoltage_2))
                        sw_cfg.cmri_dll.CMRI_GetVoltage(c_long(device), c_int(3), byref(sw_cfg.GetVoltage_3))
                        # Getting current
                        sw_cfg.cmri_dll.CMRI_GetCurrent(c_long(device), c_int(1), byref(sw_cfg.GetCurrent_1))
                        sw_cfg.cmri_dll.CMRI_GetCurrent(c_long(device), c_int(2), byref(sw_cfg.GetCurrent_2))
                        sw_cfg.cmri_dll.CMRI_GetCurrent(c_long(device), c_int(3), byref(sw_cfg.GetCurrent_3))
                        # Getting temperature
                        sw_cfg.cmri_dll.CMRI_GetTemp(c_long(device), byref(sw_cfg.GetTemp))
                        # Setting tooltip
                        self.interface["cmri_{0}{1}".format(stand, place)].setToolTip(
                            "<b>Voltage L1: </b>" + str(sw_cfg.GetVoltage_1.value) + " В <br>" +
                            "<b>Voltage L2: </b>" + str(sw_cfg.GetVoltage_2.value) + " В <br>" +
                            "<b>Voltage L3: </b>" + str(sw_cfg.GetVoltage_3.value) + " В <br>" +
                            "<b>Current L1: </b>" + str(sw_cfg.GetCurrent_1.value) + " А <br>" +
                            "<b>Current L2: </b>" + str(sw_cfg.GetCurrent_2.value) + " А <br>" +
                            "<b>Current L3: </b>" + str(sw_cfg.GetCurrent_3.value) + " А <br>" +
                            "<b>Temperature: </b>" + str(sw_cfg.GetTemp.value) + " °C")
                        # Removing the highlight of the polled device
                        self.interface["cmri_{0}{1}".format(stand, place)].setStyleSheet("")
                        # Suspending execution of the polling thread for the given number of seconds
                        sleep(sw_cfg.polling_time)
            # Actions when the do_pause = True set
            while getattr(polling_thread, "do_pause"):
                # Checking for the polling stop do_run = False
                if not getattr(polling_thread, "do_run"):
                    break
                # Resetting the specified address
                sw_cfg.cmri_dll.CMRI_Reset(c_long(sw_cfg.reset_id))
                # Exiting from the pause
                sw_cfg.polling_thread.do_pause = False

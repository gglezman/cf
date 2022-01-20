#
# Author: Greg Glezman
#
# Copyright (c) 2018-2022 G.Glezman.  All Rights Reserved.
#
# This file contains help text and support for the Cash Flow application

import webbrowser
import os
from scrollable_win import ScrollableWin
import data_file_constants as dfc


version_info = "\nVersion Information\
                \n\n Version Number: {}\
                \n\n Release Date:   {}\
                \n\n Author:         Gregory Glezman".format(
                dfc.SW_VERSION, dfc.SW_RELEASE_DATE)


class Help:
    def __init__(self, topic, master=None):
        """Open the Help window"""
        if topic == "HELP_ABOUT":
            ScrollableWin("Help - " + topic, version_info, master)
        else:
            help_file_url = "file:///{}/{}#{}".format(os.getcwd(), dfc.HELP_FILE_NAME, topic)
            webbrowser.open(help_file_url)

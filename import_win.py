#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to import data from other sources. (Notably brokerage houses and banks)
# This file contains the classes that puts up the import windows.

import csv
import re
from datetime import date
import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime
import data_file_constants as dfc
import utils as local_util
from import_support import process_fidelity_account_download
from import_support import process_kearny_account_download
from import_support import process_cap1_account_download


class ImportAccountsWin:
    """Open the Import Accounts Data window.

    This window will present a list of accounts that have defined
    import methods. The user can import data for any account in the list.
    On close the data is then fed back to the database for storage.

    :param parent: cf_gui
    :param accounts: list of accounts which have an update_method defined.
        Each entry in the list is a dictionary with the following keys:
        {'account', 'account_id', 'update_method'}.
    """

    def __init__(self, parent, accounts):
        self.parent = parent
        self.accounts = accounts
        self.cf_gui = parent.parent

        ###############################################
        # The window...
        ###############################################
        self.win = tk.Toplevel()
        self.win.title("Import Account Data")
        self.win.protocol("WM_DELETE_WINDOW", self.cancel_win)

        ###############################################
        # Create the Frames
        ###############################################
        self.accounts_frame = local_util.add_frame(self.win)
        self.controls_frame = local_util.add_controls_frame(self.win)
        self.button_frame = local_util.add_button_frame(self.controls_frame)

        ###############################################
        # Fill the frames
        ###############################################
        self.add_accounts(self.accounts_frame, accounts)
        self.add_control_buttons(self.button_frame, )

    def add_accounts(self, frame, accounts):
        """Add the given accounts to the frame

        Each row includes The name, account number and an import button.
        A function is assigned to each button, and the function is
        invoked with the corresponding row number when the button is depressed.

        :param frame: to fill in
        :param accounts: list of accounts to place in frame
        :return: None
        """
        row = 0
        col = 0
        ttk.Label(frame,
                  text="Account Name",
                  width=dfc.FW_MED,
                  style='Centered.TLabel').grid(row=row, column=col)
        col += 1
        ttk.Label(frame,
                  text="Account Id",
                  width=dfc.FW_SMALL,
                  style='Centered.TLabel').grid(row=row, column=col)
        col += 1
        ttk.Label(frame,
                  text="Action",
                  width=dfc.FW_SMALL,
                  style='Centered.TLabel').grid(row=row, column=col)

        for rec in accounts:
            row += 1
            col = 0
            ttk.Label(frame,
                      text=rec['account'],
                      width=dfc.FW_MED,
                      style='ThinLeft.TLabel').grid(row=row, column=col)
            col += 1
            ttk.Label(frame,
                      text=rec['account_id'],
                      width=dfc.FW_SMALL,
                      style='ThinLeft.TLabel').grid(row=row, column=col)
            col += 1
            ttk.Button(frame, text='Import',
                       style='Thin.TButton',
                       command=lambda entry=row - 1: self.import_account(entry)). \
                grid(row=row, column=col)

    def add_control_buttons(self, frame):
        """

        :param frame: to fill in
        :return: None
        """
        close_butt = ttk.Button(frame, text='close',
                                style='Medium.TButton',
                                command=self.cancel_win)
        close_butt.pack(side=tk.RIGHT)

    def cancel_win(self):
        """User has decided to Close the Import Accounts Window.

        Close up and signal caller that the window is closed."""
        # self.close_subordinate_windows()  # just in case...

        self.parent.ImportAccountsWin_return()

        self.win.destroy()

    def import_account(self, entry_num):
        """User has selected an account to import.

         This function is invoked when the user hits the import button.
         This function will dispatch the appropriate method based on the
         update_method defined for the account.
        :param entry_num: index into the accounts
        list of account to import
        :return: None
        """
        account = self.accounts[entry_num]

        if self.accounts[entry_num]['update_method'] == "Fidelity Export":
            fm =  self.parent.parent.get_file_manager()
            file_content = fm.open_account_import(process_fidelity_account_download,
                                                  account['account_id'])
            #self.cf_gui.update_account(account['account_id'], file_content)

        elif self.accounts[entry_num]['update_method'] == "Kearny Download":
            account_details = self.parent.parent.get_file_manager(). \
                open_account_import(
                process_kearny_account_download, account['account_id'])
            #self.cf_gui.update_account(account['account_id'], account_details)

        elif self.accounts[entry_num]['update_method'] == "Cap1 Download":
            account_details = self.parent.parent.get_file_manager(). \
                open_account_import(
                process_cap1_account_download, account['account_id'])
            #self.cf_gui.update_account(account['account_id'], account_details)

        else:
            messagebox.showerror("Import Error",
                                 "Unknown account update method: '{}'".format(
                                     self.accounts[entry_num]['update_method']))
            self.cf_gui.log(logging.ERROR,
                            "Import Error: Unknown account update method: '{}'".format(
                                self.accounts[entry_num]['update_method']))


class ImportBondDetailsWin:
    def __init__(self, parent, accounts):
        self.parent = parent

        print(accounts)
        ###############################################
        # The window...
        ###############################################
        self.win = tk.Toplevel()
        self.win.title("Import Bond Detail")
        self.win.protocol("WM_DELETE_WINDOW", self.cancel_win)

        ###############################################
        # Create the Frames
        ###############################################
        self.import_frame = local_util.add_frame(self.win)
        self.accounts_frame = local_util.add_borderless_frame(
            self.import_frame, i_pad=(2, 4))
        self.controls_frame = local_util.add_controls_frame(self.win)
        self.button_frame = local_util.add_button_frame(self.controls_frame)

        ###############################################
        # Fill the frames
        ###############################################
        self.add_accounts(self.accounts_frame, accounts)
        self.add_control_buttons(self.button_frame, )

    def add_accounts(self, frame, accounts):
        pass

    def add_control_buttons(self, frame):
        close_butt = ttk.Button(frame, text='close',
                                style='Medium.TButton',
                                command=self.cancel_win)
        close_butt.pack(side=tk.RIGHT)

    def cancel_win(self):
        """User has decided to Cancel. Close up and signal caller"""
        # self.close_subordinate_windows()  # just in case...

        self.parent.ImportBondDetailsWin_return()

        self.win.destroy()



#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2019 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to import data from other sources. (Notably brokerage houses and banks)

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

#########################################################
# Any method of importing Account Information must be
# added to the following List. This list is used when
# presenting Import methods for Edit/ Account
#########################################################
ImportMethodsSupported = ["Manual", "Fidelity Export", "Kearny Download",
                          "Cap1 Download"]


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
                       command=lambda entry=row-1: self.import_account(entry)).\
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
            account_details = self.parent.parent.get_file_manager().\
                open_account_import(
                    self.process_fidelity_account_import, account['account_id'])
            self.cf_gui.update_account(account['account_id'], account_details)

        elif self.accounts[entry_num]['update_method'] == "Kearny Download":
            account_details = self.parent.parent.get_file_manager(). \
                open_account_import(
                    self.process_kearny_account_download, account['account_id'])
            self.cf_gui.update_account(account['account_id'], account_details)

        elif self.accounts[entry_num]['update_method'] == "Cap1 Download":
            account_details = self.parent.parent.get_file_manager(). \
                open_account_import(
                    self.process_cap1_account_download, account['account_id'])
            self.cf_gui.update_account(account['account_id'], account_details)

        else:
            messagebox.showerror("Import Error",
                                 "Unknown account update method: '{}'".format(
                                     self.accounts[entry_num]['update_method']))
            self.cf_gui.log(logging.ERROR,
                            "Import Error: Unknown account update method: '{}'".format(
                                self.accounts[entry_num]['update_method']))

    def process_fidelity_account_import(self, file_handle, account_id):
        """ """
        # "Account Name/Number"
        # "Symbol",
        # "Description",
        # "Quantity",
        # "Last Price",
        # "Last Price Change",
        # "Current Value",
        # "Today's Gain/Loss Dollar",
        # "Today's Gain/Loss Percent",
        # "Total Gain/Loss Dollar",
        # "Total Gain/Loss Percent","
        # Cost Basis Per Share",
        # "Cost Basis Total","
        # Type"

        account_details = []
        reader = csv.DictReader(file_handle)
        try:
            for entry in reader:
                if entry['Account Name/Number'] == account_id:
                    # classify the entry
                    new_entry = {}
                    new_entry['investment_type'] = self.classify_instrument(entry)
                    new_entry['date'] = date.today().strftime(dfc.DATE_FORMAT)
                    new_entry['symbol'] = entry['Symbol']
                    new_entry['description'] = entry['Description']
                    new_entry['value'] = entry['Current Value'].replace('$', '')
                    new_entry['quantity'] = entry['Quantity']
                    account_details.append(new_entry)

        except KeyError:
            messagebox.showerror("Account Error", "Incorrect File Format")
            self.cf_gui.log(logging.ERROR, "Account Error, Incorrect File Format")

        if len(account_details) == 0:
            messagebox.showerror("Import Warning",
                                 "There are no records in the imported file")
        return account_details

    def process_kearny_account_download(self, file_handle, account_id):
        """ Procedure for downloading from kearny.
        login, click on the high Yield Checking, click on Download
             Current Statement
             .csv
        """
        # "Account"
        # "ChkRef"
        # "Debit"
        # "Credit"
        # "Balance"
        # "Date"
        # "Description

        account_details = []
        reader = csv.DictReader(file_handle)
        entry = reader.__next__()
        try:
            if entry['Account'] == account_id:
                # this is strictly a cash account
                entry['investment_type'] = 'ca'
                entry['symbol'] = "NOSYM"
                entry['date'] = entry['Date']
                entry['description'] = "Checking Balance"
                entry['value'] = entry['Balance']
                account_details.append(entry)

        except KeyError:
            messagebox.showerror("Account Error", "Incorrect File Format")
            self.cf_gui.log(logging.ERROR, "Account Error, Incorrect File Format")

        if len(account_details) == 0:
            messagebox.showerror("Import Warning",
                                 "There are no records in the imported file")
        return account_details

    def process_cap1_account_download(self, file_handle, account_id):
        """ Procedure for downloading from cap 1.
        login, click on the Cap 360 Money Mkt account, click on Download
        .csv
        30 days
        """
        #  Account Number,
        #  Transaction Date,
        #  Transaction Amount,
        #  Transaction Type,
        #  Transaction Description,
        #  Balance

        account_details = []
        reader = csv.DictReader(file_handle)
        entry = reader.__next__()
        try:
            # The download specifies only the last 4 chars in the account #
            if entry['Account Number'] == account_id[-4:]:
                # this is strictly a cash account
                entry['investment_type'] = 'ca'
                entry['symbol'] = "NOSYM"
                entry['date'] = date.today().strftime(dfc.DATE_FORMAT)
                entry['description'] = "Money Market Balance"
                entry['value'] = entry['Balance']
                account_details.append(entry)

        except KeyError:
            messagebox.showerror("Import Error", "Incorrect File Format")
            self.cf_gui.log(logging.ERROR, "Import Error, Incorrect File Format")

        if len(account_details) == 0:
            messagebox.showerror("Import Warning",
                                 "There are no records in the imported file")
        return account_details

    def classify_instrument(self, instrument):
        """Classify the investment instrument by its symbol.

        :param instrument: Dictionary including {symbol}
        :return: "ca","fund","bnd","Unknown"
        """
        symbol = instrument['Symbol']

        match_obj = re.match(r".*\*\*", symbol)
        if match_obj is not None:
            return "ca"

        match_obj = re.match("[A-Z]{4}X", symbol)
        if match_obj is not None:
            return "fund"    # mutual fund

        match_obj = re.match("[A-Z]{3,4}", symbol)
        if match_obj is not None:
            return "fund"    # stock/EFT

        match_obj = re.match("[0-9][A-Z0-9]{6,8}", symbol)
        if match_obj is not None:
            return "bond"
        else:
            messagebox.showerror("Import Error",
                                 "Unclassifiable symbol: {}".format(symbol))
            self.cf_gui.log(logging.ERROR,
                            "Import Error: Unclassifiable symbol: {}".format(symbol))
            return "unknown"


class ImportBondDetailsWin:
    def __init__(self, parent, accounts):
        self.parent = parent

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


class ImportFidelityBondList:
    FID_FORMAT = "%m/%d/%Y"

    def __init__(self, account_id_to_account_map):
        self.account_id_to_account_map = account_id_to_account_map
        self.records = []

    def process_bond_list(self, file_handle):
        """Read in a bond list .csv file from Fidelity.

        Convert the Fidelity record to a CF record. That is, use
        the keys we use in a standard CF bond records.

        Special Processing

        1. The quantity reported is 1000x the number purchased.
        2. Any dates in the record have to be reformatted
        3. The imported record contains an account_id which must be converted
           to an account name.

        Note that when a new bond is encountered, we don't have the following:

        1. purchase price
        2. settlement_date
        3. fee
        4. compounding
        """
        #  mapping  (Fidelity_key, CF_Key)
        key_map = [{'import': 'CUSIP', 'rec': 'cusip'},
                   {'import': 'Description', 'rec': 'issuer'},
                   {'import': 'Coupon', 'rec': 'coupon'},
                   {'import': 'Maturity', 'rec': 'maturity_date'},
                   {'import': 'Account', 'rec': 'account'},
                   {'import': 'Most Recent Price', 'rec': 'most_recent_price'},
                   {'import': "Moody's Rating", 'rec': 'moodys_rating'},
                   {'import': 'Product Type', 'rec': 'product_type'},
                   {'import': 'S&P Rating', 'rec': 's&p_rating'},
                   {'import': 'Most Recent Value', 'rec': 'most_recent_value'},
                   {'import': 'QTY', 'rec': 'quantity'},
                   {'import': 'Call Date', 'rec': 'next_call_date'},
                   {'import': 'Estimated Yield', 'rec': 'est_yield'},
                   ]
        ###############################################
        # Read in a Fidelity Bond list
        ###############################################
        self.records.clear()

        next(file_handle)  # header in csv file

        reader = csv.DictReader(file_handle)

        for bond in reader:
            # There is a lot of fluff at the end of the file. Stop when
            # a record doesn't have a valid cusip.
            # The Cusip format is '="cusip"'
            if len(bond['CUSIP']) != 0:  # valid record
                rec = {}
                rec_is_valid = True  # assume success
                for key_set in key_map:
                    if key_set['import'] in bond:
                        rec[key_set['rec']] = bond[key_set['import']]

                        ########################################
                        # The quantity value needs some tweaks
                        ########################################
                        if key_set['rec'] == 'quantity':
                            # strip comma, convert to int, divide by 1000
                            rec[key_set['rec']] = \
                                int(rec[key_set['rec']].replace(',', '')) / 1000
                        ########################################
                        # The most recent value value needs a tweak
                        #######################################
                        if key_set['rec'] == 'most_recent_value':
                            # strip the $ and comma
                            rec[key_set['rec']] = \
                                rec[key_set['rec']].replace('$', '')
                            rec[key_set['rec']] = \
                                float(rec[key_set['rec']].replace(',', ''))
                        ########################################
                        # Dates need to be put in the proper format
                        ########################################
                        if key_set['rec'] == 'maturity_date' or \
                                key_set['rec'] == 'next_call_date ':
                            # convert month/day/year to a date object
                            d = datetime.strptime(
                                    rec[key_set['rec']],
                                    ImportFidelityBondList.FID_FORMAT)

                            # convert the date to the normalized format
                            rec[key_set['rec']] = d.strftime(dfc.DATE_FORMAT)

                        ########################################
                        # The import record contains account_id,
                        # while the bond record contains account
                        ########################################
                        if key_set['rec'] == 'account':
                            if rec[key_set['rec']] in \
                                    self.account_id_to_account_map:
                                rec['account'] = self.account_id_to_account_map[
                                    rec[key_set['rec']]]
                            else:
                                msg = "Unable to find an account with the "
                                msg += "following account ID :"
                                msg += "{} ".format(rec[key_set['rec']])
                                msg += "\nfor cusip: "
                                msg += "{}. ".format(rec['cusip'])
                                msg += "\nVerify the account ID in cash "
                                msg += "accounts."
                                msg += "\nNote account IDs are case sensitive."
                                messagebox.showerror("Account Error", msg)
                                rec_is_valid = False
                    else:
                        raise ValueError(
                                "Expected key not found in imported rec: {}".format(
                                        key_set['import']))
                if rec_is_valid:
                    self.records.append(rec)
            else:
                # after the first record with no cusip, the rest is fluff
                break

    def get_bond_records(self):
        """Return records in the cf format for bonds"""

        return self.records

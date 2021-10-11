#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to manage files.
#

import sqlite3
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import logging
import csv
import utilities as util
import data_file_constants as dfc
from cf_upgrade import data_file_upgrade

DATA_FILE_MAGIC_ID = 't$9nhf5&fju%nh'


class FileManager:
    """File manager for the cash flow app.

    Manage the database file.  This object owns the db_conn for the open
    database
    """
    def __init__(self, logger):
        self.logger = logger
        self.data_filename = ""
        self.db_conn = None
        self.gui = None

    def set_gui(self, gui):
        self.gui = gui

    def open_database_file(self):
        filename = askopenfilename(
                filetypes=(("Database File","*.db"), ("Data File", "*.dat"), ("All Files", "*.*")),
                title="Open a Data File")
        if filename:
            self.data_filename = filename
            # todo - what id you attempt to open a garbage file
            self.db_conn = sqlite3.connect(filename)
            # todo - I think this is where I should trigger an upgrade

            # Read in the settings
            cursor = self.db_conn.execute(
                "SELECT tracking_months,default_account,bonds_per_page,graph_type FROM settings")
            row = cursor.fetchone()
            self.gui.set_setting('tracking_months',row[0])
            self.gui.set_setting('default_account',row[1])
            self.gui.set_setting('bonds_per_page',row[2])
            self.gui.set_setting('graph_type',row[3])
        return filename

    def write_data_file(self):
        """
        # todo - do we even need a write_data_file any longer?
        #        the individual commits should be sufficient
        # Who calls this and can I map those calls to commits?

        self.logger.log(logging.INFO,
                    "{}: {}".format(util.f_name(),self.data_filename))

        file_handle = open(self.data_filename, 'w', newline='')
        file_handle.write(DATA_FILE_MAGIC_ID + "\n")
        file_handle.write(dfc.SW_VERSION + "\n")
        file_handle.write("Reserved 1" + "\n")
        file_handle.write("Reserved 2" + "\n")

        # Accounts
        file_handle.write(str(len(self.parent.get_accounts())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.acc_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_accounts():
            writer.writerow(entry)

        # cash accounts
        file_handle.write(str(len(self.parent.get_cash_accounts())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.ca_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_cash_accounts():
            writer.writerow(entry)

        # cds
        file_handle.write(str(len(self.parent.get_cds())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.cd_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_cds():
            writer.writerow(entry)

        # loans
        file_handle.write(str(len(self.parent.get_loans())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.loan_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_loans():
            writer.writerow(entry)

        # bonds
        file_handle.write(str(len(self.parent.get_bonds())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.bond_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_bonds():
            writer.writerow(entry)

        # funds
        file_handle.write(str(len(self.parent.get_funds())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.fund_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_funds():
            writer.writerow(entry)

        # transfers
        file_handle.write(str(len(self.parent.get_transfers())) + "\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.xfer_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for entry in self.parent.get_transfers():
            writer.writerow(entry)

        # Settings
        file_handle.write("1\n")
        writer = csv.DictWriter(file_handle,
                                fieldnames=dfc.settings_fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerow(self.parent.get_settings())

        file_handle.close()

    """
    def new_data_file(self):
        """Query the user for the name of the database and create it"""
        filename = asksaveasfilename(
                filetypes=(("Database File", "*.db"), ("All Files", "*.*")),
                title="Create a New Database File",
                defaultextension=".db")
        if filename:
            self.data_filename = filename
            self.logger.log(logging.INFO, "{}: {}".format(util.f_name(), filename))
            self.create_db(filename)
        return filename

    def is_data_file_open(self):
        if self.db_conn == None:
            return False
        else:
            return True

    def create_db(self, filename):
        """Create a database file.

        Note that this function defines the schema for the current version
        of this application. It also adds the version number table to the DB
        """
        self.db_conn = sqlite3.connect(filename)

        self.db_conn.execute('''CREATE TABLE version_info
                 (base_version        TEXT NOT NULL);''')

        self.db_conn.execute('''CREATE TABLE accounts
             (account_id          TEXT  PRIMARY KEY  NOT NULL,
             account_name         TEXT  NOT NULL,
             opening_date         TEXT  NOT NULL,
             account_type         TEXT  NOT_NULL,
             update_method        TEXT  NOT_NULL,
             note                 TEXT);''')

        self.db_conn.execute('''CREATE TABLE bonds
             (bond_id             INTEGER PRIMARY KEY AUTOINCREMENT,
             account_id           TEXT NOT NULL,
             bond_price           REAL NOT NULL,
             quantity             INT,
             coupon               REAL NOT NULL,
             fee                  REAL NOT NULL,
             purchase_date        TEXT NOT NULL,
             maturity_date        TEXT NO NULL,
             frequency            TEXT NOT NULL,
             issuer               TEXT NOT NULL,
             cusip                TEXT NOT NULL,
             call_date            TEXT,
             call_price           REAL,
             most_recent_price    REAL,
             moodys_rating        TEXT,
             product_type         TEXT,
             snp_rating           TEXT,
             most_recent_value    REAL,
             next_call_date       TEXT,
             est_yield            REAL,
             FOREIGN KEY(account_id) REFERENCES accounts(account_id));''')

        self.db_conn.execute('''CREATE TABLE cash_accounts
             (cash_account_id     INTEGER PRIMARY KEY AUTOINCREMENT,
             account_id           TEXT NOT NULL,
             balance              REAL,
             rate                 REAL,
             interest_date        TEXT NOT NULL,
             frequency            TEXT NOT NULL,
             note                 TEXT NOT NULL,
             FOREIGN KEY(account_id) REFERENCES accounts(account_id));''')

        self.db_conn.execute('''CREATE TABLE CDs
             (CD_id               INTEGER PRIMARY KEY AUTOINCREMENT,
             account_id           TEXT NOT NULL,
             purchase_price       REAL,
             quantity             INT,
             rate                 REAL,
             purchase_date        TEXT NOT NULL,
             maturity_date        TEXT NOT_NULL,
             frequency            TEXT NOT NULL,
             cusip                TEXT,
             FOREIGN KEY(account_id) REFERENCES accounts(account_id));''')

        self.db_conn.execute('''CREATE TABLE funds
             (fund_id             INTEGER PRIMARY KEY AUTOINCREMENT,
             account_id           TEXT NOT NULL,
             symbol               TEXT,
             date                 TEXT,
             balance              REAL,
             est_roi              REAL,
             FOREIGN KEY(account_id) REFERENCES accounts(account_id));''')

        self.db_conn.execute('''CREATE TABLE transfers
             (transfer_id         INTEGER PRIMARY KEY AUTOINCREMENT,
             fromAccount_id       TEXT NOT NULL,
             toAccount_id         TEXT NOT NULL,
             amount               REAL,
             frequency            TEXT,
             inflation            REAL,
             note                 TEXT);''')

        self.db_conn.execute('''CREATE TABLE loans
             (loan_id             INTEGER PRIMARY KEY AUTOINCREMENT,
             account_id           TEXT NOT NULL,
             balance              REAL,
             rate                 REAL,
             orig_date            TEXT,
             payoff_date          TEXT,
             frequency            TEXT,
             note                 TEXT,
             FOREIGN KEY(account_id) REFERENCES accounts(account_id)
             );''')

        self.db_conn.execute('''CREATE TABLE settings
            (
            tracking_months      INT,
            default_account      TEXT,
            bonds_per_page       INT,
            graph_type           TEXT
            );''')

        self.db_conn.execute("INSERT INTO version_info (base_version) VALUES('2.00')")
        self.db_conn.commit()

    def dump_db(self):

        # Print the DB version number
        cursor = self.db_conn.execute("SELECT base_version from version_info")
        for row in cursor:
            print("DB Version = ", row[0], "\n")

        # Print accounts
        cursor = self.db_conn.execute(
            "SELECT account_id, account_name, opening_date, account_type, update_method, note from accounts")

        for row in cursor:
            print("account_name  =  ", row[1])
            print("account_id    =  ", row[0])
            print("opening_date  =  ", row[2])
            print("account_type  =  ", row[3])
            print("update_method =  ", row[4])
            print("note          =  ", row[5], "\n")

        # Print cash accounts
        cursor = self.db_conn.execute(
            "SELECT cash_account_id, account_id, balance, rate, interest_date, frequency, note from cash_accounts")

        for row in cursor:
            print("cash_account_id = ", row[0])
            print("account_id     =  ", row[1])
            print("balance        =  ", row[2])
            print("rate           =  ", row[3])
            print("interest_date  =  ", row[4])
            print("frequency      =  ", row[5])
            print("note           =  ", row[6], "\n")

        # Print CDs
        cursor = self.db_conn.execute(
            "SELECT * from CDs")

        for row in cursor:
            print("CD_id          = ", row[0])
            print("account_id     =  ", row[1])
            print("purchase_price =  ", row[2])
            print("quantity       =  ", row[3])
            print("rate           =  ", row[4])
            print("purchase_date  =  ", row[5])
            print("maturity_date  =  ", row[6])
            print("frequency      =  ", row[7])
            print("cusip          =  ", row[8], "\n")

        # Print Loans
        cursor = self.db_conn.execute(
            "SELECT * from loans")

        for row in cursor:
            print("loan_id     = ", row[0])
            print("account_id  = ", row[1])
            print("balance     = ", row[2])
            print("rate        = ", row[3])
            print("orig_date   = ", row[4])
            print("payoff_date = ", row[5])
            print("frequency   = ", row[6])
            print("note        = ", row[7], "\n")

        # Print bonds
        cursor = self.db_conn.execute(
            "SELECT * from bonds")

        for row in cursor:
            print("bond_id            = ", row[0])
            print("account_id         = ", row[1])
            print("bond_price         = ", row[2])
            print("quantity           = ", row[3])
            print("coupon             = ", row[4])
            print("fee                = ", row[5])
            print("purchase_date      = ", row[6])
            print("maturity_date      = ", row[7])
            print("frequency          = ", row[8])
            print("issuer             = ", row[9])
            print("cusip              = ", row[10])
            print("call_date          = ", row[11])
            print("call_price         = ", row[12])
            print("most_recent_price  = ", row[13])
            print("moodys_rating      = ", row[14])
            print("product_type       = ", row[15])
            print("snp_rating         = ", row[16])
            print("most_recent_value  = ", row[17])
            print("next_call_date     = ", row[18])
            print("est_yield          = ", row[19], "\n")

        # Print transfers
        cursor = self.db_conn.execute(
            "SELECT * from transfers")

        for row in cursor:
            print("transfer_id     = ", row[0])
            print("fromAccount_id  = ", row[1])
            print("toAccount_id    = ", row[2])
            print("amount          = ", row[3])
            print("frequency       = ", row[4])
            print("inflation       = ", row[5])
            print("note            = ", row[6], "\n")

        # Print transfers
        cursor = self.db_conn.execute(
            "SELECT * from settings")

        for row in cursor:
            print("tracking_months  = ", row[0])
            print("default_account  = ", row[1])
            print("bonds_per_page   = ", row[2])
            print("graph_type       = ", row[3], "\n")

    #################################################################
    # todo - For the folllowing, I think I can write one function that takes
    #       filetypes, title and callback and token as an opaque parameter
    # These functions are for handling files downloaded from brokerage sites
    def open_bond_list(self, read_callback):
        """Open a csv file to read in bond information"""

        filename = askopenfilename(
                filetypes=(("Text File", "*.csv"), ("All Files", "*.*")),
                title="Open Bond List File")
        if filename:
            self.logger.log(logging.INFO,"FileManager::{}():".format(util.f_name()))
            with open(filename, 'r', newline='') as file_obj:
                read_callback(file_obj)

    def open_account_import(self, read_callback, account_id):
        """Open a csv file to read in Account information"""

        filename = askopenfilename(
                filetypes=(("Text File", "*.csv"), ("All Files", "*.*")),
                title="Open Account Import File")
        if filename:
            self.logger.log(logging.INFO,"FileManager::{}():".format(util.f_name()))
            with open(filename, 'r', newline='') as file_obj:
                # The callback will return an array of imported data
                #print("Account_ID is {}".format(account_id))
                return read_callback(file_obj, account_id)

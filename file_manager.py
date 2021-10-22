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
from occurrences import Occurrences
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

    # todo - once I stop reading settinsg on open, I can delete selg.gui
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

        self.db_conn.execute('''CREATE TABLE account
             (rec_id              TEXT  PRIMARY KEY  NOT NULL,
             account_name         TEXT  NOT NULL,
             account_number       TEXT  NOT_NULL,
             opening_date         TEXT  NOT NULL,
             account_type         TEXT  NOT_NULL,
             update_method        TEXT  NOT_NULL,
             note                 TEXT);''')

        self.db_conn.execute('''CREATE TABLE bond
             (rec_id              INTEGER PRIMARY KEY AUTOINCREMENT,
             account_rec_id       TEXT NOT NULL,
             account_name         TEXT  NOT NULL,
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
             FOREIGN KEY(account_rec_id) REFERENCES account(rec_id));''')

        self.db_conn.execute('''CREATE TABLE ca
             (rec_id              INTEGER PRIMARY KEY AUTOINCREMENT,
             account_rec_id       TEXT NOT NULL,
             account_name         TEXT  NOT NULL,
             balance              REAL,
             rate                 REAL,
             interest_date        TEXT NOT NULL,
             frequency            TEXT NOT NULL,
             note                 TEXT NOT NULL,
             FOREIGN KEY(account_rec_id) REFERENCES account(rec_id));''')

        self.db_conn.execute('''CREATE TABLE cd
             (rec_id              INTEGER PRIMARY KEY AUTOINCREMENT,
             account_rec_id       TEXT NOT NULL,
             account_name         TEXT  NOT NULL,
             purchase_price       REAL,
             quantity             INT,
             rate                 REAL,
             purchase_date        TEXT NOT NULL,
             maturity_date        TEXT NOT_NULL,
             frequency            TEXT NOT NULL,
             cusip                TEXT,
             FOREIGN KEY(account_rec_id) REFERENCES account(rec_id));''')

        self.db_conn.execute('''CREATE TABLE fund
             (rec_id              INTEGER PRIMARY KEY AUTOINCREMENT,
             account_rec_id       TEXT NOT NULL,
             account_name         TEXT  NOT NULL,
             symbol               TEXT,
             date                 TEXT,
             balance              REAL,
             est_roi              REAL,
             FOREIGN KEY(account_rec_id) REFERENCES account(rec_id));''')

        self.db_conn.execute('''CREATE TABLE transfer
             (rec_id              INTEGER PRIMARY KEY AUTOINCREMENT,
             from_account_rec_id  TEXT NOT NULL,
             to_account_rec_id    TEXT NOT NULL,
             from_acount_name     TEXT NOT NULL,
             to_acount_name       TEXT NOT NULL,
             amount               REAL,
             frequency            TEXT,
             inflation            REAL,
             note                 TEXT);''')

        self.db_conn.execute('''CREATE TABLE loan
             (rec_id              INTEGER PRIMARY KEY AUTOINCREMENT,
             account_rec_id       TEXT NOT NULL,
             account_name         TEXT  NOT NULL,
             balance              REAL,
             rate                 REAL,
             orig_date            TEXT,
             payoff_date          TEXT,
             frequency            TEXT,
             note                 TEXT,
             FOREIGN KEY(account_rec_id) REFERENCES account(rec_id)
             );''')

        self.db_conn.execute('''CREATE TABLE setting
            (
            tracking_months      INT,
            default_account      TEXT,
            entries_per_page     INT,
            graph_type           TEXT
            );''')

        self.db_conn.execute("INSERT INTO version_info (base_version) VALUES('2.00')")

        self.db_conn.execute("INSERT INTO setting (tracking_months," +
                             "default_account, entries_per_page, graph_type) "+
                             " VALUES('24','','33','bar')")

        self.db_conn.commit()

    @staticmethod
    def get_new_rec(instrument_type):
        """Return an new data file record based on instrument_type.

        The new record will have all the keys appropriate for
        the instrument_type and default values appropriate for the key.
        """
        acc_new_rec = {'rec_id': "", 'account_name':'','account_number': '',
                       'opening_date': "", 'account_type':"",
                       'update_method':"Manual", 'note': ""}
        ca_new_rec = {'rec_id':'', 'account_rec_id': "", 'account_name':'','balance': 0.0, 'rate': 0.0,
                      'interest_date': "", 'frequency': "monthly", 'note': ""}
        bond_new_rec = {'rec_id':'', 'account_rec_id': "", 'account_name':'','bond_price': 0.0, 'quantity': 0,
                        'coupon': 0.0, 'fee': 0.0, 'purchase_date': "", 'maturity_date': "",
                        'frequency': "", 'issuer': "", 'cusip': "",
                        'call_date': "None", 'call_price': 0.0,
                        'most_recent_price': 0.0, 'moodys_rating': "", 'product_type': "",
                        'snp_rating': "", 'most_recent_value': 0.0, 'next_call_date': "None",
                        'est_yield': 0.0}
        fund_new_rec = {'rec_id':'', 'account_rec_id': "", 'account_name':'','symbol': "", 'date': "", 'balance': 0.0,
                        'est_roi': 0.0}
        xfer_new_rec = {'rec_id":'', ''from_account_rec_id': "", 'to_account_rec_id': "",
                        'from_account_name':'', 'to_account_name':'',
                        'amount': 0.0, 'frequency': "", 'inflation':0, 'note': ""}
        loan_new_rec = {'rec_id':'', 'account_rec_id': "", 'account_name':'','balance': 0.0,
                        'rate': 0.0, 'orig_date': "", 'payoff_date': "",
                        'frequency': "", 'note': ""}
        cd_new_rec = {'rec_id':'', 'account_rec_id': "", 'account_name':'','purchase_price': 0.0, 'quantity': 0,
                      'rate': 0.0, 'purchase_date': "", 'maturity_date': "", 'frequency': "",
                      'cusip': ""}

        if instrument_type == 'account':
            return acc_new_rec.copy()
        elif instrument_type == 'ca':
            return ca_new_rec.copy()
        elif instrument_type == 'bond':
            return bond_new_rec.copy()
        elif instrument_type == 'fund':
            return fund_new_rec.copy()
        elif instrument_type == 'cd':
            return cd_new_rec.copy()
        elif instrument_type == 'loan':
            return loan_new_rec.copy()
        elif instrument_type == 'transfer':
            new_rec = xfer_new_rec.copy()
            new_rec['frequency'] = Occurrences.default_occurrence_spec()
            return new_rec
        else:
            raise TypeError("Invalid instrument_type: {}".format(instrument_type))


    def dump_db(self):
        """ Dump the content of the database to a file.

        We'll ask the user for a file name
        """
        filename = asksaveasfilename(
            filetypes =(("Text File", "*.txt"),("All Files","*.*")),
            title = "Save the Database",
            defaultextension=".txt")
        if filename:
            with open(filename, 'w', newline='') as text_file:
                # ######################################################
                # Get a list of tables in the DB
                # ######################################################
                cursor = self.db_conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [
                    v[0] for v in cursor.fetchall()
                    if v[0] != "sqlite_sequence"
                ]

                for table in tables:
                    text_file.write("******************\n")
                    text_file.write ("Table: {}\n".format(table))
                    text_file.write ("******************\n")
                    # ######################################################
                    # Get the column names in the table
                    # ######################################################
                    column_names = []
                    cursor = self.db_conn.execute("SELECT * FROM PRAGMA_TABLE_INFO(\'{}\');".format(table))
                    for row in cursor:
                        column_names.append(row[1])

                    # ######################################################
                    # Get the data and display it
                    # ######################################################
                    cursor = self.db_conn.execute("SELECT * FROM \'{}\';".format(table))
                    for row in cursor:
                        for i,column_name in enumerate(column_names):
                            text_file.write ("{:20}: {}\n".format(column_name, row[i]))
                        text_file.write ("\n")

    #################################################################
    # todo - For the following, I think I can write one function that takes
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

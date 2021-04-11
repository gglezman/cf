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
    def __init__(self, parent):
        self.parent = parent  # GUI
        self.data_filename = ""

    def open_data_file(self):
        filename = askopenfilename(
                filetypes=(("Data File", "*.dat"), ("All Files", "*.*")),
                title="Open a Data File")
        if filename:
            self.data_filename = filename
            self.read_data_file(filename)

        return filename

    def read_data_file(self, filename):
        """ Read in a file containing the users data.

        Notes:
        Data File format:

        - t$9nhf5&fju%nh         - Magic Tag file Id
        - version Number
        - reserved 1
        - reserved 2
        - num_account_entries
        - account_entries
        - num_cash_account_entries
        - cash_account_entries
        - num_cd entries
        - cd entries
        - num loan entries
        - loan entries
        - num bond entries
        - bond entries
        - num fund entries
        - fund entries
        - num transfer entries
        - transfer entries

        
        """
        self.parent.log(logging.INFO, "{}: {}".format(util.f_name(), filename))

        file_handle = open(filename, 'r', newline='')
        tag_file_id = next(file_handle).rstrip()
        if tag_file_id != DATA_FILE_MAGIC_ID:
            messagebox.showinfo("Improper File Format",
                                "'{}' is not a Data file".format(filename))
            return False

        # might have to do a version upgrade here
        file_handle = data_file_upgrade(filename, file_handle, self.parent)

        next(file_handle).rstrip()  # reserved1
        next(file_handle).rstrip()  # reserved2

        # Before reading the data file, we init the data_source storage.
        # We want the new data to replace the old, not add to it.
        # TODO - should we do the same for settings?
        self.parent.init_ds_storage()

        settings = []  # temp storage for settings

        instrument_type = [
                           self.parent.get_accounts(),
                           self.parent.get_cash_accounts(),
                           self.parent.get_cds(),
                           self.parent.get_loans(),
                           self.parent.get_bonds(),
                           self.parent.get_funds(),
                           self.parent.get_transfers(),
                           # TODO can we get settings from the settingsMgr
                           settings
                           ]
        for instrument in instrument_type:
            instrument.clear()
            num_recs = int(next(file_handle).rstrip())

            i = 0
            if num_recs > 0:
                file_reader = csv.DictReader(file_handle,
                                             quoting=csv.QUOTE_NONNUMERIC)
                for line in file_reader:
                    instrument.append(line)
                    i += 1
                    if i >= num_recs:
                        break
            else:
                # skip fieldnames if no entries
                next(file_handle)

        file_handle.close()

        # TODO - can we eliminate this
        self.parent.set_settings(settings)

    def write_data_file(self):
        self.parent.log(logging.INFO, "{}: {}".format(util.f_name(),
                                                      self.data_filename))

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

    def new_data_file(self):
        filename = asksaveasfilename(
                filetypes=(("Data File", "*.dat"), ("All Files", "*.*")),
                title="Create a New Data File",
                defaultextension=".dat")
        if filename:
            self.data_filename = filename
            self.parent.log(logging.INFO, "{}: {}".format(util.f_name(), filename))
            self.write_data_file()
        return filename

    def is_data_file_open(self):
        if self.data_filename == "":
            return False
        else:
            return True

    #################################################################

    def open_bond_list(self, read_callback):
        """Open a csv file to read in bond information"""

        filename = askopenfilename(
                filetypes=(("Text File", "*.csv"), ("All Files", "*.*")),
                title="Open Bond List File")
        if filename:
            self.parent.log(logging.INFO,
                            "FileManager::{}():".format(util.f_name()))
            with open(filename, 'r', newline='') as file_obj:
                read_callback(file_obj)

    def open_account_import(self, read_callback, account_id):
        """Open a csv file to read in Account information"""

        filename = askopenfilename(
                filetypes=(("Text File", "*.csv"), ("All Files", "*.*")),
                title="Open Account Import File")
        if filename:
            self.parent.log(logging.INFO,
                            "FileManager::{}():".format(util.f_name()))
            with open(filename, 'r', newline='') as file_obj:
                # The callback will return an array of imported data
                #print("Account_ID is {}".format(account_id))
                ret
                urn read_callback(file_obj, account_id)

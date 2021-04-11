#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to import data from other sources. (Notably brokerage houses and banks)
# This file contains the code to process the imported files.

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
ImportMethodsSupported = ["Manual", "Fidelity Download", "Kearny Download",
                          "Cap1 Download"]

def process_fidelity_account_download(file_handle, account_id):
    """ Process an exported Fidelity File

    PORTFOLIO IMPORT
    ----------------
    We are looking for a specific portfolio file - use the following procedure
    to obtain the file:
       At the Fidelity Web site landing page,
         Click on the All Accounts block (contains the portfolio total)
         Click on Positions tab
         Click on the Download button
       The correct file will contain all the expected keys listed below.


    Return - None
    """
    reader = csv.DictReader(file_handle)

    if is_file_fidelity_portfolio_file(reader):
        process_fidelity_portfolio_file(reader, account_id)
    else:
        # todo - beef up this error message
        messagebox.showerror("Import Warning",
                             "Unknown File Format")

def is_file_fidelity_portfolio_file(csv_reader):
    """Determine if the given file is a Fidelity Portfolio download.
    If it is, it will have a specific set of keys

    Retun True or False
    """
    expected_keys = [
        "Account Name/Number",
        "Symbol",
        "Description",
        "Quantity",
        "Last Price",
        "Last Price Change",
        "Current Value",
        "Today's Gain/Loss Dollar",
        "Today's Gain/Loss Percent",
        "Total Gain/Loss Dollar",
        "Total Gain/Loss Percent",
        "Cost Basis Per Share",
        "Cost Basis Total",
        "Type"]

    fieldnames = csv_reader.fieldnames
    for key in expected_keys:
        if key not in fieldnames:
            return False
    return True

def process_fidelity_portfolio_file(reader, account_id):
    """Process a Fidelity Portfolio file.

    The file will contain records for each element of the portfolio.
    Funds, bonds,...
    Categorize each input record and generate a record for the local database
    then append it as necessary
    """
    for entry in reader:
        if entry['Account Name/Number'] == account_id:
            instrument_type = classify_instrument(entry)
            if instrument_type == 'bond':
                rec = process_fidelity_bond_rec_in_portfolio(entry)
                #append rec to bond ;ist
                print("Bond : {}".format(rec))
            elif instrument_type == 'fund':
                rec = process_fidelity_fund_rec_in_portfolio(entry)
                # append rec to fund list
                print("fund : {}".format(rec))
            elif instrument_type == 'ca':
                rec = process_fidelity_ca_rec_in_portfolio(entry)
                # append rec to list
                print("cs : {}".format(rec))
            else:
                print(entry)
                messagebox.showerror("Import Warning",
                                     "Unknown Record in Import File")
                print(rec)
    return

def process_fidelity_bond_rec_in_portfolio(bond):
    """
    How to reconcile a list of bonds in this file with what's already in the DB?
      - If the download matches what's in the DB - no change
      - If download > DB
            create a new record for the remainder with the current date (?)
      - if download < DB
            assume bonds have been sold and use the first in / first out methodology


    :param bond:
    :return:
    """

    bond_key_map = [
        {'fid_key': 'Account Name/Number', 'local_key': 'account'},
        {'fid_key': 'Symbol', 'local_key': 'cusip'},
        {'fid_key': 'Description', 'local_key': 'issuer'},
        {'fid_key': 'Quantity', 'local_key': 'quantity'},
        {'fid_key': 'Last Price', 'local_key': 'most_recent_price'},
        # {'fid_key':'Current Value', 'local_key':'},
    ]
    rec = {}
    for key_set in bond_key_map:
        # the general case
        rec[key_set['local_key']] = bond[key_set['fid_key']]

        if key_set['fid_key'] == 'Account Name/Number':
            # todo - map to account name
            rec[key_set['local_key']] = bond[key_set['fid_key']]
        elif key_set['fid_key'] == 'Description':
            # name, coupon, maturity date
            match_obj = re.match("(.*) ([0-9]{1,2}.[0-9]*)% ([0-9]{2})/([0-9]{2})/([0-9]{4})",
                                  bond[key_set['fid_key']])
            rec[key_set['local_key']] = match_obj.group(1)   # cleaned up description
            rec['coupon'] = match_obj.group(2)
            rec['maturity_date'] = match_obj.group(5) + "-" + match_obj.group(4) + "-" +match_obj.group(3)
            """
            # todo - remove the following 
            print(match_obj.group(3))   # month
            print(match_obj.group(4))  # day
            print(match_obj.group(5))  # year
            year = re.sub("^0+", "", match_obj.group(5))      # remove leading zeros
            rec['maturity_date'] = datetime(int(year),
                                            int(match_obj.group(3)),
                                            int(match_obj.group(4)))
            """
    return rec

def process_fidelity_fund_rec_in_portfolio(entry):
    pass
def process_fidelity_ca_rec_in_portfolio(entry):
    pass

def process_kearny_account_download(file_handle, account_id):
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


def process_cap1_account_download(file_handle, account_id):
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


def classify_instrument(instrument):
    """Classify the investment instrument by its symbol.

    :param instrument: Dictionary including {symbol}
    :return: "ca","fund","bnd","Unknown"
    """
    symbol = instrument['Symbol']

    match_obj = re.match(r".*\*", symbol)
    if match_obj is not None:
        return "ca"

    match_obj = re.match("[A-Z]{4}X", symbol)
    if match_obj is not None:
        return "fund"  # mutual fund

    match_obj = re.match("[A-Z]{3,4}", symbol)
    if match_obj is not None:
        return "fund"  # stock/EFT

    match_obj = re.match("[0-9][A-Z0-9]{6,8}", symbol)
    if match_obj is not None:
        return "bond"
    else:
        messagebox.showerror("Import Error",
                             "Unclassifiable symbol: {}".format(symbol))
        self.cf_gui.log(logging.ERROR,
                        "Import Error: Unclassifiable symbol: {}".format(symbol))
        return "unknown"


class ImportFidelityBondList:
    """This class is used to process a Fidelity Bond csv file.

    To use this, create the class, call the process member them cal the get_
     member. The latter will return a lists of bonds in the file.
     """
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
        key_map = [{'fid_key': 'CUSIP', 'local_key': 'cusip'},
                   {'fid_key': 'Description', 'local_key': 'issuer'},
                   {'fid_key': 'Coupon', 'local_key': 'coupon'},
                   {'fid_key': 'Maturity', 'local_key': 'maturity_date'},
                   {'fid_key': 'Account', 'local_key': 'account'},
                   {'fid_key': 'Most Recent Price', 'local_key': 'most_recent_price'},
                   {'fid_key': "Moody's Rating", 'local_key': 'moodys_rating'},
                   {'fid_key': 'Product Type', 'local_key': 'product_type'},
                   {'fid_key': 'S&P Rating', 'local_key': 's&p_rating'},
                   {'fid_key': 'Most Recent Value', 'local_key': 'most_recent_value'},
                   {'fid_key': 'QTY', 'local_key': 'quantity'},
                   {'fid_key': 'Call Date', 'local_key': 'next_call_date'},
                   {'fid_key': 'Estimated Yield', 'local_key': 'est_yield'},
                   ]
        ###############################################
        # Read in a Fidelity Bond list
        ###############################################
        self.records.clear()

        next(file_handle)  # header in csv file

        reader = csv.DictReader(file_handle)

        # validate the fields in the file

        for bond in reader:
            # There is a lot of fluff at the end of the file. Stop when
            # a record doesn't have a valid cusip.
            # The Cusip format is '="cusip"'
            if len(bond['CUSIP']) != 0:  # valid record
                rec = {}
                rec_is_valid = True  # assume success
                for key_set in key_map:
                    if key_set['fid_key'] in bond:
                        rec[key_set['local_key']] = bond[key_set['fid_key']]

                        ########################################
                        # The quantity value needs some tweaks
                        ########################################
                        if key_set['local_key'] == 'quantity':
                            # strip comma, convert to int, divide by 1000
                            rec[key_set['local_key']] = \
                                int(rec[key_set['local_key']].replace(',', '')) / 1000
                        ########################################
                        # The most recent value value needs a tweak
                        #######################################
                        if key_set['local_key'] == 'most_recent_value':
                            # strip the $ and comma
                            rec[key_set['local_key']] = \
                                rec[key_set['local_key']].replace('$', '')
                            rec[key_set['local_key']] = \
                                float(rec[key_set['local_key']].replace(',', ''))
                        ########################################
                        # Dates need to be put in the proper format
                        ########################################
                        if key_set['local_key'] == 'maturity_date' or \
                                key_set['local_key'] == 'next_call_date ':
                            # convert month/day/year to a date object
                            d = datetime.strptime(
                                    rec[key_set['local_key']],
                                    ImportFidelityBondList.FID_FORMAT)

                            # convert the date to the normalized format
                            rec[key_set['local_key']] = d.strftime(dfc.DATE_FORMAT)

                        ########################################
                        # The import record contains account_id,
                        # while the bond record contains account
                        ########################################
                        if key_set['local_key'] == 'account':
                            if rec[key_set['local_key']] in \
                                    self.account_id_to_account_map:
                                rec['account'] = self.account_id_to_account_map[
                                    rec[key_set['local_key']]]
                            else:
                                msg = "Unable to find an account with the "
                                msg += "following account ID :"
                                msg += "{} ".format(rec[key_set['local_key']])
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
                                        key_set['fid_key']))
                if rec_is_valid:
                    self.records.append(rec)
            else:
                # after the first record with no cusip, the rest is fluff
                break

    def get_bond_records(self):
        """Return records in the cf format for bonds"""

        return self.records

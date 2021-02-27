# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# Upgrade a data file for a new version of the cf code.
# A copy of the original is created as a backup.  Its name is
#         filename.old_version
# The upgraded file has the original name
# 
# Here is the general flow of using the upgrader
# 
#  caller
#     opens data file and verifies magic tag
#  upgrader gets a filename, fileHandle
#     reads version
#     if upgrade required
#         close the file handle
#         reopen and write to a new file fileName.old_version (ie copy it)
#         reopen and
#         write the new version of the data file
#         create a dictionary for each entry, adjusting each entry
#         write the entry back out
#         close the upgraded file
#         reopen and advance beyond the magic number
#      return the fileHandle

import csv
import logging
from shutil import copyfile
import utilities as util
import data_file_constants as dfc


def get_raw_version(major, minor):
    """Minor version number maxes out at 99"""
    return major * 100 + minor


def data_file_upgrade(filename, file_handle, parent):
    """Upgrade until we are at the current release level"""

    while True:
        version = next(file_handle).rstrip()

        if version == dfc.SW_VERSION:
            # File is at current version
            return file_handle

        major = int(version.split(".")[0])
        minor = int(version.split(".")[1])
        raw_version = get_raw_version(major, minor)

        if raw_version < get_raw_version(1, 7):
            file_handle = upgrade_to_1_7(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 10):
            file_handle = upgrade_to_1_10(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 13):
            file_handle = upgrade_to_1_13(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 14):
            file_handle = upgrade_to_1_14(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 17):
            file_handle = upgrade_to_1_17(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 18):
            file_handle = upgrade_to_1_18(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 20):
            file_handle = upgrade_to_1_20(filename, file_handle, parent, version)
        elif raw_version < get_raw_version(1, 21):
            file_handle = upgrade_to_1_21(filename, file_handle, parent, version)
        else:
            # no further upgrade necessary
            return file_handle


def upgrade_to_1_21(filename, file_handle, parent, old_version):
    """Upgrade from 1.20 to 1.21.
    In this upgrade, split CashAccounts into Accounts and Cash Accounts
    """
    new_version = '1.21'
    data_block = []

    read_file_handle, write_file_handle = common_upgrade_open(
            filename, file_handle, parent, old_version, new_version)

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)

    # The following two are created from the existing CAs
    cash_accounts = []
    accounts = []

    ##########################################
    # Mods - CAs
    ##########################################
    for rec in data_block:
        account_rec = {}
        account_rec['account'] = rec['account']
        account_rec['account_id'] = rec['account_id']
        account_rec['opening_date'] = rec['opening_date']
        account_rec['account_type'] = dfc.account_types[0]  # this is new
        account_rec['update_method'] = "Manual"
        account_rec['note'] = rec['note']
        accounts.append(account_rec)

        ca_rec = {}
        ca_rec['account'] = rec['account']
        ca_rec['balance'] = float(rec['balance'])
        ca_rec['rate'] = float(rec['rate'])
        ca_rec['interest_date'] = rec['interest_date']
        ca_rec['frequency'] = rec['frequency']
        ca_rec['note'] = rec['note']
        cash_accounts.append(ca_rec)

    #########
    # Write
    #########
    write_block(write_file_handle, accounts, dfc.acc_1_21_fieldnames)
    write_block(write_file_handle, cash_accounts, dfc.ca_1_21_fieldnames)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.cd_1_21_fieldnames)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.loan_1_21_fieldnames)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])
        rec['call_price'] = float(rec['call_price'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_21_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Funds - this is new
    #######################

    # create an empty section
    data_block.clear()

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.fund_1_21_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()

    #######################
    # Transfers
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['amount'] = float(rec['amount'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.xfer_1_21_fieldnames)

    #######################
    # Settings
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods - none
    #########

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.settings_1_21_fieldnames)

    # clean up and return
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_20(filename, file_handle, parent, old_version):
    """Upgrade from 1.18 to 1.20.  In this upgrade,
    1. est_yeild => est_yield  in the bond record.
    """
    new_version = '1.20'
    data_block = []

    read_file_handle, write_file_handle = common_upgrade_open(
            filename, file_handle, parent, old_version, new_version)

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.ca_1_20_fieldnames)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.cd_1_20_fieldnames)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.loan_1_20_fieldnames)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # fix typo in field name
        rec['est_yield'] = rec['est_yeild']
        del rec['est_yeild']

        # remove the $ and comma
        rec['most_recent_value'] = rec['most_recent_value'].replace('$', '')
        rec['most_recent_value'] = rec['most_recent_value'].replace(',', '')

        # force proper type (??)
        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])
        rec['call_price'] = float(rec['call_price'])
        rec['most_recent_price'] = float(rec['most_recent_price'])
        rec['most_recent_value'] = float(rec['most_recent_value'])
        rec['est_yield'] = float(rec['est_yield'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_20_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Transfers
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['amount'] = float(rec['amount'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.xfer_1_20_fieldnames)

    #######################
    # Settings
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods - none
    #########

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.settings_1_20_fieldnames)

    # clean up and return
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_18(filename, file_handle, parent, old_version):
    """Upgrade from 1.17 to 1.18.  In this upgrade, add issuer to
    the bond record.
    """
    new_version = '1.18'
    data_block = []

    read_file_handle, write_file_handle = common_upgrade_open(
            filename, file_handle, parent, old_version, new_version)

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

        rec['account_id'] = ""  # this is new to this release

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.ca_1_18_fieldnames)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.cd_1_18_fieldnames)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.loan_1_18_fieldnames)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])
        rec['call_price'] = float(rec['call_price'])

        rec['issuer'] = ""  # these are new to this release
        rec['most_recent_price'] = 0.0
        rec['moodys_rating'] = ""
        rec['product_type'] = ""
        rec['s&p_rating'] = ""
        rec['most_recent_value'] = 0.0
        rec['next_call_date'] = "None"
        rec['est_yeild'] = 0.0

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_18_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Transfers
    ####################### 
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['amount'] = float(rec['amount'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.xfer_1_18_fieldnames)

    #######################
    # Settings
    ####################### 
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods - none
    #########

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.settings_1_18_fieldnames)

    # clean up and return 
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_17(filename, file_handle, parent, old_version):
    """Upgrade from 1.14 to 1.17.  In this upgrade, convert to a generic
    form of date."""

    new_version = '1.17'
    data_block = []

    parent.log(logging.INFO, "{}: Upgrading {} from {} to {}".format(
            util.f_name(), filename, old_version, new_version))

    ####################################
    # close the file to make a copy
    ####################################
    file_handle.close()
    old_filename = filename + '.' + old_version
    copyfile(filename, old_filename)

    ###################################################
    # reopen the backup and write a new version of the data file 
    ###################################################
    read_file_handle = open(old_filename, 'r', newline='')
    write_file_handle = open(filename, 'w', newline='')

    #######################
    # header stuff
    #######################
    data_file_id = next(read_file_handle).rstrip()
    write_file_handle.write(data_file_id + "\n")
    next(read_file_handle).rstrip()  # version
    write_file_handle.write(new_version + "\n")
    reserved1 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved1 + "\n")
    reserved2 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved2 + "\n")

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.ca_1_17_fieldnames)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.cd_1_17_fieldnames)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.loan_1_17_fieldnames)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])
        rec['call_price'] = float(rec['call_price'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_17_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Transfers
    ####################### 
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['amount'] = float(rec['amount'])

        # update the frequency
        freq = rec['frequency']

        # Some names have changed
        if freq == 'annual':
            freq = 'annually'
        elif freq == 'semi-annual':
            freq = 'semi-annually'

        # weekly, monthly and twice-a-month required an additional parameter
        if freq == 'once':
            new_freq = rec['date'] + ';' + rec['date'] + ';' + freq
        elif freq == 'weekly' or freq == 'monthly' or freq == 'twice-a-month':
            new_freq = rec['date'] + ';' + 'None' + ';' + freq + ';1'
        else:
            new_freq = rec['date'] + ';' + 'None' + ';' + freq
        rec['frequency'] = new_freq

        # delete the start date
        del rec['date']

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.xfer_1_17_fieldnames)

    #######################
    # Settings
    ####################### 
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods - none
    #########

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.settings_1_17_fieldnames)

    # clean up and return 
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_14(filename, file_handle, parent, old_version):
    """Upgrade from 1.13 to 1.14.  In this upgrade, support
    for settings in the .dat file is added."""

    new_version = '1.14'
    data_block = []

    parent.log(logging.INFO, "{}: Upgrading {} from {} to {}".format(
            util.f_name(), filename, old_version, new_version))

    ####################################
    # close the file to make a copy
    ####################################
    file_handle.close()
    old_filename = filename + '.' + old_version
    copyfile(filename, old_filename)

    ###################################################
    # reopen the backup and write a new version of the data file 
    ###################################################
    read_file_handle = open(old_filename, 'r', newline='')
    write_file_handle = open(filename, 'w', newline='')

    #######################
    # header stuff
    #######################
    data_file_id = next(read_file_handle).rstrip()
    write_file_handle.write(data_file_id + "\n")
    next(read_file_handle).rstrip()  # version
    write_file_handle.write(new_version + "\n")
    reserved1 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved1 + "\n")
    reserved2 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved2 + "\n")

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.ca_1_14_fieldnames)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.cd_1_14_fieldnames)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.loan_1_14_fieldnames)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])
        rec['call_price'] = float(rec['call_price'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_14_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Transfers
    ####################### 
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['amount'] = float(rec['amount'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.xfer_1_14_fieldnames)

    #######################
    # Settings
    ####################### 
    #########
    # Read - new, nothing to read
    #########
    # read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    data_block.clear()
    data_block.append(dfc.default_settings_1_14)

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.settings_1_14_fieldnames)

    # clean up and return 
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_13(filename, file_handle, parent, old_version):
    """Upgrade from 1.10-1.12 to 1.13.  In this upgrade, support
    for bond calls is added. That means just a couple new elements
    in the bond records."""

    new_version = '1.13'
    data_block = []

    parent.log(logging.INFO, "{}: Upgrading {} from {} to {}".format(
            util.f_name(), filename, old_version, new_version))

    ####################################
    # close the file to make a copy
    ####################################
    file_handle.close()
    old_filename = filename + '.' + old_version
    copyfile(filename, old_filename)

    ###################################################
    # reopen the backup and write a new version of the data file 
    ###################################################
    read_file_handle = open(old_filename, 'r', newline='')
    write_file_handle = open(filename, 'w', newline='')

    #######################
    # header stuff
    #######################
    data_file_id = next(read_file_handle).rstrip()
    write_file_handle.write(data_file_id + "\n")
    next(read_file_handle).rstrip()  # version
    write_file_handle.write(new_version + "\n")
    reserved1 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved1 + "\n")
    reserved2 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved2 + "\n")

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.ca_1_13_fieldnames)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.cd_1_13_fieldnames)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.loan_1_13_fieldnames)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        rec['call_price'] = float(0)
        rec['call_date'] = 'None'

        # force proper type (??)
        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_13_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Transfers
    ####################### 
    #########
    # Read
    #########
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        # force proper type (??)
        rec['amount'] = float(rec['amount'])

    #########
    # Write
    #########
    write_block(write_file_handle, data_block, dfc.xfer_1_13_fieldnames)

    # clean up and return 
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_10(filename, file_handle, parent, old_version):
    """Upgrade from 1.7-1.9 to 1.10.  In this upgrade, numerics are
    converted to float and QUOTE_NONNUMERIC is used on the write.
    also some fields names are changed and all references to 'type'
    are removed"""

    new_version = '1.10'
    data_block = []

    parent.log(logging.INFO, "{}: Upgrading {} from {} to {}".format(
            util.f_name(), filename, old_version, new_version))

    ####################################
    # close the file to make a copy
    ####################################
    file_handle.close()
    old_filename = filename + '.' + old_version
    copyfile(filename, old_filename)

    ###################################################
    # reopen the backup and write a new version of the data file 
    ###################################################
    read_file_handle = open(old_filename, 'r', newline='')
    write_file_handle = open(filename, 'w', newline='')

    #######################
    # header stuff
    #######################
    data_file_id = next(read_file_handle).rstrip()
    write_file_handle.write(data_file_id + "\n")
    next(read_file_handle).rstrip()  # version
    write_file_handle.write(new_version + "\n")
    reserved1 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved1 + "\n")
    reserved2 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved2 + "\n")

    #######################
    # CAs
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        if 'type' in rec:
            del rec['type']

        # clean up the CA record
        if 'quantity' in rec:
            del rec['quantity']
        rec['opening_date'] = rec['date_1']
        del rec['date_1']
        rec['interest_date'] = rec['date_2']
        del rec['date_2']

        # type conversions
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.ca_1_10_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # CDs
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        if 'type' in rec:
            del rec['type']

        # clean up the CD record
        rec['purchase_price'] = rec['balance']
        del rec['balance']
        rec['purchase_date'] = rec['date_1']
        del rec['date_1']
        rec['maturity_date'] = rec['date_2']
        del rec['date_2']
        rec['cusip'] = rec['note']
        del rec['note']

        # type conversions
        rec['purchase_price'] = float(rec['purchase_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.cd_1_10_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Loans
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        if 'type' in rec:
            del rec['type']

        # clean up the CA record
        if 'quantity' in rec:
            del rec['quantity']
        rec['orig_date'] = rec['date_1']
        del rec['date_1']
        rec['payoff_date'] = rec['date_2']
        del rec['date_2']

        # type conversions
        rec['balance'] = float(rec['balance'])
        rec['rate'] = float(rec['rate'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.loan_1_10_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Bonds
    #######################
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        if 'type' in rec:
            del rec['type']

        rec['bond_price'] = float(rec['bond_price'])
        rec['quantity'] = float(rec['quantity'])
        rec['coupon'] = float(rec['coupon'])
        rec['fee'] = float(rec['fee'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_10_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    #######################
    # Transfers
    ####################### 
    #########
    # Read
    #########
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        if 'type' in rec:
            del rec['type']

        rec['amount'] = float(rec['amount'])

    #########
    # Write
    #########
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.xfer_1_10_fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)

    # clean up and return 
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def upgrade_to_1_7(filename, file_handle, parent, old_version):
    """Upgrade from 1.6 to 1.7"""

    new_version = '1.7'
    data_block = []

    parent.log(logging.INFO, "{}: Upgrading {} from {} to {}".format(
            util.f_name(), filename, old_version, new_version))

    ####################################
    # close the file to make a copy
    ####################################
    file_handle.close()
    old_filename = filename + '.' + old_version
    copyfile(filename, old_filename)

    ###################################################
    # reopen the backup and write a new version of the data file 
    ###################################################
    read_file_handle = open(old_filename, 'r', newline='')
    write_file_handle = open(filename, 'w', newline='')

    #######################
    # header stuff
    #######################
    data_file_id = next(read_file_handle).rstrip()
    write_file_handle.write(data_file_id + "\n")
    next(read_file_handle).rstrip()  # version
    write_file_handle.write(new_version + "\n")
    reserved1 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved1 + "\n")
    reserved2 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved2 + "\n")

    #######################
    # CAs
    #######################
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        del rec['type']

    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.ca_1_7_fieldnames)
    writer.writeheader()
    for entry in data_block:
        writer.writerow(entry)

    #######################
    # CDs
    #######################
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        del rec['type']

    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle, fieldnames=dfc.cd_1_7_fieldnames)
    writer.writeheader()
    for entry in data_block:
        writer.writerow(entry)

    #######################
    # Loans
    #######################
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        del rec['type']

    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.loan_1_7_fieldnames)
    writer.writeheader()
    for entry in data_block:
        writer.writerow(entry)

    #######################
    # Bonds
    #######################
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        rec['purchase_date'] = rec['date_1']
        del rec['date_1']

        rec['maturity_date'] = rec['date_2']
        del rec['date_2']

        rec['bond_price'] = rec['balance']
        del rec['balance']

        rec['coupon'] = rec['rate']
        del rec['rate']

        rec['cusip'] = rec['note']
        del rec['note']

        del rec['type']

    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.bond_1_7_fieldnames)
    writer.writeheader()
    for entry in data_block:
        writer.writerow(entry)

    # Transfers
    data_block.clear()
    read_file_handle = read_block(read_file_handle, data_block)
    #########
    # Mods
    #########
    for rec in data_block:
        del rec['type']

    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle,
                            fieldnames=dfc.xfer_1_7_fieldnames)
    writer.writeheader()
    for entry in data_block:
        writer.writerow(entry)

    # clean up and return 
    return common_upgrade_close(read_file_handle, write_file_handle, filename)


def read_block(file_handle, data_block):
    """A block is the section for Cash Accounts, CDs, Bonds,... """

    data_block.clear()

    num_recs = int(next(file_handle).rstrip())
    i = 0
    if num_recs > 0:
        file_reader = csv.DictReader(file_handle)
        for line in file_reader:
            data_block.append(line)
            i += 1
            if i >= num_recs:
                break
    else:
        # skip fieldnames if no entries
        next(file_handle)

    return file_handle


def write_block(write_file_handle, data_block, fieldnames):
    write_file_handle.write(str(len(data_block)) + "\n")
    writer = csv.DictWriter(write_file_handle, fieldnames=fieldnames,
                            quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for rec in data_block:
        writer.writerow(rec)


def common_upgrade_open(filename, file_handle, parent, old_version, new_version):
    parent.log(logging.INFO, "{}: Upgrading {} from {} to {}".format(
            util.f_name(), filename, old_version, new_version))

    ####################################
    # close the file to make a copy
    ####################################
    file_handle.close()
    old_filename = filename + '.' + old_version
    copyfile(filename, old_filename)

    ###################################################
    # reopen the backup and write a new version of the data file 
    ###################################################
    read_file_handle = open(old_filename, 'r', newline='')
    write_file_handle = open(filename, 'w', newline='')

    #######################
    # header stuff
    #######################
    data_file_id = next(read_file_handle).rstrip()
    write_file_handle.write(data_file_id + "\n")
    next(read_file_handle).rstrip()  # version
    write_file_handle.write(new_version + "\n")
    reserved1 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved1 + "\n")
    reserved2 = next(read_file_handle).rstrip()
    write_file_handle.write(reserved2 + "\n")

    return read_file_handle, write_file_handle


def common_upgrade_close(read_file_handle, write_file_handle, filename):
    # close the files
    read_file_handle.close()
    write_file_handle.close()

    # reopen the upgraded file and read the first couple lines
    file_handle = open(filename, 'r', newline='')
    next(file_handle).rstrip()  # tag_file_id

    return file_handle

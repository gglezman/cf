#
# Author: Greg Glezman
#
# Copyright (c) 2018-2022 G.Glezman.  All Rights Reserved.
# 
# This file defines the content of the data file as it evolves
# through releases.
# 
# When the data file must change in content, define a new set 
# of fieldnames for the release and update the 'current' section
#
#

import platform

#################################
# Some useful constants
#################################
# The following software version should be updated with every release
SW_VERSION = "2.1"

# Field widths for display widgets
if platform.system() == 'Linux':
    FW_TINY = 1
    FW_SMALLEST = 6
    FW_SMALL = 10
    FW_MEDSMALL = 14
    FW_MED = 20
    FW_MEDLARGE = 25
    FW_LARGE = 30
    FW_OCC_FIRST_COL = 8  # used in the occurrence window
    FW_OCC_SECOND_COL = 11
else:
    FW_TINY = 1
    FW_SMALLEST = 6
    FW_SMALL = 11
    FW_MEDSMALL = 14
    FW_MED = 20
    FW_MEDLARGE = 25
    FW_LARGE = 30
    FW_OCC_FIRST_COL = 10  # used in the occurrence window
    FW_OCC_SECOND_COL = 14

SMALL_BORDER_WIDTH = 2
BORDER_WIDTH = 4

account_types = ['Checking', 'Brokerage', 'Savings', 'Money Market']
instrument_types = ['ca', 'bond', 'cd', 'loan', 'transfer', 'setting']

# the following should be used in conjunction with
#     datetime.strftime(xxx_FORMAT)
DATE_FORMAT = '%Y-%m-%d'
SHORT_DATE_FORMAT = '%m/%d'

# the following are rec_id definitions for pseudo accounts
INCOME_ACCOUNT_ID = 0
EXPENSE_ACCOUNT_ID = 1
FIRST_REAL_ACCOUNT = 2

# ###################################################
# Fieldnames for the data file
# ###################################################

# Note: The xx_new_rec 's are used to create a new record
#       of the associated type. They contain the default
#       values for a new rec

#################################
# As of  1.22
#################################
acc_1_22_fieldnames = ['account', 'account_id', 'opening_date', 'account_type', 'update_method', 'note']

ca_1_22_fieldnames = ['account', 'balance', 'rate', 'interest_date', 'frequency', 'note']

bond_1_22_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'issuer', 'call_date', 'call_price',
                        'most_recent_price', 'moodys_rating', 'product_type',
                        's&p_rating', 'most_recent_value', 'next_call_date',
                        'est_yield']

fund_1_22_fieldnames = ['account', 'fund', 'date', 'balance', 'est_roi',
                        'interest_date', 'frequency']

xfer_1_22_fieldnames = ['fromAccount', 'toAccount',
                        'amount', 'frequency', 'inflation', 'note']

loan_1_22_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']

cd_1_22_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

settings_1_22_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']

# todo - the following is still used
default_settings = {'tracking_months': 24, 'default_account': "",
                    'entries_per_page': 30, 'graph_type': "bar"}

#################################
# Current field names
#################################
acc_fieldnames = acc_1_22_fieldnames
ca_fieldnames = ca_1_22_fieldnames
bond_fieldnames = bond_1_22_fieldnames
fund_fieldnames = fund_1_22_fieldnames
xfer_fieldnames = xfer_1_22_fieldnames
loan_fieldnames = loan_1_22_fieldnames
cd_fieldnames = cd_1_22_fieldnames
settings_fieldnames = settings_1_22_fieldnames

#################################
# As of  1.21
#################################
acc_1_21_fieldnames = ['account', 'account_id', 'opening_date', 'account_type', 'update_method', 'note']

ca_1_21_fieldnames = ['account', 'balance', 'rate', 'interest_date', 'frequency', 'note']

bond_1_21_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'issuer', 'call_date', 'call_price',
                        'most_recent_price', 'moodys_rating', 'product_type',
                        's&p_rating', 'most_recent_value', 'next_call_date',
                        'est_yield']
fund_1_21_fieldnames = ['account', 'fund', 'date', 'balance', 'est_roi',
                        'interest_date', 'frequency']

xfer_1_21_fieldnames = ['fromAccount', 'toAccount',
                        'amount', 'frequency', 'note']

loan_1_21_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']

cd_1_21_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

settings_1_21_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']


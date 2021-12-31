#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
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


# todo - the SW version is now kept in the DB
SW_VERSION = "1.22"

# Field widths for display widgets
if platform.system() == 'Linux':
    FW_TINY = 1
    FW_SMALLEST = 6
    FW_SMALL = 10
    FW_MEDSMALL = 14
    FW_MED = 20
    FW_MEDLARGE = 25
    FW_LARGE = 30
    FW_OCC_FIRST_COL = 8   # used in the occurrence window
    FW_OCC_SECOND_COL = 11
else:
    FW_TINY = 1
    FW_SMALLEST = 6
    FW_SMALL = 11
    FW_MEDSMALL = 14
    FW_MED = 20
    FW_MEDLARGE = 25
    FW_LARGE = 30
    FW_OCC_FIRST_COL = 10   # used in the occurrence window
    FW_OCC_SECOND_COL = 14

SMALL_BORDER_WIDTH = 2
BORDER_WIDTH = 4

account_types = ['Checking', 'Brokerage', 'Savings', 'Money Market']
instrument_types = ['ca', 'bond', 'cd', 'loan', 'transfer','setting' ]

# the following should be used in conjunction with
#     datetime.strftime(xxx_FORMAT)
DATE_FORMAT = '%Y-%m-%d'
SHORT_DATE_FORMAT = '%m/%d'

# the following are rec_id definitions for pseudo accounts
INCOME_ACCOUNT_ID = 0
EXPENSE_ACCOUNT_ID = 1
FIRST_REAL_ACCOUNT = 2

####################################################
# Fieldnames for the data file
####################################################

# Note: The xx_new_rec 's are used to create a new record
#       of the associated type. They contain the default
#       values for a new rec

#################################
# As of  1.22
#################################
acc_1_22_fieldnames = ['account', 'account_id', 'opening_date', 'account_type','update_method','note']
#acc_new_rec = {'account': "", 'account_id': "", 'opening_date': "", 'account_type':"",
#              'update_method':"Manual", 'note': ""}

ca_1_22_fieldnames = ['account', 'balance', 'rate', 'interest_date', 'frequency', 'note']
#ca_new_rec = {'account': "", 'balance': 0.0, 'rate': 0.0,
#              'interest_date': "", 'frequency': "monthly", 'note': ""}

bond_1_22_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'issuer', 'call_date', 'call_price',
                        'most_recent_price', 'moodys_rating', 'product_type',
                        's&p_rating', 'most_recent_value', 'next_call_date',
                        'est_yield']
#bond_new_rec = {'account': "", 'bond_price': 0.0, 'quantity': 0,
#                'coupon': 0.0, 'fee': 0.0, 'purchase_date': "", 'maturity_date': "",
#                'frequency': "", 'cusip': "", 'issuer': "",
#                'call_date': "None", 'call_price': 0.0,
#                'most_recent_price': 0.0, 'moodys_rating': "", 'product_type': "",
#                's&p_rating': "", 'most_recent_value': 0.0, 'next_call_date': "None",
#                'est_yield': 0.0}

fund_1_22_fieldnames = ['account', 'fund', 'date', 'balance', 'est_roi',
                        'interest_date', 'frequency']
#fund_new_rec = {'account': "", 'fund': "", 'date': "", 'balance': 0.0,
#                'est_roi': 0.0, 'interest_date': "", 'frequency': ""}

xfer_1_22_fieldnames = ['fromAccount', 'toAccount',
                        'amount', 'frequency', 'inflation', 'note']
#xfer_new_rec = {'fromAccount': "", 'toAccount': "",
#                'amount': 0.0, 'frequency': "", 'inflation':0, 'note': ""}

loan_1_22_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']
#loan_new_rec = {'account': "", 'balance': 0.0,
#                'rate': 0.0, 'orig_date': "", 'payoff_date': "",
#                'frequency': "", 'note': ""}

cd_1_22_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']
#cd_new_rec = {'account': "", 'purchase_price': 0.0, 'quantity': 0,
#              'rate': 0.0, 'purchase_date': "", 'maturity_date': "", 'frequency': "",
#              'cusip': ""}

settings_1_22_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']

#todo - the following is still used
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
acc_1_21_fieldnames = ['account', 'account_id', 'opening_date', 'account_type','update_method','note']

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

#################################
# As of  1.20
#################################
ca_1_20_fieldnames = ['account', 'account_id', 'balance',
                      'rate', 'opening_date', 'interest_date', 'frequency', 'note']

bond_1_20_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'issuer', 'call_date', 'call_price',
                        'most_recent_price', 'moodys_rating', 'product_type',
                        's&p_rating', 'most_recent_value', 'next_call_date',
                        'est_yield']

fund_1_20_fieldnames = ['account', 'fund', 'date', 'balance', 'est_roi',
                        'interest_date', 'frequency']

xfer_1_20_fieldnames = ['fromAccount', 'toAccount',
                        'amount', 'frequency', 'note']

loan_1_20_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']

cd_1_20_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

settings_1_20_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']

default_settings_1_20 = {'tracking_months': 24, 'default_account': "",
                         'bonds_per_page': 30, 'graph_type': "bar"}

#################################
# As of  1.18
#################################
ca_1_18_fieldnames = ['account', 'account_id', 'balance',
                      'rate', 'opening_date', 'interest_date', 'frequency', 'note']

bond_1_18_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'issuer', 'call_date', 'call_price',
                        'most_recent_price', 'moodys_rating', 'product_type',
                        's&p_rating', 'most_recent_value', 'next_call_date',
                        'est_yeild']

fund_1_18_fieldnames = ['account', 'fund', 'date', 'balance', 'est_roi',
                        'interest_date', 'frequency']

xfer_1_18_fieldnames = ['fromAccount', 'toAccount',
                        'amount', 'frequency', 'note']

loan_1_18_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']

cd_1_18_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

settings_1_18_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']

default_settings_1_18 = {'tracking_months': 24, 'default_account': "",
                         'bonds_per_page': 30, 'graph_type': "bar"}

#################################
# As of  1.17 
#################################
ca_1_17_fieldnames = ['account', 'balance',
                      'rate', 'opening_date', 'interest_date', 'frequency', 'note']

bond_1_17_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'call_date', 'call_price']

xfer_1_17_fieldnames = ['fromAccount', 'toAccount',
                        'amount', 'frequency', 'note']

loan_1_17_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']

cd_1_17_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

settings_1_17_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']

#################################
# As of  1.14 
#################################
ca_1_14_fieldnames = ['account', 'balance',
                      'rate', 'opening_date', 'interest_date', 'frequency', 'note']

bond_1_14_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'call_date', 'call_price']

xfer_1_14_fieldnames = ['fromAccount', 'toAccount',
                        'date', 'amount', 'frequency', 'note']

loan_1_14_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']

cd_1_14_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

settings_1_14_fieldnames = ['tracking_months', 'default_account',
                            'bonds_per_page', 'graph_type']

default_settings_1_14 = {'tracking_months': 24, 'default_account': "",
                         'bonds_per_page': 30, 'graph_type': "bar"}

#################################
# As of  1.13 
#################################
ca_1_13_fieldnames = ['account', 'balance',
                      'rate', 'opening_date', 'interest_date', 'frequency', 'note']
bond_1_13_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip', 'call_date', 'call_price']
xfer_1_13_fieldnames = ['fromAccount', 'toAccount',
                        'date', 'amount', 'frequency', 'note']
loan_1_13_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']
cd_1_13_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

#################################
# As of  1.10 
#################################
ca_1_10_fieldnames = ['account', 'balance',
                      'rate', 'opening_date', 'interest_date', 'frequency', 'note']
bond_1_10_fieldnames = ['account', 'bond_price', 'quantity',
                        'coupon', 'fee', 'purchase_date', 'maturity_date',
                        'frequency', 'cusip']
xfer_1_10_fieldnames = ['fromAccount', 'toAccount',
                        'date', 'amount', 'frequency', 'note']
loan_1_10_fieldnames = ['account', 'balance',
                        'rate', 'orig_date', 'payoff_date', 'frequency', 'note']
cd_1_10_fieldnames = ['account', 'purchase_price', 'quantity',
                      'rate', 'purchase_date', 'maturity_date', 'frequency',
                      'cusip']

#################################
# As of  1.7
#################################
ca_1_7_fieldnames = ['account', 'balance', 'quantity',
                     'rate', 'date_1', 'date_2', 'frequency', 'note']
bond_1_7_fieldnames = ['account', 'bond_price', 'quantity',
                       'coupon', 'fee', 'purchase_date', 'maturity_date',
                       'frequency', 'cusip']
xfer_1_7_fieldnames = ['fromAccount', 'toAccount',
                       'date', 'amount', 'frequency', 'note']
loan_1_7_fieldnames = ca_1_7_fieldnames
cd_1_7_fieldnames = ca_1_7_fieldnames

#################################
# 1.6 and before
#################################
ca_1_6_fieldnames = ['account', 'type', 'balance', 'quantity',
                     'rate', 'date_1', 'date_2', 'frequency', 'note']
bond_1_6_fieldnames = ['account', 'type', 'balance', 'quantity',
                       'rate', 'fee', 'date_1', 'date_2', 'frequency', 'note']
xfer_1_6_fieldnames = ['fromAccount', 'type', 'toAccount',
                       'date', 'amount', 'frequency', 'note']
loan_1_6_fieldnames = ca_1_6_fieldnames
cd_1_6_fieldnames = ca_1_6_fieldnames

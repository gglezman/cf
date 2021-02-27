#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains help text and support for the Cash Flow application


# Keep the next two statements in order so ttk widgets override TK widgets
from scrollable_win import ScrollableWin
import data_file_constants as dfc

help_text = {
    "Overview":
"Overview of the Cash Flow Application\n\n\
This application is intended predict future cash flows based on \
the current value of cash accounts and the ownership of funds, loans, CDs \
and Bonds.\n\n\
The cash flow results are viewable in either\n\
 - Text Format or\n\
 - Graph Format\n\n\
Cash flows are presented from the current date forward for a provisionable \
number of months (see Settings/Tracking Months), to the end date. \
Past cash flows are not tracked, only forward cash flows.\n\n\
Note: If the opening date of a cash account is prior to the current date, \
cash flow will be presented, in text mode, from the account opening date through the end date. However, graph mode is restricted to begin at the current date.\
\n\n\
Note: Past bond, loan and CD information is held for historical purposes and can be viewed from the Edit Menu",
    "Usage":
"Using The Cash Flow Application\n\n"
"The first step in using this application is to create a data file to store\n\
you data. A data file is created using the File/New Data File selection.\n\n\
Next you need to create at least one account. Accounts are created using the\n\
Edit/Account menu. You can add a checking account,savings, brokerage, etc.",
    "File":
"File Menu Help\n\n\
Open Data File    Use this option to open an existing data file. The data\n\
                  must have been previously created by this application.\n\n\
                  Opening a second data file replaces all information\n\
                  previously read in.\n\n\
New Data File     Create a new data file. The data file is used to store all\n\
                  user information and settings.\n\n\
                  Creating a new data file replaces all information\n\
                  previously read in.\n\n\
Save              There is no save operation available to the user. All\n\
                  required file save operations are performed automatically.\n\n\
                  Note that some screens have an 'Update' button. Depressing\n\
                  button is required to save the changes applied in that\n\
                  screen.\n\n\
Note: Data Files have an associated version. If an upgrade is required\n\
      it will be done automatically.",
    "Editing Settings":
"Settings Help\n\n\
Tracking Months:  The number of months cash flows will be tracked \n\
                  from the current date.\n\
                  A pull down is available with common choices but any\n\
                  number of months could be entered.\n",
    "Editing Accounts":
"Editing the Accounts List\n\n\
In this window you add or edit account information. An account is something\n\
you open with a bank, a brokerage firm or on-line. The account may be\n\
simply a checking or savings account or it may be a brokerage account.\n\
If its a brokerage account it may contain many additionaal finacial instruments\n\
such as stock bonds and mutual funds. They will be entered elswehere.\n\n\
This window is used to enter the top level account information only.\n\n\
Account Name:  The account nickname. In almost all cases, the nickname\n\
               is the used to refer to the account.\n\n\
Account ID:    The ID the bank or brokerage firm uses to identify the\n\
               account. This is useful when importing data from a bank\n\
               or brokerage account.\n\n\
Account Type:  This is self explanatory.\n\n\
Update Method  Account information may be updated via download from the\n\
               bank/firm or it may be provided manually. If account download\n\
               is supported, make the appropriate selection from the\n\
               pull down menu.\n\n\
Note: Some Account Types, such as checking and savings, are simple cash\n\
accounts. These accounts will be automatically placed in the cash accounts list.\n\
For broakerage accounts you will have to enter the sweep account manually since\n\
there is additioan information required.\n",
    "Editing Cash Accounts":
"Editing the Cash Accounts List\n\n\
Cash accounts hold cash. They can be a bank account, a checking account or\n\
a brokerage account. For brokerage accounts, this is the sweep account.\n\n\
Fields in the Cash Account Edit Window:\n\n\
Account Name:  The account nickname. In almost all cases, the nickname\n\
               is the used to refer to the account.\n\n\
Account ID:    The ID the bank or brokerage house uses to identify the\n\
               account. This is useful when importing data from a bank\n\
               or brokerage account.\n\n\
Account Type:  This is self explanatory.\n\n\
Update Method  Account information may be updated via download from the\n\
               bank/firm or it may be provided manually. If account download\n\
               is supported, make the appropriate selection from the\n\
               pull down menu.\n\n\
Opening Date:  Opening date is the date the account contained the amount\n\
               specified in the 'Balance' column. Typically, the Opening Date\n\
               is advanced each time the balance is updated\n\n\
Balance:       Cash funds in the account as of the 'Opening Date'\n\n\
Rate:          Current interest rate paid by the account\n\n\
Interest Date: Date the interest is applied\n\n\
Compound:      How frequently the interest is applied\n\
",
    "Editing The CD List":
    "CD",
    "Editing The Bond List":
"Editing the Bonds List\n\n\
The bond list is a list of all bonds entered into the application. The bond\n\
list may be manually edited or data may be imported from the brokerage\n\
firm.\n\n\
The Bond List Window Layout:\n\n\
The bond list window is is divided into three frames: the bond filters at\n\
the top of the window, the bond list in the center of the window and the\n\
control and status indicators at the bottom.\n\n\
Filtering The Bond List:\n\n\
When the bond list is first opened, all bonds entered in the application are\n\
displayed. The top portion of the window contains several filters that may\n\
be applied to the bond list. The filters are as follows:\n\n\
  Account:     The account pull-down can be used limit the bonds displayed\n\
               to those purchased from a single account or all accounts.\n\
  Bond Status: The Bond Status pull-down can be used to limit the bonds\n\
               displayed as follows:\n\
                   all:     Bonds of all status\n\
                   active:  Only show bonds still active. A bond is no longer\n\
                            active if either it has matured or it has been\n\
                            called.\n\
                   closed:  Only show bonds no longer active.\n\
                   matured: Only show bonds whose maturity date has pasted.\n\
                   called:  Only show bonds that were called.\n\
\n\
The Status and Control Frame:\n\n\
The status section displays page information. If the full list of bonds can\n\
not be displayed in the window, page information is shown in the lower left\n\
of the frame.  The \">>\" and \">>\" buttons are used to page forward and\n\
backward respectively.\n\n\
The control frame contains the following buttons:\n\n\
  Import Bonds: Import bond information from a brokerage house.\n\n\
  New:          Manually enter a new bond.\n\n\
  Update:       Update the database with the changes made in the Bond List\n\
                Window. That is, if you make any changes to the entries in\n\
                the Bond List Window, you must Update. Failure to do so\n\
                results in all changes being lost.\n\n\
  Cancel:       Discard all changes made in the Bond List Window\n\
\n\
Fields in the Bond List Frame:\n\n\
The following fields can be manually edited:\n\n\
  Account Name:    Nickname of account from which the bond was purchased.\n\
                   An account from the pull-down may be selected. All accounts\n\
                   specified in the Cash Accounts window will appear in this\n\
                   list.\n\
  Settlement Date: Settlement date per the brokerage house.\n\n\
  Price:           Price paid for the bond. Per industry standard, $100\n\
                   represents the par value of $1000 bond.\n\n\
  Quantity:        Number of bonds purchased.\n\n\
  Coupon:          Stated coupon for the bond.\n\n\
  Fees:            Fees charged by the brokerage house for the bond purchase.\n\n\
  Maturity Date:   Maturity date stated on the bond.\n\n\
  Pay Frequency:   Frequency at which the bond pays interests.\n\n\
  CUSIP:           Bond identifier used by the brokerage house.\n\n\
  Issuer:          Stated issuer of the bond.\n\n\
",
    "Editing Loans":
"Editing the Loans list",
    "Editing The Transfers List":
"Transfers",
    "Editing Scheduled Transfers":
"Transfers",
    "Editing Funds":
"Funds List",
    "Accounts":
"Account Pull Down Help",
    "TextGraph":
"Text / Graph Mode Selection Help",
    "DateRange":
"Graph Date Range Help\n\n\
In graph mode, a graph of cash flows is presented for the date range \
defined by the 'Date Range' button. The default values for the Date Range \
are: the current date through the period defined by the Tracking Months. \
For example, if the current date is Jan 1, 2018 and Tracking Months is provisioned for 24 months, the start date is Jan 1, 2018 and the end date is \
Jan 1, 2020.\n\n\
The graphs presentation can get very 'busy', especially if the Tracking Months \
are provisioned to a large number of months. The amount of data shown on the \
graph can be reduced via the Date Range button.\n\n\
The start date can neither precede the current date nor be equal to or follow the end date. The end date must be after the start date and can not exceed the end period defined by the Tracking Months. ",
    "About":
"\nVersion Information: {} 03/10/19\n\n\
Author: Gregory Glezman".format(dfc.SW_VERSION)
}


class Help:
    def __init__(self, topic, master=None):
        """Open the Help window"""
        
        if topic in help_text:
            ScrollableWin("Help - " + topic, help_text[topic], master)

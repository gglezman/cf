#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to present a GUI to the cash flow report.
#
#  To Do
#   . datepicker widget - if month has 6 rows, the botom buttons are cut off
#   . scheduled transfers, date ordering (click on a date) doesn't work properly
#   . Help - review help text
#   . Architectural
#      - I have added funds to the edit menu, the file read and file write
#      - how to move money from funds to CA - sell / buy
#         option 1- sell action on fund: cash goes to sweep account
#              Issue - the fund menu to not support fund sales (wrong columns)
#                    solution 1 - add a sell menu item / record same as transfer records
#                               - user can schedule a sale and/or purchase
#                               - this creates two unique places where events are schedule
#                     solution 2 - add a sell record and change 'scheduled transfers'
#                                  to 'scheduled actions'
#                                - net result is one place where all events are
#                                  recorded and I can fix the date sorting
#         option 2 - manually adjust balance in funds and CA
#              Issue - this can't be planned for future events hence you can't
#                      prdedict / analyze
#                     - this option is pretty much useless
#  *****  option 3 - do I allow transfers from fund to CA and forget about sales
#                     solution 1 - I would have to beef up the transfer page
#                                - will required modifications to the transfer record
#                                - will require mods to the transfer menu
#        related question : should Adding a fund debit the CA
#                         : should Adding a bond debit the CA
#                         : Bond sale already credits the CA - YES
#                         : should fund sale credit the CA - YES
#                         : if bond data is imported, do we import the CA amount as well?
#                              should this possibly affect the CA?
#                         : if fund data iss imported, do we import CA amount as well?
#                              should this possibly affec the CA?
#     - scheduled transfers - date sort - I show the next occurrence in the transfer window,
#                                      but it looks like I sort based on the first ocurrence?
#   . General
#     - File / Validate Data File
#       . this would be nice to have, at least a framework
#       . this could be run on all start-ups
#   . Import Bonds from Fid
#     - determine how the 'add'will work
#       - AccountEdit is the best candidate for update
#          - should I let them pile up, throttle or auto add all?
#          - possibly create a list with Add/Discard buttons in-line
#          - consider highlighting "unknown info"
#   . Funds
#     - add record to data file
#       - upgrade, data_file_constants
#   . Reports menu item
#     - Cash flow on all instruments
#     - total interest per year / month
#     - bond rating characteristics
#   . Debit order in register
#     - Bond purchases would look better if the order was Purchase, AccInt, fee
#       This could be accomplished by using the time trick I use for credit
#     - At the same time, change cf.bond_cash_flow to put type instead of
#       note.  The receiver can do whatever they want based on the type.
#       The type would be used to force the order of entries in the register
#   . Logging
#     - must be global (static methods on a class)
#     - provision level via settings
#   . Occurrences
#     - eg quarterly, end after :1, too many "-" in string
#     - fix sorting for occurrences (bonds)
#     - issues
#       . Windows only - open once occurrence; change date/OK;
#           resulting window is too small - can't see buttons !!!
# ****** . Multi-column repeat (check) lastDate / regularity - applies to new
#     - maybe apply to Cash Accounts, CDs, Bonds, Loans (data file upgrade)
#   . Edit menu
#     - settings
#       . initial location on screen,
#       . initial size
#       . debug level
#     - transfers
#       . Amount - make it a button and add an inflation schedule
#   . Consider generalizing InstrumentType.  Will be easier to add new types
#       - maybe do this when I add Treasuries
# ! . Weekly has got to be made to work
#       - How about a point graph
# XXX. when account goes negative, don't subtract negative interest
#   . If you don't hit update it is not written to disk
# ! . ActionsOnInstrument
#     - Bond
#       - analysis - ROI, YTM, Duration
#       - consider fields in the column_descriptor that will not
#         be shown in the NewInstrument window - eg bond/call_price
#       - Cleanup - "delete Bond Records" => Mark Bond for deletion
#      - General
#       - Cleanup - color is currently gray(Windows version).
#                     Make it same as background
# ! . AccountEdit / ActionsOnInstruments / New Instruments
#     - All highlighting any data which has changed
#     - Bonds
#       -  statusBar - number of instruments (eg number of bonds)
#       -  add a tooltip over Call
#       -  New Bond - "call" still appears
#     - CDs
#       - cash flow details not available
# ! . In Graph mode,
#       - date change plus update does not always update the graph
#       - what are the best dates? end of month, end of year?
#       - what date to start with ??
#       - dates and amounts are way to busy. Left axis and limit dates
# !!!    - each column should clearly show
#            . cash
#            . bond interest
#            . bond principal
#            . cd interest
#            . cd principal
#            . Treasure interest
#            . Treasure Principal
# !!!    - hovering over subsection should provide details
#   . Add support for US treasuries and Agency Bonds
#       - US treasuries and agency bonds are quoted in 32nds.  That is
#         94:16 means 9450 is the bond price
#   Bugs
#   Scenario I:
#     Open bond list
#     Mark a bond deleted   - shows as RED
#     Add a new bond / Add
#     Problem - when account list is updated, deleted bond is no longer RED
#
#   Windows Only
#    1. When ActionsOnInstrument is open and the AccountEdit window
#       is minimized, ActionsOnInstrument window gets buried
#    2. Style changes not working for item delete
# !! 3. On the Bond page, ActionsOnInstrument, Bond Call selection
#       BondCall window recedes behind all windows!!
#  !3a Error windows for the bond call popup appear to be associated with the
#      main window. When I click on the error window the main window
#      comes to the top
# !!3b. Most pop-ups immediately hide behind the top window
#       - Bond Cash Flow Details hidesbehind the bond window
#       - Bond Call hides behind the bond window
#    4. Edit Cash accounts - Opening Date field is to narrow
#    5. AccountEdit - Deleted instrument does not show properly
#    6. sceduled transfers / left click on date to bring up change window
#        the window is to small, buttons on the bottom are hidden
# Keep the next two statements in order so ttk widgets override TK widgets
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime, date
from tkinter import messagebox
from functools import partial
from help import Help
import data_file_constants as dfc
from settings_win import SettingsWin
from account_edit_win import AccountEditWin
from import_win import ImportAccountsWin
from import_win import ImportBondDetailsWin
from import_support import ImportMethodsSupported
import gui as gui
import file_manager as fm
import cf_styles
import utils as local_util
# todo - the following line should go away
from import_support import process_fidelity_account_download


class GraphFrame:
    """This is the frame that will contain a graphical 
    representation of the data. We'll need the master window 
    to properly place the drawing canvas
    """

    def __init__(self, parent, master, w=400, h=300):
        self.parent = parent
        self.width = w
        self.height = h
        self.pop_up = None
        self.accnt_data = []
        self.pillar_edges = None

        self.frame = local_util.add_frame(master)

        self.canvas = tk.Canvas(self.frame, width=w, height=h)
        # Expand in both directions taking all available space
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.bind("<Configure>", self.configure)
        self.canvas.bind("<Motion>", self.motion)

    def graph_data(self, accnt_data):
        """Graph the provided account data. Each entry in the list 
        has datetime and amount component. """

        self.accnt_data = accnt_data
        self.pillar_edges = []  # (xStart, xEnd, Y)

        if not accnt_data:
            return

        axis_pad = 15
        headroom_pad = 15
        tick_mark_height = 5
        max_pillar_width = 56
        max_pillar_spacing = 42
        pillar_width_proportion = 4 / 7
        pillar_spacing_proportion = 3 / 7

        width = self.width - axis_pad  # usable area on
        height = self.height - axis_pad  # the canvas

        # Number and width of pillars
        num_pillars = len(accnt_data)
        if num_pillars == 0:
            # No data yet.  Fake the data to avoid bad things
            num_pillars = 1
        pillar_width = width / num_pillars * pillar_width_proportion
        pillar_space = width / num_pillars * pillar_spacing_proportion

        # prevent really fat pillars - shrink and center the pillars
        if pillar_width > max_pillar_width:
            pillar_width = max_pillar_width
            pillar_space = max_pillar_spacing
            total_used = num_pillars * (pillar_space + pillar_width)
            center_pad = (width - total_used) / 2
        else:
            center_pad = 0

        # Height of pillars
        tallest = 1  # set to 1 to avoid div-by-zero on new data file
        for entry in accnt_data:
            if entry[1] > tallest:
                tallest = entry[1]
        scale = (height - headroom_pad) / tallest

        # axis
        # 0,0 is upper left
        self.canvas.delete("all")
        y_axis = self.canvas.create_line(axis_pad,
                                         height,
                                         axis_pad,
                                         axis_pad)
        x_axis = self.canvas.create_line(axis_pad,
                                         height,
                                         width,
                                         height)
        # tick mark x coordinate
        self.pillar_edges.clear()
        tm = center_pad + axis_pad + pillar_space / 2 + pillar_width / 2
        for i in range(num_pillars):
            # self.canvas.create_line( tm, height, tm, height+tick_mark_height)
            # top left, bottom right of rectangle
            self.canvas.create_rectangle(
                    tm - pillar_width / 2,
                    height - (accnt_data[i][1] * scale),
                    tm + pillar_width / 2,
                    height,
                    fill='blue')
            # label the height of the pillar
            self.canvas.create_text(tm, height - (accnt_data[i][1] * scale) - 5,
                                    text="{:.0f}".format(accnt_data[i][1]))
            if self.parent.get_granularity() == "Weekly":
                date = "{}/{}".format(accnt_data[i][0].month,
                                      accnt_data[i][0].day)
            elif self.parent.get_granularity() == "Monthly":
                date = "{}/{}/{}".format(accnt_data[i][0].month,
                                         accnt_data[i][0].day,
                                         accnt_data[i][0].year - 2000)
            else:
                date = "{}/{}/{}".format(accnt_data[i][0].month,
                                         accnt_data[i][0].day,
                                         accnt_data[i][0].year)
            self.canvas.create_text(tm, self.height - (axis_pad / 2), text=date)
            # TODO
            # print("beg {} tick {} end {}".format(
            #    tm - pillar_width/2,
            #    tm,
            #    tm + pillar_width/2) )
            # keep track of all objects on the screen
            self.pillar_edges.append(
                    (tm - pillar_width / 2,  # start X
                     tm + pillar_width / 2,  # end x
                     height - (accnt_data[i][1] * scale),  # top Y
                     accnt_data[i][1]))  # Value
            tm = tm + pillar_space + pillar_width
        for entry in self.pillar_edges:
            pass
            # print("start {} end {} top y {} value: {}".format(
            #                     entry[0], entry[1], entry[2], entry[3]) )

    def configure(self, event):
        self.width = event.width
        self.height = event.height

        self.graph_data(self.accnt_data)

    def motion(self, event):
        """This method destroys then repaints the text on the canvas
        for every cursor movement event if its on the same pillar. The text 
        object has a string tag.  I could use the starting x as a tag and
        only delete/create_text object if the tag differs"""

        # print("X {}, Y {}".format(event.x, event.y) )
        # Check if any data is currently displayed
        if len(self.pillar_edges) == 0:
            return

        over_pillar = False
        entry = (0, 0, 0, 0)
        for entry in self.pillar_edges:
            if (entry[0] <= event.x <= entry[1] and
                    entry[2] <= event.y < (self.height + 10)):
                # fix me above - make the 10 a class constant
                # print (entry[3])
                over_pillar = True
                break
        if over_pillar:
            if self.pop_up:
                self.canvas.delete(self.pop_up)
            self.pop_up = self.canvas.create_text(
                    entry[0], entry[2] - 10, text=entry[3], fill='RED')
        else:
            if self.pop_up:
                # print("We  are clear")
                self.canvas.delete(self.pop_up)

    def close_up(self):
        """Destroy the < graph frame (switching to text display mode)"""
        self.frame.destroy()


class MyMenuBar:
    """Every good app should contain a menu bar."""

    def __init__(self, master, parent):
        self.parent = parent  # Gui
        self.master = master  # Tk.root
        self.data_file_name = ""
        self.edit_window_open = {  # use an instrument type to index this dictionary
            'account': 0, 'ca':0, 'cd': 0, 'loan': 0, 'bond': 0,
            'fund': 0, 'transfer': 0, 'setting': 0}
        self.import_account_win_open = False
        self.import_bond_details_win_open = False

        my_menu = tk.Menu(master)
        master.config(menu=my_menu)
        self.my_menu = my_menu

        ########################################################
        # File Menu
        ########################################################
        self.file_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Database File",
                                   command=self.open_database_file)
        self.file_menu.add_command(label="New Database File",
                                   command=self.new_database_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Validate Database File!",
                                   command=self.validate_database_file)
        self.file_menu.add_command(label="Dump Current Database",
                                   command=self.dump_db)
        self.file_menu.add_separator()

        # todo - create an exit function which will close the DB then quit
        #      - if I x out the main gui, call the new exit function
        self.file_menu.add_command(label="Exit", command=quit)

        ########################################################
        # Edit Menu - disable until a file is opened
        ########################################################
        self.edit_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="Edit", menu=self.edit_menu, state='disabled')
        self.edit_menu.add_command(label="Settings",
                                   command=self.edit_settings)
        self.edit_menu.add_command(label="Accounts",
                                   command=self.edit_accounts)
        self.edit_menu.add_command(label="Cash Accounts",
                                   command=self.edit_cash_accounts)
        self.edit_menu.add_command(label="CDs",
                                   command=self.edit_cds)
        self.edit_menu.add_command(label="Bonds",
                                   command=self.edit_bonds)
        self.edit_menu.add_command(label="Funds",
                                   command=self.edit_funds)
        self.edit_menu.add_command(label="Loans",
                                   command=self.edit_loans)
        self.edit_menu.add_command(label="Scheduled Transfers",
                                   command=self.edit_transfers)

        ########################################################
        # Import Menu - disable until a file is opened
        ########################################################
        self.import_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="Import",
                            menu=self.import_menu, state='disabled')
        self.import_menu.add_command(label="Accounts",
                                     command=self.import_accounts)
        self.import_menu.add_command(label="Bond Details",
                                     command=self.import_bonds)

        ########################################################
        # Reports Menu - disable until a file is opened
        ########################################################
        self.report_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="Reports",
                            menu=self.report_menu, state='disabled')
        self.report_menu.add_command(label="Interest!",
                                     command=self.report_interest)

        ########################################################
        # Help Menu
        ########################################################
        self.help_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Overview",
                                   command=partial(
                                           Help,
                                           "Overview",
                                           self.master))
        self.help_menu.add_command(label="Using This Application",
                                   command=partial(
                                           Help,
                                           "Usage",
                                           self.master))
        self.help_menu.add_command(label="File Menu",
                                   command=partial(
                                           Help,
                                           "File",
                                           self.master))
        self.edit_menu = tk.Menu(self.help_menu)
        self.help_menu.add_cascade(label="Edit Menu", menu=self.edit_menu)
        self.edit_menu.add_command(label="Settings!",
                                   command=partial(
                                           Help,
                                           "Editing Settings",
                                           self.master))
        self.edit_menu.add_command(label="Accounts",
                                   command=partial(
                                           Help,
                                           "Editing Accounts",
                                           self.master))
        self.edit_menu.add_command(label="Cash Accounts",
                                   command=partial(
                                           Help,
                                           "Editing Cash Accounts",
                                           self.master))
        self.edit_menu.add_command(label="CDs!",
                                   command=partial(
                                           Help,
                                           "Editing The CD List",
                                           self.master))
        self.edit_menu.add_command(label="Bonds",
                                   command=partial(
                                           Help,
                                           "Editing The Bond List",
                                           self.master))
        self.edit_menu.add_command(label="Funds!",
                                   command=partial(
                                           Help,
                                           "Editing Funds",
                                           self.master))
        self.edit_menu.add_command(label="Loans!",
                                   command=partial(
                                           Help,
                                           "Editing Loans",
                                           self.master))
        self.edit_menu.add_command(label="Transfers!",
                                   command=partial(
                                           Help,
                                           "Editing Scheduled Transfers",
                                           self.master))
        self.help_menu.add_command(label="Imports!",
                                   command=partial(
                                           Help,
                                           "Imports",
                                           self.master))
        self.help_menu.add_command(label="Account Pull Down!",
                                   command=partial(
                                           Help,
                                           "Accounts",
                                           self.master))
        self.help_menu.add_command(label="Text/Graph!",
                                   command=partial(
                                           Help,
                                           "TextGraph",
                                           self.master))
        self.help_menu.add_command(label="Date Range",
                                   command=partial(
                                           Help,
                                           "DateRange",
                                           self.master))
        self.help_menu.add_command(label="About",
                                   command=partial(
                                           Help,
                                           "About",
                                           self.master))

    def open_database_file(self):
        self.parent.init_storage()
        filename = self.parent.fm.open_database_file()
        if filename:
            self.parent.restart()
            self.parent.mode_change("Graph")
            self.parent.set_datafile(filename)
            self.enable_full_menu_bar()

    def new_database_file(self):
        # FileManager will create the new data file and write it to disk

        # reset the ledger
        self.parent.init_storage()
        filename = self.parent.fm.new_data_file()
        if filename:
            self.parent.restart()
            self.parent.mode_change("Graph")
            self.parent.set_datafile(filename)
            # enable the 'Edit' entry on the menu bar
            self.enable_full_menu_bar()

    def enable_full_menu_bar(self):
        self.my_menu.entryconfig("Edit", state='normal')
        self.my_menu.entryconfig("Import", state='normal')
        self.my_menu.entryconfig("Reports", state='normal')

    @staticmethod
    def validate_database_file():
        messagebox.showerror("Data Validation",
                             "This feature is not yet in place")

    def dump_db(self):
        filename = self.parent.fm.dump_db()

    @staticmethod
    def report_interest():
        messagebox.showerror("Interest Report",
                             "This feature is not yet in place")

    def edit_accounts(self):
        if self.edit_window_open['account'] == 0:
            columns = [
                {"heading": "Account Name", "key": "account_name", "width": dfc.FW_MED,
                 "type": "entry", "content": "text"},
                {"heading": "Account Number", "key": "account_number", "width": dfc.FW_MEDSMALL,
                 "type": "entry", "content": "text"},
                {"heading": "Account Type", "key": "account_type", "width": dfc.FW_MEDSMALL,
                 "type": "combo", "content": dfc.account_types},
                {"heading": "Opening Date", "key": "opening_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Update Method", "key": "update_method", "width": dfc.FW_MEDSMALL,
                 "type": "combo", "content": ImportMethodsSupported},
                ]

            self.edit_window_open['account'] = 1
            AccountEditWin(self.parent, 'Accounts', columns,
                           self.parent.get_real_accounts('account'), 'account',
                           'account_name', 'account_number',
                           validate_func=self.validate_account_entry)

    def edit_cash_accounts(self):
        if self.edit_window_open['ca'] == 0:
            compound1 = ['monthly', 'quarterly', 'annual', 'semi-annual']
            accnt_set = self.parent.get_sorted_accounts_list()

            columns = [
                {"heading": "Account Name", "key": "account_name", "width": dfc.FW_MED,
                 "type": "text", "content": "ThinLeft.TLabel"},
                {"heading": "Balance", "key": "balance", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "dollars"},
                {"heading": "Rate", "key": "rate", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "rate"},
                {"heading": "Interest Date", "key": "interest_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Interest\nFrequency", "key": "frequency", "width": dfc.FW_SMALL,
                 "type": "combo", "content": compound1},
            ]

            self.edit_window_open['ca'] = 1
            AccountEditWin(self.parent, 'Cash Accounts', columns,
                           self.parent.get_real_accounts('ca'), 'ca',
                           'account_name', 'balance',
                           validate_func=self.validate_ca_entry)

    def edit_cds(self):
        if self.edit_window_open['cd'] == 0:
            compound0 = ['monthly', 'quarterly', 'annual', 'semi-annual', 'once']
            accnt_set = self.parent.get_sorted_accounts_list()

            columns = [
                {"heading": "Account Name", "key": "account_name", "width": dfc.FW_MED,
                 "type": "combo", "content": accnt_set},
                {"heading": "Purchase\n Date", "key": "purchase_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Cost", "key": "purchase_price", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "dollars"},
                {"heading": "Quantity", "key": "quantity", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "quantity"},
                {"heading": "Rate", "key": "rate", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "rate"},
                {"heading": "Maturity Date", "key": "maturity_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Compound", "key": "frequency", "width": dfc.FW_SMALL,
                 "type": "combo", "content": compound0},
                {"heading": "CUSIP", "key": "cusip", "width": dfc.FW_MED,
                 "type": "entry", "content": "cusip"}]

            self.edit_window_open['cd'] = 1
            AccountEditWin(self.parent, 'Certificates of Deposit', columns,
                           self.parent.get_from_db('cd'), 'cd', 'account_name', 'maturity_date',
                           validate_func=self.validate_cd_entry)

    def edit_loans(self):
        if self.edit_window_open['loan'] == 0:
            compound0 = ['monthly', 'quarterly', 'annual', 'semi-annual', 'once']
            accnt_set = self.parent.get_sorted_accounts_list()

            columns = [
                {"heading": "Account Name", "key": "account_name", "width": dfc.FW_MED,
                 "type": "combo", "content": accnt_set},
                {"heading": "Origination\n Date", "key": "orig_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Balance", "key": "balance", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "dollars"},
                {"heading": "Rate", "key": "rate", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "rate"},
                {"heading": "Payoff Date", "key": "payoff_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Compound", "key": "frequency", "width": dfc.FW_SMALL,
                 "type": "combo", "content": compound0},
                {"heading": "Notes", "key": "note", "width": dfc.FW_MED,
                 "type": "entry", "content": "text"}]
            self.edit_window_open['loan'] = 1
            AccountEditWin(self.parent, 'Loans', columns, self.parent.get_from_db('loan'),
                           'loan', 'account_name', 'payoff_date',
                           validate_func=self.validate_loan_entry)

    def edit_bonds(self):
        if self.edit_window_open['bond'] == 0:
            compound1 = ['monthly', 'quarterly', 'annual', 'semi-annual']
            accnt_set = self.parent.get_sorted_accounts_list()
            expanded_accnt_set = ['All']
            expanded_accnt_set.extend(accnt_set)  # All + account set

            columns = [
                {"heading": "Account Name", "key": "account_name", "width": dfc.FW_MED,
                 "type": "combo", "content": accnt_set},
                {"heading": "Settlement\nDate", "key": "purchase_date",
                 "width": dfc.FW_SMALL, "type": "date", "content": "standard"},
                {"heading": "Price", "key": "bond_price", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "price"},
                {"heading": "Quantity", "key": "quantity", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "quantity"},
                {"heading": "Coupon", "key": "coupon", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "rate"},
                {"heading": "Fees", "key": "fee", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "dollars"},
                {"heading": "Maturity\nDate", "key": "maturity_date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "Coupon\nFrequency", "key": "frequency", "width": dfc.FW_SMALL,
                 "type": "combo", "content": compound1},
                {"heading": "CUSIP", "key": "cusip", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "cusip"},
                {"heading": "Issuer", "key": "issuer", "width": dfc.FW_MED,
                 "type": "entry", "content": "text"},
                {"heading": "Call", "key": "call_price", "width": dfc.FW_TINY,
                 "type": "checkbutton", "content": "call"}]
            filters = [
                {'type': 'combo', 'width': dfc.FW_MEDSMALL, 'label': 'Account Name:',
                 'set': expanded_accnt_set, 'function': self.account_filter},
                {'type': 'combo', 'width': dfc.FW_SMALLEST,  'label': 'Bond Status:',
                 'set': ['All', 'active', 'closed', 'matured', 'called'],
                 'function': self.bond_status_filter}]

            self.edit_window_open['bond'] = 1
            AccountEditWin(self.parent, 'Bonds', columns, self.parent.get_from_db('bond'),
                           'bond', 'account_name', 'maturity_date', filters=filters,
                           validate_func=self.validate_bond_entry)

    def edit_funds(self):
        if self.edit_window_open['fund'] == 0:
            compound1 = ['monthly', 'quarterly', 'annual', 'semi-annual']
            accnt_set = self.parent.get_sorted_accounts_list()
            expanded_accnt_set = ['All']
            expanded_accnt_set.extend(accnt_set)  # All + account set

            columns = [
                {"heading": "Account Name", "key": "account_name", "width": dfc.FW_MED,
                 "type": "combo", "content": accnt_set},
                {"heading": "Fund Name", "key": "symbol", "width": dfc.FW_MED,
                 "type": "entry", "content": "text"},
                {"heading": "Date", "key": "date", "width": dfc.FW_SMALL,
                 "type": "date", "content": "standard"},
                {"heading": "balance", "key": "balance", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "dollars"},
                {"heading": "Return\nRate", "key": "est_roi", "width": dfc.FW_SMALLEST,
                 "type": "entry", "content": "rate"},
                #{"heading": "Interest\nDate", "key": "interest_date", "width": dfc.FW_SMALL,
                # "type": "date", "content": "standard"},
                #{"heading": "Compound", "key": "frequency", "width": dfc.FW_SMALL,
                # "type": "combo", "content": compound1}
                ]
            filters = [
                {'type': 'combo', 'width': dfc.FW_MEDSMALL, 'label': 'Account Name:',
                 'set': expanded_accnt_set, 'function': self.account_filter}]

            self.edit_window_open['fund'] = 1
            AccountEditWin(self.parent, 'Funds', columns, self.parent.get_from_db('fund'),
                           'fund', 'account_name', 'interest_date',
                           filters=filters,
                           validate_func=self.validate_fund_entry)

    def edit_transfers(self):
        if self.edit_window_open['transfer'] == 0:
            accnt_set1 = self.parent.get_sorted_accounts_list(income=True)
            #accnt_set1.append('income')
            accnt_set2 = self.parent.get_sorted_accounts_list(expense=True)
            #accnt_set2.append('expense')

            columns = [
                {"heading": "From Account", "key": "from_account_name", "width": dfc.FW_MED,
                 "type": "combo", "content": accnt_set1},
                {"heading": "To Account", "key": "to_account_name", "width": dfc.FW_MED,
                 "type": "combo", "content": accnt_set2},
                {"heading": "Date", "key": "frequency", "width": dfc.FW_SMALL,
                 "type": "date", "content": "latest"},
                {"heading": "Amount", "key": "amount", "width": dfc.FW_SMALL,
                 "type": "entry", "content": "dollars"},
                {"heading": "Occurrences", "key": "frequency", "width": dfc.FW_MEDSMALL,
                 "type": "date", "content": "regularity"},
                {"heading": "Inflation", "key":"inflation", "width":dfc.FW_SMALL,
                "type": "entry", "content":"rate"},
                {"heading": "", "key": "", "width": dfc.FW_TINY,
                 "type": "filler", "content": ""},
                {"heading": "Notes", "key": "note", "width": dfc.FW_MEDLARGE,
                 "type": "entry", "content": "text"}]
            filters = []
            expanded_accnt_set1 = ['All']
            expanded_accnt_set1.extend(accnt_set1)  # All + account set
            filters.append({'type': 'combo',
                            'width': dfc.FW_MEDSMALL,
                            'label': 'FromAccount:',
                            'set': expanded_accnt_set1,
                            'function': self.from_account_filter})
            expanded_accnt_set2 = ['All']
            expanded_accnt_set2.extend(accnt_set2)  # All + account set
            filters.append({'type': 'combo',
                            'width': dfc.FW_MEDSMALL,
                            'label': 'to_account:',
                            'set': expanded_accnt_set2,
                            'function': self.to_account_filter})

            self.edit_window_open['transfer'] = 1
            AccountEditWin(self.parent, 'Scheduled Transfers', columns,
                           self.parent.get_from_db('transfer'), 'transfer',
                           'from_account_name', 'to_account_name',  # TODO - how to sort date
                           filters=filters,
                           validate_func=self.validate_xfer_entry)

    def edit_settings(self):
        if self.edit_window_open['setting'] == 0:
            self.edit_window_open['setting'] = 1
            SettingsWin(self.parent, self.master, self)

    def edit_window_closed(self, instrument_type, new_accounts=[]):
        # Mark the window closed
        if instrument_type in self.edit_window_open:
            self.edit_window_open[instrument_type] = 0

        # Todo - this are needs work. gjg  It needs to be moved into import_support
        # this is the trigger point for account init

        fm = self.parent.get_file_manager()

        for account in new_accounts:
            update_method = self.parent.get_account_update_method(account['account_id'])
            if update_method != "Manual":
                response = tk.messagebox.askquestion(
                    "New Account Initialization",
                    "You have just created a new account "+
                    "named \'{}\', ".format(account['account'])+
                    "account ID: \'{}\'. ".format(account['account_id'])+
                    "Would you like to initialize it? "+
                    "(You will need a file to import "+
                    "based on the Import Method you specified.)")
                if response == "yes":
                    if update_method == "Fidelity Export":
                        file_content = fm.open_account_import(process_fidelity_account_download,
                                                              account['account_id'])
                        for rec in file_content:
                            print(rec)
                else:
                    print("He answered No")


    @staticmethod
    def account_filter(accnt, rec):
        """Filter a bond based on the given account criteria """

        if accnt == 'All' or accnt == rec['account_name']:
            return True
        else:
            return False

    @staticmethod
    def to_account_filter(accnt, rec):
        """Filter a bond based on the given account criteria """

        if accnt == 'All' or accnt == rec['to_account_name']:
            return True
        else:
            return False

    @staticmethod
    def from_account_filter(accnt, rec):
        """Filter a bond based on the given account criteria """

        if accnt == 'All' or accnt == rec['from_account_name']:
            return True
        else:
            return False

    @staticmethod
    def bond_status_filter(status, rec):
        """Filter a bond based on the given bond criteria.

        We have defined several bond selection criteria to make 
        reviewing bonds easier. This filter will check the bond
        against the given predefined criteria and return True if the
        bond matches the criteria, False otherwise
        """

        maturity_date = datetime.strptime(rec['maturity_date'], '%Y-%m-%d').date()

        if status == 'All':
            return True

        elif status == 'active':
            if maturity_date >= date.today() and rec['call_price'] == 0.0:
                return True

        elif status == 'matured':
            if maturity_date < date.today():
                return True

        elif status == 'closed':
            if maturity_date < date.today() or rec['call_price'] != 0.0:
                return True

        elif status == 'called':
            if rec['call_price'] != 0.0:
                return True
            else:
                return False

        return False

    def validate_bond_entry(self, rec, column_desc):
        """Validate the content of a bond record. 

        This function is called when a user hits Update on the Account Edit 
        screen with the intent of saving his changes. The changes may
        have been made to modify an existing entry of create a new one.

        To generate error messages, I extract column headings from the column
        descriptors. This allows the headings to be changed and the error
        message will automatically be updated. Note also that I strip \n
        or new_line characters out of the headings. The heading may look good
        split across 2 lines but the error messages looks funky."""

        settlement_date = datetime.strptime(rec['purchase_date'], '%Y-%m-%d')
        maturity_date = datetime.strptime(rec['maturity_date'], '%Y-%m-%d')
        header = "CUSIP: {}\n".format(rec["cusip"])

        if rec["cusip"] == "":
            return header + "\"{}\" may not be blank.".format(
                    self.get_column_heading("cusip", column_desc))

        elif rec["account_name"] == "":
            return header + "\"{}\" must be a valid account.".format(
                    self.get_column_heading("account_name", column_desc))

        elif rec["bond_price"] < 50 or rec["bond_price"] > 150:
            return header + "\"{}\" is out of range ($50 - $150).".format(
                    self.get_column_heading("bond_price", column_desc))

        elif rec["quantity"] < 1:
            return header + "\"{}\" must be a minimum of one.".format(
                    self.get_column_heading("quantity", column_desc))

        elif rec["quantity"] < 1:  # must be integer
            return header + "\"{}\" must be a minimum of one.".format(
                    self.get_column_heading("quantity", column_desc))

        elif rec["coupon"] <= 0:
            return header + "\"{}\" must be greater than 0.".format(
                    self.get_column_heading("coupon", column_desc))

        elif rec["fee"] < 0:
            return header + "\"{}\" must have a positive value or zero.".format(
                    self.get_column_heading("fee", column_desc))

        elif settlement_date >= maturity_date:
            return header + "\"{}\" must be after \"{}\".".format(
                self.get_column_heading("maturity_date", column_desc).
                                        replace("\n", " "),
                self.get_column_heading("purchase_date", column_desc))
        elif rec["frequency"] == "":
            return header + "\"{}\" must be a valid value.".format(
                self.get_column_heading("frequency", column_desc).
                                        replace("\n", " "))

        elif rec["call_price"] != 0:
            if rec["call_price"] < 50 or rec["call_price"] > 150:
                return header + \
                       "\"Call Redemption Price\" is out of range ($50 - $150)."

            call_date = datetime.strptime(rec['call_date'], '%Y-%m-%d')

            if call_date >= maturity_date:
                return header + \
                       "\"Call Date\" must be before the \"{}\".".format(
                            self.get_column_heading("maturity_date", column_desc).
                                                    replace("\n", " "))
            if call_date <= settlement_date:
                return header + \
                       "\"Call Date\" must be after the \"{}\".".format(
                            self.get_column_heading("purchase_date", column_desc).
                                                    replace("\n", " "))
        return ""

    def validate_fund_entry(self, rec, column_desc):
        """Validate the content of a fund record."""
        print(rec)
        header = ""
        if rec["account_name"] == "":
            return header + "\"{}\" must be a valid account name.".format(
                    self.get_column_heading("account", column_desc))

        elif rec["fund"] == "":
            return header + "\"{}\" must be a valid fund.".format(
                    self.get_column_heading("fund", column_desc))

        elif rec["date"] == "":
            return header + "\"{}\" must be a valid date.".format(
                    self.get_column_heading("date", column_desc))

        elif rec["frequency"] == "":
            return header + "\"{}\" must be a valid value.".format(
                    self.get_column_heading("frequency", column_desc))

        return ""

    def validate_xfer_entry(self, rec, column_desc):
        """Validate the content of a transfer record. """

        header = ""
        if rec["from_account_name"] == "":
            return header + "\"{}\" must be a valid account.".format(
                    self.get_column_heading("from_account_name", column_desc))

        elif rec["to_account_name"] == "":
            return header + "\"{}\" must be a valid account.".format(
                    self.get_column_heading("to_account_name", column_desc))

        elif rec["amount"] == 0.0:
            return header + "\"{}\" can not be zero.".format(
                    self.get_column_heading("amount", column_desc))

        elif rec["frequency"] == "":
            return header + "\"{}\" must be a valid selection.".format(
                    self.get_column_heading("frequency", column_desc))

        try:
            # TODO - the rec is updated from the widget before
            # the field is validated by this function.
            # this function works off the record, not the widget
            # so I may have to validate certain fields at the widget
            # maybe when the cursor tries to leave the widget
            # ensure a valid dollar amount
            float(rec["amount"])
        except ValueError:
            return header + "\"{}\" contains an invalid amount.".format(
                    self.get_column_heading("amount", column_desc))

        return ""

    def validate_account_entry(self, rec, column_desc):
        """Validate the content of a account record. """
        if rec["account_name"] == "":
            return "Account must have a non-blank Account Name"

        header = rec["account_name"] + ": "
        """
        if 'newRecKey' in rec and self.parent.get_account_rec(rec['account_id']) != None:
            return "\"{}\" \'{}\' already exists. ".format(
                    self.get_column_heading("account", column_desc),
                    rec['account_id']) + \
                   "Change the name on account with {} \'{}\' or Cancel".\
                       format(self.get_column_heading("account_id", column_desc),
                              rec['account_id'])
        """
        if rec["account_number"] == "":
            return header + "\"{}\" may not be left blank.".format(
                    self.get_column_heading("account_number", column_desc))

        elif rec["account_type"] == "":
            return header + "\"{}\" must be a valid entry.".format(
                self.get_column_heading("account_type", column_desc))

        elif rec["update_method"] != "Manual" and rec["account_number"] == "":
            return header + \
                   "\"{}\" field may not be left blank when {} is specified." \
                       .format(self.get_column_heading("account_number", column_desc),
                               self.get_column_heading("update_method", column_desc))
        return ""

    def validate_ca_entry(self, rec, column_desc):
        """Validate the content of a cash account record. """
        header = ""
        if rec["account_name"] == "":
            return header + "\"{}\" may not be left blank.".format(
                    self.get_column_heading("account_name", column_desc))

        elif rec["frequency"] == "":
            return header + "\"{}\" must be a valid entry.".format(
                    self.get_column_heading("frequency", column_desc))

        return ""

    def validate_cd_entry(self, rec, column_desc):
        """Validate the content of a cd record. """

        settlement_date = datetime.strptime(rec['purchase_date'], '%Y-%m-%d')
        maturity_date = datetime.strptime(rec['maturity_date'], '%Y-%m-%d')
        header = "CUSIP: {}\n".format(rec["cusip"])

        if rec["cusip"] == "":
            return header + "\"{}\" may not be blank.".format(
                    self.get_column_heading("cusip", column_desc))

        elif rec["account_name"] == "":
            return header + "\"{}\" must be a valid account.".format(
                    self.get_column_heading("account_name", column_desc))

        elif rec["purchase_price"] <= 0:
            return header + "\"{}\" may not be zero.".format(
                    self.get_column_heading("purchase_price", column_desc))

        elif rec["quantity"] < 1:
            return header + "\"{}\" must be a minimum of one.".format(
                    self.get_column_heading("quantity", column_desc))

        elif rec["quantity"] < 1:  # must be integer
            # todo - this is a dup of the previous check
            return header + "\"{}\" must be a minimum of one.".format(
                    self.get_column_heading("quantity", column_desc))

        elif rec["rate"] <= 0:
            return header + "\"{}\" must be greater than 0.".format(
                    self.get_column_heading("rate", column_desc))

        elif settlement_date >= maturity_date:
            return header + "\"{}\" must be after \"{}\".".format(
                self.get_column_heading("maturity_date", column_desc).
                                        replace("\n", " "),
                self.get_column_heading("purchase_date", column_desc).
                                        replace("\n", " "))
        elif rec["frequency"] == "":
            return header + "\"{}\" must be a valid value.".format(
                    self.get_column_heading("frequency", column_desc))
        return ""

    def validate_loan_entry(self, rec, column_desc):
        """Validate the content of a loan record. """

        orig_date = datetime.strptime(rec['orig_date'], '%Y-%m-%d')
        payoff_date = datetime.strptime(rec['payoff_date'], '%Y-%m-%d')

        header = ""

        if rec["account_name"] == "":
            return header + "\"{}\" must be a valid account.".format(
                    self.get_column_heading("account_name", column_desc))

        elif rec["balance"] <= 0:
            return header + "\"{}\" must <be greater than zero.".format(
                    self.get_column_heading("balance", column_desc))

        elif orig_date >= payoff_date:
            return header + "\"{}\" must be after \"{}\".".format(
                self.get_column_heading("payoff_date", column_desc).
                                        replace("\n", " "),
                self.get_column_heading("orig_date", column_desc).
                                        replace("\n", " "))
        elif rec["frequency"] == "":
            return header + "\"{}\" must be a valid value.".format(
                    self.get_column_heading("frequency", column_desc))
        return ""

    def import_accounts(self):
        if self.import_account_win_open is False:
            accounts = self.parent.get_accounts_with_import_methods()
            if len(accounts) > 0:
                self.import_account_win_open = True
                ImportAccountsWin(self, accounts)
            else:
                messagebox.showerror("Import Accounts",
                                    "You must first assign an import method "+
                                    "to at leaset one account.")

    def ImportAccountsWin_return(self):
        """This funtion is required by the ImportAccountsWin class.

        It is called when the ImportAccountsWin window is closed
        """
        self.import_account_win_open = False

    def import_bonds(self):
        if self.import_bond_details_win_open is False:
            self.import_bond_details_win_open = True
            accounts = self.parent.get_accounts_with_bond_import_methods()
            ImportBondDetailsWin(self,accounts)

    def ImportBondDetailsWin_return(self):
        """This function is required by the ImportBondDetailsWin class.

        It is called when the ImportBondsDetailsWin window is closed
        """
        self.import_bond_details_win_open = False

    @staticmethod
    def get_column_heading(key, column_desc):
        for entry in column_desc:
            if entry['key'] == key:
                return entry['heading']
        return "UNKNOWN"


class StatusBar:
    """The status bar is presented at the bottom of the window.

     The status bar contains useful information such as data file path.
    """

    LABEL = "Current Data File: "

    def __init__(self, master):
        self.datafile = "None"

        frame = local_util.add_frame(master, side=tk.BOTTOM, fill=tk.X, expand=0)

        self.status = ttk.Label(frame,
                                text=StatusBar.LABEL + self.datafile,
                                anchor=tk.W)
        self.status.pack(anchor=tk.W)

    def set_datafile(self, filename):
        self.datafile = filename
        self.status.configure(text=StatusBar.LABEL + self.datafile)

class CfGui:
    """This is the main class for the GUI.  

    It will construct the window and add all the required components.
    The 'data_source' will provide account data."""

    def __init__(self, data_source, file_manager, logger):
        """The init method creates the user frame and related objects.
        The run() function puts it up on the screen.
        The user can then open a data file which triggers creation of
        the text frame"""

        self.ds = data_source
        self.logger = logger
        self.root = tk.Tk()
        self.root.title("Cash Flow Analysis")
        cf_styles.set_styles()
        #self.settings_mgr = SettingsManager()
        self.fm = file_manager
        self.fm.set_gui(self)
        self.mb = MyMenuBar(self.root, self)
        self.bf = gui.ButtonFrame(self, self.root, self.ds,
                                  data_source.start_date,
                                  data_source.end_date, mode="Graph")
        self.gf = GraphFrame(self, self.root, w=800, h=400)
        self.tf = None         # we'll create the text frame later
        self.sf = StatusBar(self.root)

    def run(self):
        """Display the user window and wait for a data file to be opened.

        When the user opens a file, open_data_file() will call restart()."""

        h = 550  # size of initial window put up
        w = 800

        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = int((ws / 2) - (w / 2))
        y = int((hs / 2) - (h / 2))

        # set the dimensions of the screen and where it is placed
        # print("w={}, h={}, x={}, y={}".format(w,h,x,y))
        self.root.geometry('{}x{}+{}+{}'.format(w, h, x, y))

        self.root.mainloop()

    def update_graph(self):
        accnt_data = self.ds.get_account_data(
                self.bf.get_active_account_id(),
                self.bf.get_granularity(),
                self.bf.start_date,
                self.bf.end_date)
        if accnt_data:
            self.gf.graph_data(accnt_data)
        # self.sf   # TODO - work on updating the status bar

    def update_text(self):
        # A new data file may have no accounts
        active_account_id = self.bf.get_active_account_id()
        if active_account_id != "":
            accnt_data = self.ds.get_register(active_account_id)
            self.tf.show_text(accnt_data)

    def get_granularity(self):
        return self.bf.get_granularity()

    def mode_change(self, new_mode):
        if new_mode == 'Graph':
            if self.tf:
                self.tf.close_up()
                self.tf = None
            if not self.gf:
                self.root.title("Cash Flow Graph")
                self.gf = GraphFrame(self, self.root, w=800, h=400)
            # Get the active account and requests its data
            self.update_graph()
        else:
            if self.gf:
                self.gf.close_up()
                self.gf = None
            if not self.tf:
                self.root.title("Cash Flow Report")
                self.tf = gui.TextFrame(self, self.root, w=900, h=400)
            # Get the active account and requests its data
            self.update_text()

    def get_root(self):
        return self.root

    def get_menu_bar(self):
        return self.mb

    def format_date(self, date):
        return self.ds.format_date(date)

    def get_from_db(self, table, column=None, value=None):
        return self.ds.get_from_db(table, column, value)

    def get_real_accounts(self, table):
        return self.ds.get_real_accounts(table)

    def get_accounts_OBFISCATED(self):
        return self.ds.get_accounts()

    def get_account_rec(self, account):
        return self.ds.get_account_rec(account)

    def get_cash_accounts_OBFISCATED(self):
        return self.ds.get_cash_accounts()

    def get_cds_OBFISCATED(self):
        return self.ds.get_cds()

    def get_loans_OBFISCATED(self):
        return self.ds.get_loans()

    def get_bonds_OBFISCATED(self):
        return self.ds.get_bonds()

    def get_bond_cash_flow(self, bond_entry_from_source):
        return self.ds.bond_cash_flow(bond_entry_from_source)

    def get_funds_OBFISCATED(self):
        return self.ds.get_funds()

    def get_transfers_OBFISCATED(self):
        return self.ds.get_transfers()

    def get_sorted_accounts_list(self, expense=False, income=False):
        return self.ds.get_sorted_accounts_list(expense, income)

    def get_new_rec(self, instrument_type):
        return self.fm.get_new_rec(instrument_type)

    #def set_settings(self, settings):
    #    self.settings_mgr.set_settings(settings)

    def set_setting(self, setting, value):
        self.ds.set_setting(setting, value)

    def write_to_db(self, table, rec_id, modified_data):
        self.ds.write_to_db(table, rec_id, modified_data)

    def new_db_rec(self, table, rec):
        self.ds.new_db_rec(table, rec)

    def delete_db_rec(self, table, rec_id):
        self.ds.delete_db_rec(table, rec_id)

    def get_settings(self, column=None):
        """Get the requested setting(s)

        If a single setting is requested, return just that setting.
        Otherwise, return a dictionary of settings.

        """
        setting = self.ds.get_from_db('setting')

        # At start up, some data is needed before the DB is open.
        if len(setting) == 0:
            return ""
        else:
            if column == None:
                return setting[0]             # return a dictionary
            else:
                return setting[0][column]     # return a scalar

    def init_ds_storage(self):
        self.ds.init_storage()

    def account_delete(self, account):
        self.ds.account_delete(account)

    def account_create(self, rec):
        self.ds.account_create(rec)

    def account_name_changed(self, old_name, new_name):
        self.ds.account_name_changed(old_name, new_name)

    def restart(self):
        self.ds.restart(int(self.get_settings('tracking_months')))

        # Update account list and date range
        self.bf.restart()

        if self.bf.get_mode() == "Text":
            if self.tf:
                self.tf.close_up()
            self.tf = gui.TextFrame(self, self.root, w=800, h=400)
            # Get the active account and requests its data
            self.update_text()
        else:
            if self.gf:
                self.gf.close_up()
            self.gf = GraphFrame(self, self.root, w=800, h=400)
            # Get the active account and requests its data
            self.update_graph()

    def update_bf_account_list(self):
        self.bf.update_account_list()

    def get_file_manager(self):
        return self.fm

    def set_datafile(self, filename):
        self.sf.set_datafile(filename)

    def init_storage(self):
        self.ds.init_storage()

    def log(self, lvl, debug_str):
        self.ds.log(lvl, debug_str, )

    def get_tracking_end_date(self):
        return self.ds.get_end_date()

    def get_inflated_amounts(self, amount, inflation, dates):
        return self.ds.get_inflated_amounts(amount, inflation, dates)

    def get_account_id_map(self):
        return self.ds.get_account_id_map()

    def get_account_id(self, account_name):
        return self.ds.get_account_rec_id(account_name)

    def get_accounts_with_import_methods(self):
        return self.ds.get_accounts_with_import_methods()

    def get_accounts_with_bond_import_methods(self):
        return self.ds.get_accounts_with_bond_import_methods()

    def get_account_update_method(self, acc_id):
        return self.ds._update_method(acc_id)

    def update_account(self,account_id, account_details): # todo - maybe this goes away
        self.ds.update_account(account_id, account_details)

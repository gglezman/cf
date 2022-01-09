#
# Author: Greg Glezman
#
# Copyright (c) 2018-2022 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to present a GUI to the cash flow application.
#

import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime
from tkinter import messagebox
import utilities as util
import data_file_constants as dfc
from datepicker import DatePicker
import utils as local_util


class TextFrame:
    """The text frame is used to view register transactions as text
    (as opposed to a graphic view of the summary)"""
    # todo - width and h are not used - same issue for graph frame
    def __init__(self, parent, master, w=400, h=300):
        # parent is GUI; master is Tk()
        self.parent = parent
        self.frame = local_util.add_frame(master)
        self.text_pad = local_util.add_borderless_frame(self.frame)
        self.text = tk.Text(self.text_pad)
        self.text.config(state=tk.DISABLED)  # disable editing
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scroll = ttk.Scrollbar(self.text_pad)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.config(command=self.text.yview)
        scroll.pack(side=tk.RIGHT, fill='y')

    def show_text(self, account_data):
        self.text.config(state=tk.NORMAL)  # allow access editing
        self.text.delete('1.0', tk.END)
        header = "{0} {1} {2} {3} {4}\n".format(
                "Date".center(10),
                "Transaction".rjust(12),
                "Balance".rjust(12),
                "    ",
                "Notes".ljust(0))
        self.text.insert(tk.END, header)

        for record in account_data:
            transaction = "{:10} {:12,.2f} {:12,.2f}      {}\n".format(
                    self.parent.format_date(record[0]),
                    record[1],
                    record[2],
                    record[3])
            self.text.insert(tk.END, transaction)

        self.text.config(state=tk.DISABLED)  # disable editing

    def close_up(self):
        self.frame.destroy()


class ButtonFrame:
    """This frame will hold a collection of useful buttons"""
    # todo w/h are not used - same issue for TextFrame
    def __init__(self, parent, master, data_source,
                 start_date, end_date, width=400, height=30, mode="Graph"):
        self.parent = parent  # GUI
        self.ds = data_source
        self.date_range_obj = None  # object to handle date range changes
        self.min_start_date = start_date  # graph earliest date
        self.start_date = start_date  # graph start date
        self.end_date = end_date  # graph end date
        self.max_end_date = end_date  # tracking end date

        ##########################
        # Button Frame
        ##########################
        frame = local_util.add_frame(master, fill=tk.X, expand=0)

        ##########################
        # Account selection
        ##########################
        l1 = ttk.Label(frame, text="Account: ")
        l1.pack(side=tk.LEFT)

        self.account = ttk.Combobox(frame, style='Common.TCombobox', width=15)
        self.account.bind('<<ComboboxSelected>>', self.account_selection)
        self.account.pack(side=tk.LEFT)

        self.update_account_list()
        self.active_account = self.account.get()

        ##########################
        # spacer between buttons
        ##########################
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(side=tk.LEFT, padx=5)

        ##########################
        # Text / Graph Mode Button
        ##########################
        self.mode_butt = ttk.Button(frame, style='MediumThin.TButton', )
        if mode == "Graph":
            self.mode_butt['text'] = "Text"
        else:
            self.mode_butt['text'] = "Graph"
        self.mode_butt.bind("<Button-1>", self.toggle_display_mode)
        self.mode_butt.pack(side=tk.LEFT)

        ##########################
        # spacer between buttons
        ##########################
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(side=tk.LEFT, padx=5)

        ##########################
        # Granularity selection
        ##########################
        ttk.Label(frame, text="Granularity: ").pack(side=tk.LEFT)

        # TODO - get this from cf.py
        granularities = ('Annual', 'Monthly', 'Weekly')
        self.granularity_cb = ttk.Combobox(frame, values=granularities,
                                           width=8)
        self.granularity_cb.bind('<<ComboboxSelected>>',
                                 self.granularity_selected)
        # <TODO - select monthly
        self.granularity_cb.current(1)

        self.granularity = "Monthly"  # default granularity
        self.granularity_cb.pack(side=tk.LEFT)

        ##########################
        # spacer between buttons
        ##########################
        sep = ttk.Separator(frame, orient='horizontal')
        sep.pack(side=tk.LEFT, padx=5)

        #################################
        # Date Range Button in Mode Frame
        #################################
        self.date_range = ttk.Button(frame, style='MediumThin.TButton',
                                     command=self.select_date_range)
        self.date_range['text'] = "Date Range"
        self.date_range.pack(side=tk.LEFT)

    def disable_granularity(self):
        self.granularity_cb.config(state=tk.DISABLED)

    def enable_granularity(self):
        self.granularity_cb.config(state=tk.NORMAL)

    def disable_date_range(self):
        self.date_range.configure(state=tk.DISABLED)

    def enable_date_range(self):
        self.date_range.configure(state=tk.NORMAL)

    def toggle_display_mode(self, _):
        if self.mode_butt['text'] == "Text":
            self.mode_butt['text'] = "Graph"
            self.disable_granularity()
            self.disable_date_range()
            self.parent.mode_change('Text')
        else:
            self.mode_butt['text'] = "Text"
            self.enable_granularity()
            self.enable_date_range()
            self.parent.mode_change('Graph')

        # Check the DateRange window
        if self.date_range_obj:
            self.date_range_obj.kill_win()
            self.date_range_obj = None

    def get_mode(self):
        """The txt on the button says where you will go to, not
        where you are at"""

        if self.mode_butt['text'] == "Text":
            return "Graph"
        else:
            return "Text"

    def get_granularity(self):
        """Return the current graph granularity"""

        return self.granularity

    def get_active_account_id(self):
        """The active account is whatever is active in the combo box"""

        account_name = self.account.get()
        return self.parent.get_account_id(account_name)

    def account_selection(self, _):
        """User has selected an account from the combo box"""

        if self.active_account != self.account.get():
            self.active_account = self.account.get()
            if self.mode_butt['text'] == "Graph":  # ie Text mode
                self.parent.update_text()
            else:
                self.parent.update_graph()

    # def granularity_selection(self):
    #    if self.granularity != self.grp.get():
    #        self.granularity = self.grp.get()
    #        self.parent.update_graph()

    def granularity_selected(self, _):
        if self.granularity != self.granularity_cb.get():
            self.granularity = self.granularity_cb.get()
            self.parent.update_graph()

    def update_account_list(self):
        self.account['values'] = self.ds.get_sorted_accounts_list()

        # Note - for a new data file, the default_account will be set to ""
        default_account = self.parent.get_settings('default_account')
        if default_account == "":
            if len(self.account['values']) > 0:
                self.account.set(self.account['values'][0])
            else:
                self.account.set("")
        else:
            self.account.set(default_account)

        self.active_account = self.account.get()

    def set_max_end_date(self, date):
        """This function is called when the tracking_months_count is changed
        in the Settings menu and hence the tracking end date changes.  Make 
        the graph match the new end_date"""

        self.max_end_date = date
        self.end_date = self.max_end_date

    def set_start_date(self, date):
        """This function is called when the tracking_months_count is changed
        in the Settings menu and hence the tracking end date changes. Also,
        the start_date may have been made invalid by a new end_date."""

        self.start_date = date

    def select_date_range(self):
        """User has depressed the "Date Range" button"""

        if not self.date_range_obj:
            self.date_range_obj = DateRange(
                    self, self.start_date, self.end_date,
                    self.min_start_date, self.max_end_date)

    def date_range_closed(self, start_date, end_date, ):
        if start_date:
            self.start_date = start_date
            if end_date > self.max_end_date:
                self.end_date = self.max_end_date
            else:
                self.end_date = end_date
        self.date_range_obj = None
        self.parent.update_graph()

    def restart(self):
        """This is called when the app restarts following modifications
        and or additions to the accounts or settings. In particular, the user
        has added an account or changed he tracking_months"""

        self.update_account_list()

        self.set_start_date(self.ds.get_start_date())
        self.set_max_end_date(self.ds.get_end_date())


class DateRange:
    NUM_DATE_BUTTS = 2  # start_date and end_date
    """Select a date range for display in the graph frame

    *Args*
        parent (object): calling object

        start_date (datetime):

        end_date (datetime):

        min_start_date (datetime): earliest possible acceptable date

        max_end_date (datetime): latest possible acceptable date
    """

    def __init__(self, parent, start_date, end_date,
                 min_start_date, max_end_date):
        self.parent = parent  # ButtonFrame
        self.start_date = start_date
        self.end_date = end_date
        self.min_start_date = min_start_date
        self.max_end_date = max_end_date

        if type(start_date) != datetime or type(end_date) != datetime:
            raise TypeError("Must be datetime object")

        self.dr_button = []
        self.date_picker_result = []
        self.date_range_pickers = []
        for i in range(DateRange.NUM_DATE_BUTTS):
            self.date_picker_result.append({'token_key': i})
            self.date_range_pickers.append(None)

        ################################################
        # Window
        ################################################
        self.range_win = tk.Toplevel()
        self.range_win.title("Graph Date Range")
        self.range_win.protocol("WM_DELETE_WINDOW", self.cancel_date_range)
        ################################################
        # Frame for date picker buttons
        ################################################
        frame = local_util.add_frame(self.range_win)

        ttk.Label(frame, text="Start Date",
                  width=dfc.FW_SMALL).grid(row=0, column=0)
        ttk.Label(frame, text="End Date",
                  width=dfc.FW_SMALL).grid(row=0, column=1)

        s_date = "{}-{:02}-{:02}".format(start_date.year,
                                         start_date.month,
                                         start_date.day)
        self.dr_button.append(ttk.Button(frame,
                                         text=s_date,
                                         style='Thin.TButton',
                                         command=lambda butt_num=0:
                                             self.date_range_picker(butt_num)))
        self.dr_button[-1].grid(row=1, column=0)
        e_date = "{}-{:02}-{:02}".format(end_date.year,
                                         end_date.month,
                                         end_date.day)
        self.dr_button.append(ttk.Button(frame,
                                         text=e_date,
                                         style='Thin.TButton',
                                         command=lambda butt_num=1:
                                         self.date_range_picker(butt_num)))
        self.dr_button[-1].grid(row=1, column=1)

        ################################################
        # Frame for cleanup buttons
        ################################################
        ctrls_frame = local_util.add_controls_frame(self.range_win)
        butt_frame = local_util.add_button_frame(ctrls_frame)

        cancel_butt = ttk.Button(butt_frame, text='Cancel',
                                 style='Medium.TButton',
                                 command=self.cancel_date_range)
        cancel_butt.pack(side=tk.RIGHT)

        update_butt = ttk.Button(butt_frame, text='Update',
                                 style='Medium.TButton',
                                 command=self.close_and_update_range)
        update_butt.pack(side=tk.RIGHT)

        ###############################################
        # Center the pop up
        ###############################################
        util.center_popup(self.range_win, self.parent.parent.get_root())

    def date_range_picker(self, butt_num):
        # check if the date picker is already open
        if self.date_range_pickers[butt_num]:
            return

        if butt_num == 0:
            date = self.start_date
            title = "Start Date"
        else:
            date = self.end_date
            title = "End Date"

        self.date_range_pickers[butt_num] = \
            DatePicker(self, butt_num, date, title=title,
                       parent_win=self.range_win)

    def DatePicker_return(self, date, butt_num):
        # This method is required by the datepicker
        """User has closed a datepicker window."""

        # Mark the datepicker closed
        self.date_range_pickers[butt_num] = None

        if date:
            self.dr_button[butt_num].configure(text=date.strftime('%Y-%m-%d'))

            # we really store datetime not date
            if butt_num == 0:
                self.start_date = datetime.combine(date, datetime.min.time())
            else:
                self.end_date = datetime.combine(date, datetime.min.time())

    def close_and_update_range(self):
        """User depressed the Update button"""

        if self.start_date >= self.end_date:
            messagebox.showinfo("Date Range Error ",
                                "Start Date must be\nbefore End Date")
        elif self.start_date < self.min_start_date:
            messagebox.showinfo("Date Range Error ",
                                "Start Date is before\nCurrent Date")
        elif self.end_date > self.max_end_date:
            messagebox.showinfo("Date Range Error ",
                                "End Date is beyond\nMax End Date of\
                                    {}".format(self.max_end_date.date()))
        else:
            self.parent.date_range_closed(self.start_date, self.end_date)

            self.kill_subordinate_windows()
            self.range_win.destroy()

    def cancel_date_range(self):
        """User depressed the Cancel button"""

        self.parent.date_range_closed(None, None)
        self.kill_subordinate_windows()
        self.range_win.destroy()

    def kill_win(self):
        self.kill_subordinate_windows()
        self.range_win.destroy()

    def kill_subordinate_windows(self):
        for i in range(DateRange.NUM_DATE_BUTTS):
            if self.date_range_pickers[i]:
                self.date_range_pickers[i].kill_win()
                self.date_range_pickers[i] = None

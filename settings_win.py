#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2019 G.Glezman.  All Rights Reserved.
#
# This file contains code for the settings window for the
# Cash Flow Analysis application.

# Keep the next two statements in order so ttk widgets override TK widgets
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import StringVar
import utilities as util
import utils as local_util


class SettingsWin:
    def __init__(self, parent, parent_win, menu_bar):
        self.parent = parent  # Gui
        self.menu_bar = menu_bar  # menu bar on Gui

        ############################
        # Capture the current settings
        ############################
        self.old_settings = parent.get_settings()

        ############################
        # Window
        ############################
        self.settings_win = tk.Toplevel(width=1000, height=50)
        self.settings_win.title("Settings")
        self.settings_win.protocol("WM_DELETE_WINDOW", self.cancel_settings)
        self.settings_win.geometry('255x130')

        ############################
        # Frame for setting options
        ############################
        frame = local_util.add_frame(self.settings_win)

        ############################
        # Setting options
        ############################
        row = 0
        col = 0
        ###################
        # Tracking Months
        ###################
        tracking_months = ['1', '3', '6', '9', '12', '18', '24', '30', '36',
                           '48', '60', '72', '120']

        ttk.Label(frame, text="Tracking Months:",
                  style='MediumLeft.TLabel'). \
            grid(row=row, column=col, sticky='W')
        col += 1
        # 'width' could not be integrated into the style
        self.tm_var = StringVar(frame)
        self.tracking_months_combo = ttk.Combobox(frame, width=15,
                                                  textvariable=self.tm_var,
                                                  style='Common.TCombobox')
        self.tracking_months_combo.grid(row=row, column=col)
        self.tracking_months_combo.set(
                int(self.parent.get_settings('tracking_months')))
        self.tracking_months_combo['values'] = tracking_months

        ###################
        # Default Account
        ###################
        # The default account is specified in the settings.
        # If nothing is specified in settings, use the first entry
        # in the account list.
        # If the account list is empty (eg new data file) use ""
        row += 1
        col = 0

        ttk.Label(frame, text="Default Account:",
                  style='MediumLeft.TLabel'). \
            grid(row=row, column=col, sticky='W')
        col += 1

        self.default_account_var = StringVar(frame)
        self.account_combo = ttk.Combobox(frame, width=15,
                                          textvariable=self.default_account_var,
                                          style='Common.TCombobox')

        self.account_combo['values'] = self.parent.get_sorted_accounts_list\
            ()

        self.account_combo.grid(row=row, column=col)
        if self.parent.get_settings('default_account') == "":
            if len(self.account_combo['values']) > 0:
                self.account_combo.set(self.account_combo['values'][0])
            else:
                self.account_combo.set("")
        else:
            self.account_combo.set(self.parent.get_settings('default_account'))

        ###################
        # Bonds per page
        ###################
        row += 1
        col = 0

        bonds_per_page = ['15', '20', '25', '30', '35', '40', '45']
        ttk.Label(frame, text="Bonds Per Page:",
                  style='MediumLeft.TLabel'). \
            grid(row=row, column=col, sticky='W')
        col += 1
        self.bonds_per_page_combo = ttk.Combobox(frame, width=15,
                                                 style='Common.TCombobox')
        self.bonds_per_page_combo.grid(row=row, column=col)
        self.bonds_per_page_combo.set(
                int(self.parent.get_settings('bonds_per_page')))
        self.bonds_per_page_combo['values'] = bonds_per_page

        ###################
        # Graph Type
        ###################
        row += 1
        col = 0

        graph_types = ['bar', 'line']
        ttk.Label(frame, text="Graph Type:",
                  style='MediumLeft.TLabel'). \
            grid(row=row, column=col, sticky='W')
        col += 1
        self.graph_type_combo = ttk.Combobox(frame, width=15,
                                             style='Common.TCombobox')
        self.graph_type_combo.grid(row=row, column=col)
        self.graph_type_combo.set(self.parent.get_settings('graph_type'))
        self.graph_type_combo['values'] = graph_types

        ############################
        # Frame for cleanup buttons
        ############################
        ctrls_frame = local_util.add_controls_frame(self.settings_win)
        butt_frame = local_util.add_button_frame(ctrls_frame)

        cancel_butt = ttk.Button(butt_frame, text='Cancel',
                                 command=self.cancel_settings)
        cancel_butt.pack(side=tk.RIGHT)

        update_butt = ttk.Button(butt_frame, text='Update',
                                 command=self.close_and_update_settings)
        update_butt.pack(side=tk.RIGHT)

        ############################
        # Center the pop-up
        ############################
        util.center_popup(self.settings_win, parent_win)

    def close_and_update_settings(self):
        write_data_file = False

        # Tracking Months
        if self.old_settings['tracking_months'] != \
                self.tracking_months_combo.get():
            self.parent.set_setting('tracking_months',
                                    self.tracking_months_combo.get())
            tracking_months_changed = True
            write_data_file = True
        else:
            tracking_months_changed = False

        # Default Account
        if self.old_settings['default_account'] != \
                self.account_combo.get():
            self.parent.set_setting('default_account',
                                    self.account_combo.get())
            default_account_changed = True
            write_data_file = True
        else:
            default_account_changed = False

        # Bonds_per_page
        if self.old_settings['bonds_per_page'] != \
                self.bonds_per_page_combo.get():
            self.parent.set_setting('bonds_per_page',
                                    self.bonds_per_page_combo.get())
            bonds_per_page_changed = True
            write_data_file = True
        else:
            bonds_per_page_changed = False

        # Graph Type
        if self.old_settings['graph_type'] != \
                self.graph_type_combo.get():
            self.parent.set_setting('graph_type',
                                    self.graph_type_combo.get())
            graph_type_changed = True
            write_data_file = True
        else:
            graph_type_changed = False

        ##################################
        # Write the settings to the
        # current data file
        ##################################
        if write_data_file:
            self.parent.fm.write_data_file()

        ##################################
        # Deal with changed setting
        ##################################
        if tracking_months_changed:
            # Recalculate all accounts
            self.parent.restart()
        if graph_type_changed:
            pass
        if bonds_per_page_changed:
            pass
        if default_account_changed:
            pass

        # inform the calling class we have closed the window
        self.menu_bar.edit_window_closed('settings')
        self.settings_win.destroy()

    def cancel_settings(self):
        self.menu_bar.edit_window_closed('settings')
        self.settings_win.destroy()

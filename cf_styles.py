#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to initialize ttk styles used.
#

import tkinter as tk
import tkinter.ttk as ttk
import data_file_constants as dfc

DELETE_COLOR = 'firebrick1'

def set_styles():

    s = ttk.Style()

    ##############################
    # Label Styles
    ##############################
    s.configure('Centered.TLabel', justify='center', anchor='center')
    s.configure('Medium.TLabel', padding=(2, 2))
    # not sure if anchor in the following works
    s.configure('MediumLeft.TLabel',
                # justify='right',  # I get left justified labels
                # anchor=tk.W,      #     without these 2 options
                padding=(2, 2))
    s.configure('ThinLeft.TLabel',padding=(1, 1))
    s.configure('Padded.TLabel', padding=(12, 0, 8))
    s.configure('NoPad.TLabel', padding=(0, 0, 0))
    s.configure('LimitedPad.TLabel', padding=(6, 0, 3))
    s.configure('Borderless.TLabel', borderwidth=0, padding=(6, 2, 1))

    ##############################
    # Labelframe Styles
    ##############################
    s.configure('Ridge.TLabelframe',
                borderwidth=dfc.SMALL_BORDER_WIDTH,
                relief=tk.RIDGE)
    s.configure('Padded5Ridge.TLabelframe',
                borderwidth=dfc.SMALL_BORDER_WIDTH,
                relief=tk.RIDGE, padding=5)

    ##############################
    # Frame Styles
    ##############################
    s.configure('White.TFrame', background='White')

    ##############################
    # Button Styles
    ##############################
    s.configure('TButton', padding=(1, 3))
    s.configure('Medium.TButton', padding=(2, 2))
    s.configure('MediumThin.TButton', padding=(1, 1))
    s.configure('Thin.TButton', padding=(0, 0))
    s.configure('Special.Thin.TButton')
    s.configure('Borderless.TButton', borderwidth=0,
                background='White', anchor='w', padding=(18, 2, 1))

    s.map("Special.Thin.TButton", background=[('disabled', DELETE_COLOR)])

    ##############################
    # Entry Styles
    ##############################
    s.configure('Special.TEntry')

    ##############################
    # Combobox Style
    ##############################
    # width in the following does not work
    s.configure('Common.TCombobox', width=9)
    s.configure('Special.TCombobox')

    ##############################
    # Radiobutton Styles
    ##############################
    s.configure('TRadiobutton', padding=(1, 3))

    ##############################
    # Mappings 
    ##############################
    s.map("Special.TEntry", fieldbackground=[('disabled', DELETE_COLOR)])
    s.map("Special.TCombobox", fieldbackground=[('disabled', DELETE_COLOR)],
          arrowcolor=[('disabled', DELETE_COLOR)],
          background=[('disabled', DELETE_COLOR)])

    # print(s.layout('TCombobox'))
    # print(s.element_options('Combobox.field'))
    # print(s.element_options('Combobox.downarrow'))
    # print(s.element_options('Combobox.padding'))
    # print(s.element_options('Combobox.textarea'))
    # print(s.layout('TLabel'))
    # print(s.element_options('Label.label'))

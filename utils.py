#
# Author: Greg Glezman
#
# Copyright (c) 2018-2022 G.Glezman.  All Rights Reserved.
#
# Useful utilities

# Place utils for this module in this file.
# Place more global utils in helper/src/utilities.py

import tkinter as tk
import tkinter.ttk as ttk
import data_file_constants as dfc


################################################
# Frame Architecture for this module
################################################
#
# Generally, try to apply this everywhere possible
#
# Start with a window (Toplevel())
# Add Frames
#  Top frame:       add_label_frame - optional filter
#  Middle frame:    add_frame() - content of some kind
#  Control_Frame    add_controls_frame() - lower section for controls
#     Button_Frame: add_button_frame() - far right
#     Page_Frame:   add_page_frame - far left
#     Scroll_Frame: add_scroll_frame - middle of control frame
#

def add_label_frame(parent, text, style=None, x_padx=2, x_pady=2):
    """Add a frame to the window.The frame will get filter combo buttons. """

    if style:
        frame = ttk.LabelFrame(parent, style=style, text=text)
    else:
        frame = ttk.LabelFrame(parent, text=text)
    # x_pady puts space around the outside of the frame
    frame.pack(fill=tk.BOTH, expand=1, padx=x_padx, pady=x_pady)
    return frame


def add_frame(parent, x_padx=2, y_pady=2, i_pad=3,
              fill=tk.BOTH, expand=1, side=tk.TOP):
    """Add a frame to the given window.

    *Args*
        parent (object): Owner of the frame

        x_pad / y_pad: spacers around the outside of the border.

        i_pad : padding internal to the border
    """

    # Frame padding is internal to the border
    frame = ttk.Frame(parent, padding=i_pad,
                      borderwidth=dfc.SMALL_BORDER_WIDTH,
                      relief=tk.RIDGE)
    if expand == 1:
        # Stretch on resize
        frame.pack(fill=fill, expand=1, padx=x_padx, pady=y_pady, side=side)
    else:
        frame.pack(fill=fill, padx=x_padx, pady=y_pady, side=side)

    return frame


def add_borderless_frame(parent, x_padx=2, x_pady=2, i_pad=0,
                         side=tk.TOP, fill=tk.BOTH, expand=1, style=None):
    """Add a borderless frame to the given window.

    The x_padx and x_pady values place spacers around the outside of the border.
    The i_pad value is padding internal to the border.
    """
    if style:
        frame = ttk.Frame(parent, padding=i_pad, style=style)
    else:
        frame = ttk.Frame(parent, padding=i_pad)

    if expand == 1:
        # Stretch on resize
        frame.pack(fill=fill, expand=1, padx=x_padx, pady=x_pady, side=side)
    else:
        frame.pack(fill=fill, padx=x_padx, pady=x_pady, side=side)

    return frame


def add_controls_frame(parent, x_padx=2, x_pady=2, i_pad=(3, 3, 3, 2)):
    """Add a frame to the window. Bottom of the window.

    The x_padx and x_pady values place spacers around the outside of the border.
    """

    # Frame padding is internal to the border
    frame = ttk.Frame(parent, padding=i_pad,
                      borderwidth=dfc.SMALL_BORDER_WIDTH, relief=tk.RIDGE)
    frame.pack(fill=tk.BOTH, expand=1, padx=x_padx, pady=x_pady)
    return frame


def add_button_frame(parent):
    """Add a button frame to the given parent frame.

    We like button frames on the right"""
    frame = ttk.Frame(parent)
    frame.pack(side=tk.RIGHT)
    return frame


def add_page_frame(parent):
    """Add a frame to the window.The frame will get page indications."""

    frame = ttk.Frame(parent)
    frame.pack(side=tk.LEFT)
    return frame


def add_scroll_frame(parent):
    """Add a frame to the window.The frame will get scroll controls."""

    frame = ttk.Frame(parent)
    frame.pack()
    return frame

#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2019 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to an occurrence.  An occurrence represents how often and for how long
# an event (e.g. transfer between accounts) will occur
#
#

import platform
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import datetime, time
from datepicker import DatePicker
import data_file_constants as dfc
import utilities as util
from occurrences import Occurrences, EndDate
import utils as local_util
from scrollable_win import ScrollableWin

days_of_month = ['NA', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
                 '9th', '10th', '11th', '12th', '13th', '14th', '15th',
                 '16th', '17th', '18th', '19th', '20th', '21st', '22nd',
                 '23rd', '24th', '25th', '26th', '27th', '28th', '29th',
                 '30th', '31st']

if platform.system() == 'Linux':
    WIN_HEIGHT = 143
    WIN_WIDTH = 460
else:
    WIN_HEIGHT = 155
    WIN_WIDTH = 455


class OccurrenceWin:

    def __init__(self, account_edit_obj, title, occurrence_spec, last_date, token,
                 master=None):
        self.account_edit_obj = account_edit_obj
        self.last_date = last_date  # TODO - no need to save this
        self.occ = Occurrences(occurrence_spec, last_date)
        self.token = token
        self.start_date_butt = None
        self.regularity = None
        self.current_regularity = None
        self.weekly_interval = None
        self.second_day = None
        self.month_interval = None
        self.end_date_type = None
        self.occ_count = None
        self.end_date_butt = None
        self.current_end_date_type = None

        self.datepicker_windows = {}

        # all rows use the same width for the first 2 columns.  Looks better
        if platform.system() == 'Linux':
            self.FIRST_COL_WIDTH = 8
            self.SECOND_COL_WIDTH = 11
        else:
            self.FIRST_COL_WIDTH = 10
            self.SECOND_COL_WIDTH = 14

        ###############################################
        # The window...
        ###############################################
        self.win = tk.Toplevel()
        self.win.title(title)
        self.win.protocol("WM_DELETE_WINDOW", self.cancel_win)

        ###############################################
        # Create the Frames
        ###############################################
        self.selection_frame = local_util.add_frame(self.win)
        self.start_date_frame = local_util.add_borderless_frame(
            self.selection_frame, i_pad=(2, 4))
        self.regularity_frame = local_util.add_borderless_frame(
                self.selection_frame, i_pad=(2, 4))
        self.end_date_frame = local_util.add_borderless_frame(
                self.selection_frame, i_pad=(2, 4))
        self.controls_frame = local_util.add_controls_frame(self.win)
        self.button_frame = local_util.add_button_frame(self.controls_frame)

        ###############################################
        # Fill the frames
        ###############################################
        self.add_start_date_widgets(self.start_date_frame, self.occ)
        self.add_regularity_widgets(self.regularity_frame, self.occ)
        self.add_end_date_widgets(self.end_date_frame, self.occ)
        self.add_control_buttons(self.button_frame)

        if master:
            ###############################################
            # Center the pop up
            ###############################################
            util.center_popup(self.win, master)

        self.set_win_geometry()

    def add_start_date_widgets(self, frame, occ):

        ################################
        # Start Date
        ################################
        row = 0
        col = 0
        ttk.Label(frame,
                  style='Padded.TLabel',
                  text="Start Date:",
                  width=self.FIRST_COL_WIDTH).grid(row=row, column=col)
        col += 1  # datepicker
        self.start_date_butt = ttk.Button(
                frame,
                text=occ.get_start_date(),
                width=self.SECOND_COL_WIDTH,
                style='Special.Thin.TButton')
        self.start_date_butt.configure(
                command=lambda token='start': self.open_datepicker(token))
        self.start_date_butt.grid(row=row, column=col)

    def add_regularity_widgets(self, frame, occ):
        """Add widgets associated with the regularity selection.

        Args:
            frame (frame):
            occ (occurrence) details of what to present

        This includes the regularity selection and may include number of weeks,
        number of months, second day for twice-a-month,...
        """

        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                        'Saturday', 'Sunday']

        weekly_combo_width = 2
        twice_a_month_combo_width = 4
        monthly_combo_width = 2

        start_date = occ.get_start_date()

        ################################
        # Regularity
        ################################

        # Common to all regularities - the selection combobox
        row = 0
        col = 0
        ttk.Label(frame,
                  style='Padded.TLabel',
                  text="How Often:",
                  width=self.FIRST_COL_WIDTH).grid(row=row, column=col)
        col += 1
        self.regularity = ttk.Combobox(frame,
                                       style='Special.TCombobox',
                                       width=self.SECOND_COL_WIDTH)
        self.regularity.grid(row=row, column=col)
        self.regularity['values'] = Occurrences.regularities_list
        self.regularity.set(occ.get_regularity())
        self.regularity.bind('<<ComboboxSelected>>', self.regularity_change)
        self.current_regularity = self.regularity.get()  # TODO - pull to top

        if occ.get_regularity() == 'once':
            pass  # nothing additional for this regularity

        elif occ.get_regularity() == 'weekly':
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="every",
                      ).grid(row=row, column=col)
            col += 1
            self.weekly_interval = ttk.Combobox(frame,
                                                style='Special.TCombobox',
                                                width=weekly_combo_width)
            self.weekly_interval.grid(row=row, column=col)
            self.weekly_interval['values'] = list(range(1, 53))
            self.weekly_interval.set(occ.weekly_interval)
            self.weekly_interval.bind('<<ComboboxSelected>>',
                                      self.weekly_interval_change)
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="week(s) on {}".
                      format(days_of_week[start_date.weekday()]),
                      ).grid(row=row, column=col)

        elif occ.get_regularity() == 'bi-weekly':
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="every 2 week(s) on {}".
                      format(days_of_week[start_date.weekday()]),
                      ).grid(row=row, column=col)

        elif occ.get_regularity() == 'twice-a-month':
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="on the {} and ".
                      format(days_of_month[start_date.day]),
                      ).grid(row=row, column=col)

            col += 1
            self.second_day = ttk.Combobox(frame,
                                           style='Special.TCombobox',
                                           width=twice_a_month_combo_width)
            self.second_day.grid(row=row, column=col)
            self.second_day['values'] = days_of_month
            self.second_day.set(days_of_month[occ.second_day])
            self.second_day.bind('<<ComboboxSelected>>',
                                 self.second_day_change)
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="of the month").grid(row=row, column=col)

        elif occ.get_regularity() == 'monthly':
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="every",
                      ).grid(row=row, column=col)
            col += 1
            self.month_interval = ttk.Combobox(frame,
                                               style='Special.TCombobox',
                                               width=monthly_combo_width)
            self.month_interval.grid(row=row, column=col)
            self.month_interval['values'] = list(range(1, 24))
            self.month_interval.set(occ.monthly_interval)
            self.month_interval.bind('<<ComboboxSelected>>',
                                     self.month_interval_change)
            col += 1
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="month(s) on the {}".
                      format(days_of_month[start_date.day])
                      ).grid(row=row, column=col)

        elif occ.get_regularity() == 'quarterly':
            col += 1
            s = occ.get_sample_dates(4)
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="on the {}, {}, {} and {}".format(*s),
                      ).grid(row=row, column=col)

        elif occ.get_regularity() == 'semi-annually':
            col += 1
            s = occ.get_sample_dates(2)
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="on the {} and {}".
                      format(*s)
                      ).grid(row=row, column=col)

        elif occ.get_regularity() == 'annually':
            col += 1
            s = occ.get_sample_dates(1)
            ttk.Label(frame,
                      style='LimitedPad.TLabel',
                      text="on {}".format(*s)
                      ).grid(row=row, column=col)
        else:
            raise TypeError("Unsupported regularity: {} ".format(
                    occ.get_regularity()))

    def add_end_date_widgets(self, frame, occ):
        """Add widgets associated with the end date.

        Args:
            frame (frame): frame to place the widgets in
            occ (Occurrence): contains end_date to present

        This includes the end date type selection as well as an explicit
        end_date or a number of occurrences.
        """
        combo_box_width = 2
        filler_box_width = 1

        end_date = occ.get_end_date()

        ################################
        # EndDate is disabled for regularity of 'once'
        ################################
        if self.occ.get_regularity() == 'once':
            end_date_state = tk.DISABLED
        else:
            end_date_state = tk.NORMAL

        ################################
        # End Date
        ################################
        row = 0
        col = 0
        # -------   end date type selector combobox    ---------
        ttk.Label(frame,
                  style='Padded.TLabel',
                  text="End Date:",
                  width=self.FIRST_COL_WIDTH).grid(row=0, column=col)

        col += 1
        self.end_date_type = ttk.Combobox(frame,
                                          # style='Special.TCombobox',
                                          width=self.SECOND_COL_WIDTH)
        self.end_date_type.grid(row=0, column=col)
        # active selection is made later
        self.end_date_type['values'] = ["No End Date", "End On", "End After"]
        self.end_date_type.bind('<<ComboboxSelected>>',
                                self.end_date_type_change)
        self.end_date_type.config(state=end_date_state)

        if end_date_state == tk.NORMAL:
            # ------- add-ons based on type ---------
            if end_date.has_count():
                self.end_date_type.set("End After")

                col += 1  # spacing between boxes
                ttk.Label(frame,
                          style='NoPad.TLabel',
                          text="",
                          width=filler_box_width).grid(row=row, column=col)

                col += 1  # number box
                self.occ_count = ttk.Combobox(frame,
                                              style='Special.TCombobox',
                                              width=combo_box_width)
                self.occ_count.grid(row=row, column=col)
                self.occ_count['values'] = list(range(1, 99))
                self.occ_count.set(end_date.count())
                self.occ_count.bind('<<ComboboxSelected>>',
                                    self.occ_count_change)

                col += 1  # trailing text
                if self.occ.regularity == "twice-a-month":
                    ttk.Label(frame,
                              style='LimitedPad.TLabel',
                              text="month(s)",
                              ).grid(row=row, column=col)
                else:
                    ttk.Label(frame,
                              style='LimitedPad.TLabel',
                              text="occurrence(s)",
                              ).grid(row=row, column=col)
            elif end_date.has_no_end_date():
                self.end_date_type.set("No End Date")

            elif end_date.includes_end_date():
                self.end_date_type.set("End On")

                col += 1  # spacer between boxes
                ttk.Label(frame,
                          style='NoPad.TLabel',
                          text="",
                          width=filler_box_width).grid(row=row, column=col)

                col += 1  # date picker
                self.end_date_butt = ttk.Button(
                        frame,
                        text=end_date.date().date(),  # end_date.date() is a datetime
                        width=self.SECOND_COL_WIDTH,
                        style='Special.Thin.TButton')
                self.end_date_butt.configure(
                        command=lambda token='end': self.open_datepicker(token))
                self.end_date_butt.grid(row=row, column=col)

            else:
                raise TypeError("Inconsistent end_date: {}".format(end_date))

        self.current_end_date_type = self.end_date_type.get()  # TODO copy at top

    def add_control_buttons(self, frame):
        """Add the control buttons (Cancel, Add) to the control frame."""

        cancel_butt = ttk.Button(frame, text='Cancel',
                                 style='Medium.TButton',
                                 command=self.cancel_win)
        cancel_butt.pack(side=tk.RIGHT)

        add_butt = ttk.Button(frame, text='Accept',
                              style='Medium.TButton',
                              command=self.close_and_update_win)
        add_butt.pack(side=tk.RIGHT)

        add_butt = ttk.Button(frame, text='List',
                              style='Medium.TButton',
                              command=self.open_list_win)
        add_butt.pack(side=tk.RIGHT)

    def set_win_geometry(self, width=WIN_WIDTH, height=WIN_HEIGHT):
        # geom = '{}x{}'.format(width,height)
        # print(geom)
        self.win.geometry('{}x{}'.format(width, height))

    def start_date_change(self, date):
        """The user has changed the start_date. Update the text on the 
        button and update the occ. Also, the regularity frame may be affected.
        For example, the start_date provides the day_of_the month when
        the regularity is monthly. It also provides the 1st and second days
        for twice-a-month.
        """

        self.occ.set_start_date(datetime.combine(date, time.min))

        self.start_date_butt.configure(text=date.strftime(dfc.DATE_FORMAT))

        self.repaint_regularity_frame()

    def regularity_change(self, _):
        """The user has made a selection in the regularity combobox.

        With a change in regularity, the end_date frame may need to 
        become active or disabled."""

        if self.occ.get_regularity() != self.regularity.get():
            self.occ.set_regularity(self.regularity.get())

            self.repaint_regularity_frame()

            self.repaint_end_date_frame()

    def repaint_regularity_frame(self):
        # wipe out all the old objects in the frame
        for widget in self.regularity_frame.grid_slaves():
            widget.grid_forget()

        # add the appropriate widgets based on current_regularity
        self.add_regularity_widgets(self.regularity_frame, self.occ)

        # ensure windows systems make the window big enough
        # for some reason, Windows was shrinking the size of the win
        self.set_win_geometry()

    def repaint_end_date_frame(self):
        # wipe out all the old objects in the frame
        for widget in self.end_date_frame.grid_slaves():
            widget.grid_forget()

        # add the appropriate widgets based on end date
        self.add_end_date_widgets(self.end_date_frame, self.occ)

    def end_date_change(self, date):
        """The user has changed the end_date. 

        Update the text on the button and update the occ. Also update
        the regularity frame. Changing the end_date may affect the
        sample dates in the regularity frame.
        """

        text_date = date.strftime(dfc.DATE_FORMAT)

        self.occ.set_end_date(EndDate.END_ON, date=text_date)

        self.end_date_butt.configure(text=text_date)

        self.repaint_regularity_frame()

    def month_interval_change(self, _):
        """The user has changed the month interval"""

        self.occ.set_monthly_interval(int(self.month_interval.get()))

    def weekly_interval_change(self, _):
        """The user has changed the weekly interval"""

        self.occ.set_weekly_interval(int(self.weekly_interval.get()))

    def second_day_change(self, _):
        """The user has changed the second_day"""

        self.occ.set_second_day(days_of_month.index(self.second_day.get()))

    def occ_count_change(self, _):
        """The user has changed the second_day.

        Changing the count may have an effect on the sample dates
        provided to say "Quarterly" regularity
        """

        self.occ.set_occ_count(int(self.occ_count.get()))

        self.repaint_regularity_frame()

    def open_datepicker(self, token):
        if token in self.datepicker_windows.keys():
            # TODO - see if there is a way to bring the datepicker to
            # the top of the stack
            print("Already open")
        else:
            if token == 'start':
                day = self.start_date_butt.cget('text')
                title = 'Start Date'
            elif token == 'end':
                day = self.end_date_butt.cget('text')
                title = 'End Date'
            else:
                raise TypeError("Unknown Token: {}".format(token))

            # create the datePicker and add it to the list of open datepickers
            self.datepicker_windows[token] = DatePicker(
                    self,  # caller
                    token,  # opaque data
                    date=datetime.strptime(day, "%Y-%m-%d"),
                    title=title,
                    parent_win=self.win)

    def DatePicker_return(self, date, token):
        # This method is required by the datepicker
        """User has closed a datepicker window."""

        if token in self.datepicker_windows.keys():
            del self.datepicker_windows[token]

            if date:
                if token == 'start':
                    self.start_date_change(date)
                elif token == 'end':
                    self.end_date_change(date)
                else:
                    raise TypeError("Unknown token {}".format(token))
            else:
                pass  # user cancelled out of the datepicker
        else:
            raise TypeError("Unknown datepicker:{}".format(token))

    def end_date_type_change(self, _):
        """The user has changed the end date type combobox.

        Update the occ end date and repaint the end_date frame.
        Also, selecting a new end_date may effect the sample dates
        in the regularity frame.
        """

        if self.current_end_date_type != self.end_date_type.get():
            # Update the end date within the occurrence
            if self.end_date_type.get() == "No End Date":
                self.occ.set_end_date(EndDate.NONE)
            elif self.end_date_type.get() == "End On":
                self.occ.set_end_date(EndDate.END_ON)
            else:
                self.occ.set_end_date(EndDate.COUNT)

            self.repaint_end_date_frame()
            self.repaint_regularity_frame()

    def close_and_update_win(self):
        """User has selected to Accept the occurrence description.

        If the current selections pass validation, generate a string_spec
        and pass it back to the caller.
        """
        result = self.occ.validate()
        if result == "":
            occurrence_spec = self.occ.get_string_spec()

            # Return the occurrence and signal complete
            self.account_edit_obj.OccurrenceWin_return(occurrence_spec,
                                                       self.token)
            self.close_subordinate_windows()  # just in case...
            self.win.destroy()
        else:
            messagebox.showerror("Data Error", result)

    def cancel_win(self):
        """User has decided to Cancel. Close up and signal caller"""
        self.close_subordinate_windows()  # just in case...

        # return a NULL string indicating no change
        self.account_edit_obj.OccurrenceWin_return("", self.token)

        self.win.destroy()

    def close_subordinate_windows(self):
        """Close any other windows that were opened.

        This could include datepicker windows.
        """

        for key, datepicker_obj in self.datepicker_windows.items():
            datepicker_obj.kill_win()

    def kill_win(self):
        """Calling object has decided to cancel request."""

        self.close_subordinate_windows()  # just in case...

        # DO NOT INDICATE CLOSED to caller. it already knows
        self.win.destroy()

    def open_list_win(self):
        """Open a window and fill with the list of generated dates"""

        date_list = ""
        for date in self.occ.get_dates():
            date_list += date.strftime(dfc.DATE_FORMAT) + '\n'

        # put up a window with the date list
        ScrollableWin("Occurrence List", date_list, self.win)

#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to edit account data. Account data includes items such as
#    cash accounts
#    transfers to/from an account
#    details of bonds in an account
#
#    BUT not individual transactions into/out of an account
#
import platform
import math
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from operator import itemgetter
from datetime import datetime
from collections import OrderedDict
from datepicker import DatePicker
import data_file_constants as dfc
import utilities as util
from scrollable_win import ScrollableWin
from occurrences import Occurrences
from occurrence_win import OccurrenceWin
from import_support import ImportFidelityBondList
import utils as local_util


class AccountEditWin:
	"""Edit Account related information.

	This class is used to display/edit account information (not transactions).
	For example, for a cash account the balance, interest,
	rate, interest payment date and compounding period are editable.

	This module will present current account information and track changes
	made by the user. If the user accepts the changes they will be
	written to the actual data source and pushed out to the hard drive.
	Note that a working copy of the data is made. If the user wishes
	to save the changes and they pass validation, they are copied
	back over the original version.

	*Architecture of this module...*

	The account data is presented through a collection of 'caller defined'
	widgets (ie combobox, entry boxes, checkbox). These widgets
	store the changes until the user closes the window. There are two
	exceptions:

	Occurrences Exception: The widgets involved in storing/presenting portions
	 of the occurrence (ie next_date and regularity) do not store the occurrence
	itself.	Therefore occurrences must be maintained directly in the record.
	(The next_date (in the occurrence sequence) and the regularity (eg monthly,
	yerly) are extracted from the occurrence when needed for display).

	ActionOnInstrument Exception: Some actions on instruments want to be
	performed on the information the user has entered and is currently stored
	in the widget. For example, if the user changes the inflation factor in a
	transfer, the "Transfer Schedule" action on the insturment should reflect
	the latest inflation factor. For this reason, ActionOnInstrument always
	pushed the widget content for a given row to the data_source. The actions
	then us data_source for calculations.

	In order to support filtering and paging (i.e. situations where
	the display does not present complete account data), the entire
	set of account widgets is created before any are displayed.
	The filter and paging controls determine which of the account
	data widgets will be included in the display.

	A complete list of the account widgets is kept in a two dimensional
	array. The first dimension is for each account entry and the second
	is for each widget in the presentation for any given account entry.
	The array is appropriately called 'account_widgets'.

	*Structure of the display...*

	Top_level window
		- filter_frame
			- filter widgets
		- account_frame
			- column heading labels (Button)
			- account_widgets
		- controls_frame
			- page_frame
			- scroll_frame
			- button_frame

	*Subordinate windows...*
		- actions_menu: right mouse opens a window to act on an account entry
		- bond_call_window: process a bond call event
		- new_instrument: create a new account entry
		- date pickers
		- occurrence windows

	*Args*
		parent (object): calling object

		title (str): Title to display on the pop up window
 
		column_descriptor (list( (dict) )): The column descriptor list
		   contains dictionaries which define columns to be displayed and the
		   content of the column. See below for a complete description
		   of a column_descriptor

		data_source (list(dict())): Records to display. These are cf records.

		type (str): Type of account of data being displayed. Type list includes

			- 'accounts' for top level accounts
			- 'ca' for cash account,
			- 'cd' for certificate of deposit,
			- 'loan' for outstanding loans,
			- 'bond' for detailed bond descriptions
			- 'funds'for fund summary  and
			- 'transfer' for scheduled transfers between accounts

		primary_sort_key (str): key identifying field for sorting

		secondary_sort_key (str):  key identifying field for sorting

		filters (list( dict() ), optional): Each entry in the list is a
			dictionary describing a filter to use on the data being displayed

		validation_func (func_ptr ), optional): If included, this function
			will be called to validate the record before accepting. This
			function is run when "Update" is depressed:
			func_ptr(rec, column_descriptor)

	*column_descriptor details:*
		Format
			{ 'heading':, 'key':, 'width':,' type':, 'content':}

		Where:
			key (str): used to access the data_source record
				(eg opening_date,rate,...)

			heading (str): the column heading

			width (int): is the width, in characters, of the column.

			type (str): type of widget for the data. possible values include:
				text, entry, date (button), combo(box), checkbutton,

			content:
			    if type = 'text'
			        content (str): the TTK style to be used for the field

				if type = "entry"
					content (str): this field describes how the text in the
					entry box will be formatted

					- 'text' or 'cusip': left justified
					- 'dollars' : right justified, float with 2 decimal points
					- 'rate' : right just, float, 3 decimal points
					- 'price' : right just, float, 3 decimal points
					- 'quantity' : right justified

				if type = "checkbutton"
					content (str): this field describes the application.

					- 'call' - used for bond call procedure.

					NOTE: there can only be ONE call button in an entry!!

				if type = "combo"
					content (list): list of strings to present in the combobox

				if type = "date"
					content (str): this field describes the date processing

					- 'standard': brings up a date picker screen
					- 'latest': evaluate the frequency spec in the cf records
					   and present the next date in the list following the
					   current date.
					- 'regularity': the rec field described by the 'key'
					   in the column_descriptor is an occurrence specification
					   defining the regularity of the transfers. That is,
					   rec[column_descriptor['key']] is an occurrence spec
  
	The data source varies.  It can be bonds, cash accounts, transfers,...
	The column descriptor has a keys used to access column data in the record.

	"""

	def __init__(self, parent, title, column_descriptor, data_source,
				 instrument_type, primary_sort_key, secondary_sort_key,
				 filters=None, validate_func=None):
		self.parent = parent  # GUI
		self.title = title
		self.column_descriptor = column_descriptor
		self.data_source_orig = data_source  # reference to official
		self.tracking_end_date = parent.get_tracking_end_date()
		self.data_source = []  # make a copy of the data
		for item in data_source:
			self.data_source.append(item.copy())

		self.instrument_type = instrument_type
		self.primary_sort_key = primary_sort_key
		self.secondary_sort_key = secondary_sort_key
		self.filters = filters
		self.validate_func = validate_func

		self.display_data = []  # filtered/sorted version of data_source

		self.menu_bar = parent.get_menu_bar()

		self.first_entry_to_display = 0  # paging support
		self.entries_to_display = int(parent.get_settings('bonds_per_page'))
		self.page_label = None
		self.actions_menu = None  # Subordinate windows
		self.bond_call_windows = []
		self.new_instrument_windows = []
		self.datepicker_windows = {}
		self.occurrence_windows = {}

		###############################################
		# Add an ID for ease of record tracking
		###############################################
		for id_, rec in enumerate(self.data_source):
			rec['id'] = id_
		self.next_id = len(self.data_source)

		############################################################
		# Construct all possible frames and widgets. The pieces
		# will be assembled based on filtering and sorting.
		############################################################
		self.win = self.create_top_level(title)

		if self.filters:
			self.filter_frame = self.add_filter_frame(self.win)
			self.filter_widgets = self.add_filter_widgets(self.filter_frame)
		else:
			self.filter_frame = None
			self.filter_widgets = None

		self.account_frame = local_util.add_frame(self.win)
		headings = add_heading_widgets(self.account_frame,
									   self.column_descriptor)
		self.bind_heading_widgets(headings, column_descriptor)
		self.account_widgets = self.create_account_widgets(self.account_frame,
														   column_descriptor)
		self.bind_account_widgets(self.account_widgets, column_descriptor)

		self.controls_frame = local_util.add_controls_frame(self.win)
		self.button_frame = local_util.add_button_frame(self.controls_frame)
		self.page_frame = local_util.add_page_frame(self.controls_frame)
		self.add_control_buttons(self.button_frame)
		self.scroll_frame = local_util.add_scroll_frame(self.controls_frame)

		###############################################
		# Put the data in the window
		###############################################
		self.display_accounts()

	def create_top_level(self, title):
		"""Create the top level window."""
		win = tk.Toplevel()
		win.title(title)
		win.protocol("WM_DELETE_WINDOW", self.cancel_win)
		return win

	@staticmethod
	def add_filter_frame(parent):
		"""Add a frame to the window.The frame will get filter combobuttons."""

		return local_util.add_label_frame(parent, "Selection Criteria:",
										  style="Padded5Ridge.TLabelframe")

	def add_filter_widgets(self, filter_frame):
		"""Add the filter widgets(combobuttons) to the filter frame.

		Filters are used to limit the data shown in the window."""

		col = 0
		row = 0
		fwl = []
		for idx, widget in enumerate(self.filters):
			if widget['type'] == 'combo':
				lab = ttk.Label(filter_frame,
								style='Padded.TLabel',
								text=widget['label'])
				lab.grid(row=row, column=col)
				col += 1
				cb = ttk.Combobox(filter_frame,
								  width=widget['width'],
								  values=widget['set'])
				cb.bind('<<ComboboxSelected>>',
						self.filter_modified)
				cb.current(0)
				cb.grid(row=row, column=col)
				fwl.append(cb)
				col += 1
		return fwl

	def bind_heading_widgets(self, widgets, column_descriptor):
		for col, column in enumerate(column_descriptor):
			widgets[col].config(
					command=lambda k=column['key']: self.sort_request(k))

	def add_control_buttons(self, parent):
		"""Add the Cancel, Update,... buttons to the control frame."""

		cancel_butt = ttk.Button(parent, text='Cancel',
								 style='Medium.TButton',
								 command=self.cancel_win)
		cancel_butt.pack(side=tk.RIGHT)

		update_butt = ttk.Button(parent, text='Update',
								 style='Medium.TButton',
								 command=self.close_and_update_win)
		update_butt.pack(side=tk.RIGHT)

		new_butt = ttk.Button(parent, text='New',
							  style='Medium.TButton',
							  command=self.new_instrument)
		new_butt.pack(side=tk.RIGHT)

		if self.instrument_type == "bond":
			import_butt = ttk.Button(parent, text='Import Bonds',
									 style='Medium.TButton',
									 command=self.import_bonds)
			import_butt.pack(side=tk.RIGHT)

		"""if self.instrument_type == "accounts":   todo - what is this for ??
		
			import_butt = ttk.Button(parent, text='Import Accounts',
									 style='Medium.TButton',
									 command=self.import_accounts)
			import_butt.pack(side=tk.RIGHT)
		"""

	def create_account_widgets(self, frame, column_descriptor):
		"""Create all the widgets necessary to present the account info.

		The member 'account_widgets' is a list of lists. Each entry
		in the list represents an item in the account list. That entry is also
		a list of all the widgets necessary to present that account entry.
		"""

		account_widgets = []
		for rec in self.data_source:
			widget_list = create_widget_row(frame, rec, column_descriptor,
											self.tracking_end_date)
			account_widgets.append(widget_list)

		return account_widgets

	def bind_account_widgets(self, account_widgets, column_descriptor):
		"""This method will bind all account frame widgets to actions.

		Widget creation is separate from widget binding. This allows
		portions of the code to be reused

		This method assumes id's in records correspond to rows in the
		account_widget list.
		"""

		for id_, row in enumerate(account_widgets):
			self.bind_widget_row(id_, row, column_descriptor)

	def bind_widget_row(self, rec_id, widget_row, column_descriptor):
		"""This method will bind the widgets in a single_row to actions.

		This method binds the "action menu" to all widgets in the row.
		It also binds functions to datepickers and checkbuttons widgets.
		"""

		for col, column in enumerate(column_descriptor):
			if column["type"] == "date":
				if column["content"] == "standard":
					widget_row[col].configure(command=lambda col=col, id_=rec_id:
											  self.open_datepicker(col, id_))
				elif column["content"] == "latest":
					widget_row[col].configure(command=lambda col=col, id_=rec_id:
											  self.open_occurrence_win(col, id_))
				elif column["content"] == "regularity":
					widget_row[col].configure(command=lambda col=col, id_=rec_id:
											  self.open_occurrence_win(col, id_))
				else:
					raise TypeError("Unknown date content: {}".format(
							column["content"]))

			elif column["type"] == "checkbutton":
				if column["content"] == "call":
					widget_row[col].configure(command=lambda col=col, id_=rec_id:
											  self.open_bond_call(col, id_))
			# all widgets get bound to menu_on_item()
			widget_row[col].bind('<ButtonRelease-3>',
								 lambda event, id_=rec_id: self.menu_on_item(id_))

	def find_call_button(self):
		"""Utility function: scan the column descriptor to find call button."""

		for col, column in enumerate(self.column_descriptor):
			if column["type"] == "checkbutton":
				if column["content"] == "call":
					return col
		raise TypeError("No bond call button")

	def display_accounts(self):
		"""Update the content of the main display frame.

		This method is responsible display of the account data.
		This includes adding widgets to the account_frame and
		scroll_frame.

		Any filters defined are executed and the primary and secondary
		sort keys are applied.

		This method is called for paging support because the paging
		buttons in the control_frame change with paging

		This method is called for filtering support because the size
		of the frame can change with filtering
		"""

		###############################################
		# Filter and sort the data
		###############################################
		self.filter_data()

		self.display_data.sort(key=itemgetter(self.primary_sort_key,
											  self.secondary_sort_key))
		###############################################
		# Fill the Account Data Frame
		###############################################
		self.remove_account_widgets()  # remove the old
		self.add_account_widgets()  # add the new that define account content

		########################
		# frame for page number
		########################
		if len(self.display_data) >= self.entries_to_display:
			page = math.ceil(
					(self.first_entry_to_display / self.entries_to_display)) + 1
			pages = math.ceil(len(self.display_data) / self.entries_to_display)
			self.page_label = ttk.Label(self.page_frame,
										text="Page: {} of {}".format(
												page, pages))
			self.page_label.grid(row=0, column=0)
		else:
			# no need for a page number
			for label in self.page_frame.grid_slaves():
				label.grid_forget()

		########################
		# update the scroll frame
		########################
		for widget in self.scroll_frame.grid_slaves():
			widget.grid_forget()

		if self.first_entry_to_display > 0:
			back_butt = ttk.Button(self.scroll_frame, text='<<',
								   style='Medium.TButton',
								   command=self.page_back)

			back_butt.grid(row=0, column=2)
		if self.first_entry_to_display + self.entries_to_display < \
				len(self.display_data):
			fwd_butt = ttk.Button(self.scroll_frame, text='>>',
								  style='Medium.TButton',
								  command=self.page_fwd)
			fwd_butt.grid(row=0, column=3)

		###############################################
		# Center the pop up
		###############################################
		util.center_popup(self.win, self.parent.get_root())

	def add_account_widgets(self):
		"""This method will add sorted data/filtered data to the display.

		This method populates the account frame based on paging
		and current filters.
		Display_data[] holds the records we want to display but they
		are not necessarily sequential. Each records has an id
		which is used to find the widgets that were created to
		hold/present its data.

		Note: [first:last] will only go to the end of the list even
		if last is beyond the end of the list
		"""

		# Only display a page worth
		first = self.first_entry_to_display
		last = self.first_entry_to_display + self.entries_to_display

		row = 1
		for rec in self.display_data[first:last]:
			widget_row = self.account_widgets[rec['id']]
			col = 0
			for i in range(len(widget_row)):
				widget_row[i].grid(row=row, column=col)
				col += 1
			row += 1

	def remove_account_widgets(self):
		"""Remove all account widgets currently in the account frame."""

		for widget in self.account_frame.grid_slaves():
			if int(widget.grid_info()["row"]) > 0:  # leave the column headings
				widget.grid_forget()

	def page_back(self):
		"""Page backward through the account data"""

		if self.first_entry_to_display < self.entries_to_display:
			self.first_entry_to_display = 0
		else:
			self.first_entry_to_display = \
				((self.first_entry_to_display - 2) // self.entries_to_display) * \
				self.entries_to_display

		self.display_accounts()

	def page_fwd(self):
		"""Page forward through the account data.

		If we get to the end, redisplay some from the previous page.
		We want all displayed pages to be the same length.
		"""

		self.first_entry_to_display += self.entries_to_display

		if self.first_entry_to_display + self.entries_to_display >= \
				len(self.display_data):
			self.first_entry_to_display = len(self.display_data) - \
										  self.entries_to_display

		self.display_accounts()

	def sort_request(self, key):
		"""The user has depressed a button, triggering a sort.

		Use the new key to adjust the previous sort order.
		The display_accounts() will execute the sort"""

		self.secondary_sort_key = self.primary_sort_key
		self.primary_sort_key = key

		self.display_accounts()

	def filter_modified(self, _):
		"""The user has changed a filter  selection in the filter frame

		Implementation detail: The '_' in the argument list the
		'ignore-by-convention' indicator. I'm ignoring the 'event' argument
		which pylint was flagging
		"""

		# Interaction with paging requires we reset the paging control.
		self.first_entry_to_display = 0

		self.display_accounts()

	def filter_data(self):
		"""Handle request to filter account data

		This method gets called when the user performs an action which
		requires redisplay of the user data. These include actions in the
		filter frame, adding a new instrument,...

		Clear out the display data and add each record in if it passes
		all the filters.
		"""

		self.display_data.clear()

		if self.filters:
			for rec in self.data_source:
				match = True  # assume the records passes all filters
				for idx, filter_definition in enumerate(self.filters):
					filter_func = filter_definition['function']
					if not filter_func(self.filter_widgets[idx].get(), rec):
						match = False
						break
				if match:
					self.display_data.append(rec)
		else:
			for rec in self.data_source:
				self.display_data.append(rec)

	def menu_on_item(self, id_):
		"""The user may open a menu on an item in the account data area.

		This method invokes a class to handle the menu request.
		"""

		if not self.actions_menu:
			# ##################################################################
			# Update the data in data_source to reflect the current content of
			# the widget. This is done so that any actions performed on the
			# instrument have latest data provided by the user (e.g user changes
			# inflation and wants to see the transfer schedule)
			# ##################################################################
			update_rec_from_widgets(self.data_source[id_],
													 self.column_descriptor,
													 self.account_widgets[id_],
													 self.instrument_type)
			# TODO  I think this needs to be adjusted for paging
			self.actions_menu = ActionsOnInstrument(self,         # AccountEditWin Class
													self.parent,  # GUI
													self.win,     # Top Level EditWin
													self.data_source,
													id_,  # record id
													self.instrument_type)

	def action_menu_closed(self):
		"""The action menu reports closing"""

		self.actions_menu = None

	def mark_as_deleted(self, rec_id, delete_flag):
		"""User has decided to delete an entry

		When the user decides to delete(/undelete) an entry, we change
		the color of the entry to all red and set the delete checkbutton.
		Note that the checkbutton is not displayed to the user.
		"""

		for col in range(len(self.column_descriptor)):
			if delete_flag:
				self.account_widgets[rec_id][col].config(state=tk.DISABLED)
			else:
				self.account_widgets[rec_id][col].config(state=tk.NORMAL)

	def cancel_win(self):
		"""User has depressed the Cancel button"""

		self.close_subordinate_windows()

		self.clean_data_source()

		# inform the calling class we have closed the window
		self.menu_bar.edit_window_closed(self.instrument_type)

		self.win.destroy()

	def close_subordinate_windows(self):
		"""Close any other windows that may be open.

		This can include bond call and new instrument windows."""

		for bond_call_obj in self.bond_call_windows:
			bond_call_obj.kill_win()

		for new_instrument_obj in self.new_instrument_windows:
			new_instrument_obj.kill_win()

		for key, datepicker_obj in self.datepicker_windows.items():
			datepicker_obj.kill_win()

		for key, occurrence_obj in self.occurrence_windows.items():
			occurrence_obj.kill_win()

		if self.actions_menu:
			self.actions_menu.cancel_win()

	def clean_data_source(self):
		"""To simplify processing, some additional keys were added to
		the records. They need to be removed before the records is written."""

		for rec in self.data_source:
			self.clean_data_rec(rec)

	def clean_data_rec(self, rec):
		if 'id' in rec:
			del rec['id']
		if 'deleteKey' in rec:
			del rec['deleteKey']
		if 'newRecKey' in rec:
			del rec['newRecKey']
		if 'accNameChangedKey' in rec:
			del rec['accNameChangedKey']

	def close_and_update_win(self):
		"""Close the Account Edit window.

		This method updates each record in the data source per user input
		then validates each field if the user has provided a validation
		function.

		If the validation fails, an error message will be presented
		and this method will return. The user must fix the error before
		continuing.

		If there are no validation errors, this method will close the
		account edit window and write the results to the internal dictionary
		and to the disk file.

		If the record is marked for deletion, exclude it from the update.

		If the account list is being edited and an account is being
		deleted, the parent will be informed.
		(The parent is responsible for deleting associated records.
		For example, the associated cash account will be deleted. If the
		account holds bonds, CDs, etc, those records will also be deleted.
		Remember that the data source in this method is only for the
		instrument being edited. (e.g. bond, CDs,...) This method does not
		have direct access to other parts of the data file).

		If the account list is being edited and a new account is being added,
		the parent will be informed. (The parent is responsible for adding
		any associated records such as the cash account record).
		"""
		self.close_subordinate_windows()  # just in case...

		for r_num, rec in enumerate(self.data_source):
			update_rec_from_widgets(rec, self.column_descriptor, self.account_widgets[r_num], self.instrument_type)
			if self.validate_func:
				msg = self.validate_func(rec, self.column_descriptor)
				if msg != "":
					messagebox.showerror("Data Error", msg)
					return

		# Prevent multiple new records with the same account name
		account_name = []
		for rec in self.data_source:
			if rec['account'] not in account_name:
				account_name.append(rec['account'])
			else:
				messagebox.showerror("Data Error",
									 "Account Name \'{}\' is used more than once. ".\
									 format(rec['account']) +\
									 "Each account name must be unique!")
				return
		# Deal with special record changes:
		#  . new record in the account list - inform the parent
		#  . modified account_name in the account list - inform parent
		#  . deleted record - exclude it from the data source
		#                   - if its a record from the account list
		#                     (ie an account is being deleted) inform the parent

		new_accounts = []
		for rec in reversed(self.data_source):
			if 'deleteKey' in rec and not 'newRec' in rec:
				if self.instrument_type == 'account':
					# inform the parent an account has been deleted
					self.parent.account_delete(rec['account'])
				self.data_source.remove(rec)
			elif 'newRecKey' in rec and self.instrument_type == 'account' and not 'deleteKey'in rec:
				self.clean_data_rec(rec)
				self.parent.account_create(rec)
				new_accounts.append({'account':rec['account'], 'account_id':rec['account_id']})
			elif 'accNameChangedKey' in rec:
				self.parent.account_name_changed(rec['accNameChangedKey'], # old name
				                                rec['account'] )           # new name
		self.clean_data_source()

		# replace the official data source with the modified
		self.data_source_orig.clear()
		for entry in self.data_source:
			self.data_source_orig.append(entry)

		self.parent.fm.write_data_file()
		# Updated account data - restart everything
		self.parent.restart()

		# inform the calling class we have closed the window
		self.menu_bar.edit_window_closed(self.instrument_type, new_accounts)

		self.win.destroy()

	def new_instrument(self):
		"""User has depressed the "New" button.

		The user would like to create a new financial instrument.
		of the type currently displayed in the account_edit window.
		"""
		# keep track of all open NewInstrument windows
		if self.instrument_type == 'ca':
			messagebox.showerror("Create Error",
								 "The cash account can not be directly created. Creating an Account will create the assoicated cash account!")
			return

		self.new_instrument_windows.append(
				NewInstrument(self, self.win, self.title,
							  self.column_descriptor,
							  self.get_new_rec(),     # empty record
							  self.instrument_type))

	def new_instrument_closed(self, new_instrument_obj, new_rec):
		"""The New Instrument window has closed.

		Assign a rec_id to it and redisplay the account.
		Also add a key to identify this as a new record. (New records
		that ultimately get accepted may get special treatment. For
		example, a new account will genertate a new cash account)
		"""

		# remove the new instrument window from the list of open window
		self.new_instrument_windows.remove(new_instrument_obj)

		if new_rec:
			new_rec['id'] = self.next_id
			new_rec['newRecKey'] = 1
			self.next_id += 1
			self.data_source.append(new_rec)
			# generate a new row of widgets
			widget_row = create_widget_row(self.account_frame,
										   new_rec,
										   self.column_descriptor,
										   self.tracking_end_date)
			self.account_widgets.append(widget_row)

			# bind the new widget row to functions
			self.bind_widget_row(new_rec['id'], widget_row,
								 self.column_descriptor)
			self.display_accounts()

	def open_datepicker(self, col, id_):
		"""Open a date picker so the user can select a alternate date"""

		token = (id_, col)
		if token not in self.datepicker_windows.keys():
			# Use the date currently in the box
			day = self.account_widgets[id_][col].cget('text')

			# create and add the datePicker to the list of open datepickers
			self.datepicker_windows[token] = DatePicker(
					self,  # caller
					token,  # opaque data
					date=datetime.strptime(day, dfc.DATE_FORMAT),
					title=self.column_descriptor[col]["heading"],
					parent_win=self.win)

	def DatePicker_return(self, date, token):
		# This method is required by the datepicker
		"""User has closed a datepicker window."""

		if token in self.datepicker_windows.keys():
			del self.datepicker_windows[token]

			if date:
				id_ = token[0]
				col = token[1]
				self.account_widgets[id_][col].configure(
						text=date.strftime(dfc.DATE_FORMAT))
		else:
			raise TypeError("Unknown datepicker Token :{}".format(token))

	def open_occurrence_win(self, col, id_):
		"""Open an occurrence window so the user can specify occurrences."""

		token = (id_, col)
		if token not in self.occurrence_windows.keys():
			spec = self.data_source[id_][self.column_descriptor[col]['key']]

			# create and add the occurrence win to the list of open windows
			self.occurrence_windows[token] = OccurrenceWin(
					self,             # caller
					"Occurrences",    # title
					spec,             # occurrence spec
					self.tracking_end_date,  # last date
					token,            # opaque data
					master=self.win)  # for centering

	def OccurrenceWin_return(self, occurrence_spec, token):
		# This method is required by OccurrenceWin
		"""User has closed a Occurrence window."""

		if token in self.occurrence_windows.keys():
			del self.occurrence_windows[token]

			if occurrence_spec != "":
				id_ = token[0]
				col = token[1]

				# writing data updates back to the source record usually
				# occurs on close. Occurrences are an exception since the
				# widgets involved don't hold an occurrence.
				self.data_source[id_][self.column_descriptor[col]['key']] = \
					occurrence_spec
				# Update any boxes in the display as needed
				occ = Occurrences(occurrence_spec, self.tracking_end_date)
				for col, column in enumerate(self.column_descriptor):
					if column['type'] == 'date':
						if column['content'] == 'latest':
							text = occ.get_latest_date().strftime(dfc.DATE_FORMAT)
						elif column['content'] == 'regularity':
							text = occ.get_modified_regularity()
						else:
							raise TypeError("Unknown content: {}".format(
									column['content']))
						self.account_widgets[id_][col].configure(text=text)
		else:
			raise TypeError("Unknown occurrence win:{}".format(token))

	def open_bond_call(self, col, id_):
		"""Open a window to record a bond call.

		The user clicked on the checkbutton but we don't
		want that to change the state of the button. Toggle
		the state back to where it was and we will fix it
		when the user closes the BondCall window.
		"""
		self.account_widgets[id_][col].toggle()
		# keep track of all open BondCall windows
		self.bond_call_windows.append(
				BondCall(self, self.win, self.data_source[id_], col, id_))

	def bond_call_closed(self, bond_call_obj, bond_called_f, col, rec_id):
		"""User has closed a bond call window.

		Remove the bond_call obj from the list of open windows and report
		the window closed to the caller."""

		self.bond_call_windows.remove(bond_call_obj)

		# update the state of the call checkbutton
		if bond_called_f:
			self.account_widgets[rec_id][col].select()
		else:
			self.account_widgets[rec_id][col].deselect()

	def import_bonds(self):
		"""The user has request the import of bonds data.

		Read in a file containing a list of bonds from a brokerage export.

		For now, only support Fidelity imports. In the future, a popup
		could appear selecting the brokerage house.  The house determines
		the format of the file.

		The Fidelity bond record contains several fields I collect when
		creating a new bond record and several other informational fields.
		The informational fields are taken as is and added to the record.

		The fields in the imported record that may already be in the bond
		record include:

		1. issuer - ignore if the bond record already has an issuer

		For new bonds in the imported set, the following required data
		is not in the imported record.

		1. bond_price
		2. compounding
		3. settlement date
		4. fee
		"""

		import_helper = ImportFidelityBondList(self.parent.get_account_id_map())

		####################################################
		# File manager will open the file. The import_helper
		# will read in the contents and generate a set of
		# records in the standard CF bond format
		####################################################
		self.parent.get_file_manager().open_bond_list(
				import_helper.process_bond_list)

		imported_records = import_helper.get_bond_records()

		# ############################################a
		# The bonds from Fidelity may already be in the
		# cf application or they may be new. Make that
		# determination based on the cusip.
		# ############################################a
		# TODO - how will this work if i have multiple instances
		#  in the same account for the same issue?
		for imported_rec in imported_records:
			found = False
			for rec in self.data_source:
				if imported_rec['cusip'] == rec['cusip'] and \
						imported_rec['account'] == rec['account']:
					#########################################
					# We already have this bond on record.
					# Update the associated record and widget.
					#########################################
					col = get_column_num_by_key(self.column_descriptor, 'issuer')
					if self.account_widgets[rec['id']][col].get() == "":
						self.account_widgets[rec['id']][col].delete(0, tk.END)
						self.account_widgets[rec['id']][col].insert(
								0, imported_rec['issuer'])

					rec['most_recent_price'] = imported_rec['most_recent_price']
					rec['moodys_rating'] = imported_rec['moodys_rating']
					rec['product_type'] = imported_rec['product_type']
					rec['s&p_rating'] = imported_rec['s&p_rating']
					rec['most_recent_value'] = imported_rec['most_recent_value']
					rec['quantity'] = imported_rec['quantity']
					rec['next_call_date'] = imported_rec['next_call_date']
					rec['est_yield'] = imported_rec['est_yield']

					found = True
					break
			if not found:
				rec = self.get_new_rec()

				# copy all imported data to new rec
				for key in imported_rec.keys():
					rec[key] = imported_rec[key]

				# keep track of all open NewInstrument windows
				self.new_instrument_windows.append(
						NewInstrument(self, self.win, self.title,
									  self.column_descriptor, rec, "bond"
									  ))

		self.display_accounts()

	"""
	def import_accounts(self):
		The user has request the import ... data.
	
		pass
	"""
	def get_new_rec(self):
		return self.parent.get_new_rec(self.instrument_type)


class ActionsOnInstrument:
	"""Right click to open a menu for an item in the account frame.

	The actions available depend on the type of instrument. For example,
	you can "call a bond" from the actions menu, can delete an
	account"""

	def __init__(self, accnt_edit, parent, accnt_edit_win,
				 data_source, id_, instrument_type):
		self.account_edit = accnt_edit         # AccEditWin Class
		self.parent = parent                   # GUI
		self.parent_win = accnt_edit_win       # top level Edit window
		self.data_source = data_source
		self.id = id_
		self.instrument_type = instrument_type

		# TODO need to add fund to this list

		description_dict = {'account':"Account", 'ca': 'Cash Account', 'bond': 'Bond CUSIP',
							'cd': 'Certificate of Deposit', 'loan': 'Loan', 'fund':'Fund Name',
							'transfer':'Transfer'}
		description = description_dict[instrument_type]

		################################################
		# Record to operate on
		################################################
		record = self.data_source[self.id]

		################################################
		# Prep text based on account type
		################################################
		if 'deleteKey' in record:
			delete_text = 'Undelete'
		else:
			delete_text = 'Delete'

		cash_flow_details_text = 'Details'
		details_text = 'Details'
		analysis_text = 'Analysis'
		call_text = ''

		if instrument_type == 'account':
			title = "{}:   {}".format(description, record['account'])
			delete_text += " account"
		elif instrument_type == 'ca':
			title = "{}:   {}".format(description, record['account'])
			delete_text += " cash account"
		elif instrument_type == 'bond':
			title = "{}: {}".format(description, record['cusip'])
			delete_text += " bond record"
			cash_flow_details_text = 'Bond Cash Flow Details '
			details_text = 'Bond Details '
			call_text += 'Bond Call'
		elif instrument_type == 'fund':
			title = "{}:  {}".format(description, record['fund'])
			delete_text += " fund record"
		elif instrument_type == 'cd':
			title = "{}: {}".format(description, record['cusip'])
			delete_text += " CD record"
			cash_flow_details_text = 'CD Cash Flow Details'
		elif instrument_type == 'loan':
			title = "{}: {}".format(description, record['note'])
			delete_text += " loan record"
		elif instrument_type == 'transfer':
			title = "{}: {}".format(description, record['note'])
			delete_text += " transfer request"
			amounts_text = " Transfer Schedule"
		else:
			raise TypeError("Unknown Instrument Type:{}".format(
					instrument_type))

		################################################
		# Construct the pop up menu
		################################################
		self.action_win = tk.Toplevel(bg='White', bd=2, relief='raised')

		self.actions_frame = local_util.add_borderless_frame(
				self.action_win, style='White.TFrame')
		r = 0
		# Header (top line)
		label = ttk.Label(self.actions_frame, text=title,
						  style='Borderless.TLabel')
		label.grid(row=r, column=0, sticky='WE')
		r += 1
		sep = ttk.Separator(self.actions_frame, orient='horizontal')
		sep.grid(row=r, column=0, sticky='EW')
		r += 1

		if instrument_type == 'bond' or instrument_type == 'cd':
			if platform.system() == 'Linux':
				cf_details_butt = ttk.Button(self.actions_frame,
											 text=cash_flow_details_text,
											 style='Borderless.TButton',
											 command=self.cf_details)
			else:
				cf_details_butt = tk.Button(self.actions_frame,
											text=cash_flow_details_text,
											background='white',
											borderwidth=0,
											command=self.cf_details)
			cf_details_butt.grid(row=r, column=0, sticky='W')
			r += 1

		if instrument_type == 'bond':
			if platform.system() == 'Linux':
				details_butt = ttk.Button(self.actions_frame,
										  text=details_text,
										  style='Borderless.TButton',
										  command=self.details)
			else:
				details_butt = tk.Button(self.actions_frame,
										 text=details_text,
										 background='white',
										 borderwidth=0,
										 command=self.details)
			details_butt.grid(row=r, column=0, sticky='W')
			r += 1

		if instrument_type == 'bond':
			if platform.system() == 'Linux':
				anal_butt = ttk.Button(self.actions_frame, text=analysis_text,
									   style='Borderless.TButton',
									   command=self.analysis)
			else:
				anal_butt = tk.Button(self.actions_frame, text=analysis_text,
									  background='white',
									  borderwidth=0,
									  command=self.analysis)
			anal_butt.grid(row=r, column=0, sticky='W')
			r += 1

			if platform.system() == 'Linux':
				call_butt = ttk.Button(self.actions_frame, text=call_text,
									   style='Borderless.TButton',
									   command=self.bond_call)
			else:
				call_butt = tk.Button(self.actions_frame, text=call_text,
									  background='white',
									  borderwidth=0,
									  command=self.bond_call)
			call_butt.grid(row=r, column=0, sticky='W')
			r += 1
		if instrument_type == 'transfer':
			if platform.system() == 'Linux':
				amounts_butt = ttk.Button(self.actions_frame, text=amounts_text,
				                          style='Borderless.TButton',
										  command=self.get_inflated_amounts)
			else:
				amounts_butt = tk.Button(self.actions_frame, text=amounts_text,
										 background='white',
									     borderwidth=0,
									     command=self.get_inflated_amounts)
			amounts_butt.grid(row=r, column=0, sticky='W')
			r += 1

		if platform.system() == 'Linux':
			del_butt = ttk.Button(self.actions_frame, text=delete_text,
								  style='Borderless.TButton',
								  command=self.delete_item)
		else:
			del_butt = tk.Button(self.actions_frame, text=delete_text,
								 background='white',
								 borderwidth=0,
								 command=self.delete_item)

		del_butt.grid(row=r, column=0, sticky='W')
		r += 1

		if platform.system() == 'Linux':
			cancel_butt = ttk.Button(self.actions_frame, text='Cancel',
									 style='Borderless.TButton',
									 command=self.cancel_win)
		else:
			cancel_butt = tk.Button(self.actions_frame, text='Cancel',
									background='white',
									borderwidth=0,
									command=self.cancel_win)
		cancel_butt.grid(row=r, column=0, sticky='W')
		r += 1

		# The following are some differences between windows and Linux
		if platform.system() != 'Linux':
			self.action_win.update_idletasks()
		else:
			# Make the actions window collapse when the parent collapses
			# Under windows this does not have the desired effect; the
			# Actions window gets closed but does not reappear when the
			# AccountEdit window is reopened.
			# For Windows, we'll just leave it up and the user will
			# have to close it
			self.action_win.transient(accnt_edit_win)

		# remove the window dressing
		self.action_win.overrideredirect(True)
		# the following is an x11 hack and only works for Linux
		# self.action_win.wm_attributes('-type', 'splash')
		util.center_popup(self.action_win, accnt_edit_win)

	def cancel_win(self):
		self.close_actions_win()

	def delete_item(self):
		if self.instrument_type == 'ca':
			self.close_actions_win()
			messagebox.showerror("Delete Error",
								 "The cash account can not be directly deleted. "\
								  "Deleting the Account will delete the assoicated cash account!")
			return
		if 'deleteKey' in self.data_source[self.id]:
			# Undelete it
			del self.data_source[self.id]['deleteKey']           # remove the deleteKey from the record
			self.account_edit.mark_as_deleted(self.id, False)
		else:
			self.data_source[self.id]['deleteKey'] = 1
			self.account_edit.mark_as_deleted(self.id, True)

		self.close_actions_win()

	def analysis(self):
		# fix me - need to finish this
		self.close_actions_win()

	def cf_details(self):
		"""The user has requested cash flow details of an instrument
		(eg a bond or CD)
		"""

		if self.instrument_type == 'bond':
			details = self.parent.get_bond_cash_flow(self.data_source[self.id])

			self.display_bond_cf_details(self.parent, details)

		elif self.instrument_type == 'cd':
			text = "TBD..."
			ScrollableWin("CD Cash Flow Details", text, self.parent_win)

		self.close_actions_win()

	def display_bond_cf_details(self, parent, details):
		"""Display the cash flow details of a bond in a window"""

		text = 'CUSIP: {}\n\n'.format(self.data_source[self.id]['cusip'])

		text += "{} {}   {}\n".format(
				"Date".center(10),
				"Amount".rjust(12),
				"Notes".ljust(0))

		for record in details:
			text += "{:10} {:12.2f}   {:20}\n".format(
					parent.format_date(record['date']),
					record['amount'],
					record['note'])

		ScrollableWin("Bond Cash Flow Details", text, self.parent_win)

	def details(self):
		"""The user has requested details of an instrument (eg a bond)"""

		if self.instrument_type == 'bond':
			self.display_bond_details()

		self.close_actions_win()

	def display_bond_details(self):
		"""Present all we know about the bond in a text frame"""

		rec = self.data_source[self.id]

		display_data = OrderedDict()
		display_data['account'] = 'Account'
		display_data['issuer'] = 'Description'
		display_data['purchase_date'] = 'Settlement Date'
		display_data['maturity_date'] = 'Maturity'
		display_data['bond_price'] = 'Purchase Price'
		display_data['most_recent_price'] = 'Most Recent Price'
		display_data['most_recent_value'] = 'Most Recent Value'
		display_data['quantity'] = 'Quantity'
		display_data['coupon'] = 'Coupon'
		display_data['est_yield'] = 'Estimated Yield'
		display_data['frequency'] = 'Pay Frequency'
		display_data['fee'] = 'Fees'
		display_data['moodys_rating'] = "Moody's Rating"
		display_data['s&p_rating'] = 'S&P Rating'
		display_data['next_call_date'] = 'Call Date'
		display_data['product_type'] = 'Product Type'

		text = "CUSIP: {}\n\n".format(rec['cusip'])
		for key in display_data.keys():
			text += "{:18} : {}\n".format(display_data[key], rec[key])
		ScrollableWin("Bond Details", text, self.parent_win)

	def bond_call(self):
		"""User has selected the Bond Call action"""

		# Determine which column holds the call checkbutton. BondCall
		# needs this to possibly change the state of the check
		col = self.account_edit.find_call_button()

		# TODO - check with the account_edit object to see if BondCall
		# window already opened for this cusip

		# inform the AccountEdit object we have opened a Bond Call window
		self.account_edit.bond_call_windows.append(
				BondCall(self.account_edit, self.parent_win,
						 self.data_source[self.id], col, self.id))

		self.close_actions_win()

	def get_inflated_amounts(self):
		"""Get a list of transfer amounts associated with the current record.
		   Inflate the amounts based on the inflation factor.
	       Use the dates specified in the current record.
	    """
		transfer_spec = self.data_source[self.id]

		end_date = self.parent.get_tracking_end_date()  # todo - take this out
		end_date = self.account_edit.tracking_end_date
		occ = Occurrences(transfer_spec['frequency'], end_date)
		dates = occ.get_dates()
		current_year = dates[0].year

		amounts = self.parent.get_inflated_amounts(transfer_spec['amount'], transfer_spec['inflation'], occ.get_dates())

		text = ""
		if len(dates) == len(amounts):
			for i, date in enumerate(dates):
				if date.year != current_year:
					text += '\n'
					current_year = date.year
				text += "{}  ".format(date.strftime(dfc.DATE_FORMAT))
				text += "${:,.2f}\n".format(amounts[i])
		else:
			text = "Error - length mismatch on dates and amounts"

		ScrollableWin("Transfer Schedule", text, self.parent_win)

		self.close_actions_win()

	def close_actions_win(self):
		# Inform the AccountEdit class we are done
		self.account_edit.action_menu_closed()
		self.action_win.destroy()


class BondCall:
	def __init__(self, parent, parent_win, bond_record, col, rec_id):
		"""Open a window for bond call processing

		Fact: when the call_price is 0, it is understood the bond
		has NOT been called.
		The Bond Call window is opened with the call_date and call_price
		from the bond record.
		If the user hits "accept", the call_date and call_price
		are written to the bond_record.
		"""

		self.parent = parent  # AccountEdit object
		self.bond_record = bond_record
		self.col = col  # col num - used for checkbutton maint
		self.rec_id = rec_id

		self.datepicker_windows = {}  # Subordinate windows

		self.win = tk.Toplevel()
		self.win.title("Bond Call")
		self.win.protocol("WM_DELETE_WINDOW", self.cancel_win)

		###########################
		# first the frame
		###########################
		self.frame = local_util.add_frame(self.win)

		col = 0
		row = 0
		###########################
		# Column Labels
		###########################
		ttk.Label(self.frame,
				  text="CUSIP",
				  width=dfc.FW_MEDSMALL,
				  style='Centered.TLabel'). \
			grid(row=row, column=col)
		col += 1
		ttk.Label(self.frame,
				  text='Call\nDate',
				  width=dfc.FW_SMALL,
				  style='Centered.TLabel'). \
			grid(row=row, column=col)
		col += 1
		ttk.Label(self.frame,
				  text='Redemption\nPrice',
				  width=dfc.FW_SMALL,
				  style='Centered.TLabel'). \
			grid(row=row, column=col)
		col = 0
		row += 1
		###########################
		# Column Content
		###########################
		# Determine what to display for the call_price and call_date
		if bond_record['call_price'] != 0.0:
			date_text = bond_record['call_date']
			price = bond_record['call_price']
		else:
			date_text = util.today_in_text()
			price = 0.0

		# Set up the display
		self.cusip = ttk.Entry(self.frame,
							   width=dfc.FW_MEDSMALL,
							   justify='left')
		self.cusip.insert(0, bond_record['cusip'])
		self.cusip.grid(row=row, column=col)
		col += 1

		self.date_butt = ttk.Button(self.frame,
									text=date_text,
									width=dfc.FW_SMALL,
									style='Thin.TButton',
									command=self.open_datepicker)
		self.date_butt.grid(row=row, column=col)
		col += 1
		self.premium_entry = ttk.Entry(self.frame,
									   width=dfc.FW_SMALL,
									   justify='right')
		self.premium_entry.insert(0, "{:,.3f}".format(price))
		self.premium_entry.grid(row=row, column=col)

		###############################################
		# Buttons Frame
		###############################################
		self.ctrl_frame = local_util.add_controls_frame(self.win)
		self.bt_frame = local_util.add_button_frame(self.ctrl_frame)

		cancel_butt = ttk.Button(self.bt_frame, text='Cancel',
								 style='Medium.TButton',
								 command=self.cancel_win)
		cancel_butt.pack(side=tk.RIGHT)

		accept_butt = ttk.Button(self.bt_frame, text='Accept',
								 style='Medium.TButton',
								 command=self.close_and_accept_change)
		accept_butt.pack(side=tk.RIGHT)

		if price != 0.0:
			# only add the Cancel_call button if the bond has been called
			cancel_call_butt = ttk.Button(self.bt_frame,
										  text='Cancel Call',
										  style='Medium.TButton',
										  command=self.cancel_call)
			cancel_call_butt.pack(side=tk.RIGHT)

		###############################################
		# Center the pop up
		###############################################
		util.center_popup(self.win, parent_win)

	def open_datepicker(self):
		"""Open a date picker so the user can select a call date"""

		token = "call date"
		if token in self.datepicker_windows.keys():
			# TODO - see if there is a way to bring the datepicker to
			# the top of the stack

			print("Already open")
		else:
			self.datepicker_windows[token] = DatePicker(
					self,  # caller
					token,  # opaque data
					date=datetime.strptime(self.date_butt.cget('text'), "%Y-%m-%d"),
					title="Call date",
					parent_win=self.win)

	def DatePicker_return(self, date, token):
		# This method is required by the datepicker
		"""User has closed a datepicker window."""

		if token in self.datepicker_windows.keys():
			del self.datepicker_windows[token]

			if date:
				self.date_butt.configure(text=date.strftime(dfc.DATE_FORMAT))
		else:
			raise TypeError("Unknown datepicker:{}".format(token))

	def close_and_accept_change(self):
		""" User hit the Accept button"""

		self.close_subordinate_windows()  # just in case...

		# collect the changes, if any
		if self.premium_entry.get() == "" or \
				float(self.premium_entry.get().replace(',', '')) == 0.0:
			# TODO - can Redemption Price be replaced by a column headings???
			messagebox.showerror("Bond Call",
								 "A Bond Call Requires a Redemption Price")
			return

		self.bond_record['call_price'] = \
			float(self.premium_entry.get().replace(',', ''))
		self.bond_record['call_date'] = self.date_butt.cget('text')

		# indicate the window closed
		self.parent.bond_call_closed(self, True, self.col, self.rec_id)

		self.win.destroy()

	def cancel_win(self):
		""" User hit the cancel window button"""

		self.close_subordinate_windows()  # just in case...

		# determine how the checkbutton should be set
		if self.bond_record['call_price'] == 0.0:
			bond_called_f = False
		else:
			bond_called_f = True

		# indicate the window closed
		self.parent.bond_call_closed(self, bond_called_f, self.col, self.rec_id)

		self.win.destroy()

	def cancel_call(self):
		""" User hit the cancel_call button"""

		# Force a clear of the call data
		self.bond_record['call_price'] = 0.0
		bond_called_f = False

		# indicate the window closed
		self.parent.bond_call_closed(self, bond_called_f, self.col, self.rec_id)

		self.win.destroy()

	def kill_win(self):
		""" Parent decided to close window"""

		self.close_subordinate_windows()  # just in case...

		# DO NOT INDICATE CLOSED to caller. it already knows
		self.win.destroy()

	def close_subordinate_windows(self):
		"""Close any other windows that may be open."""

		for key, datepicker_obj in self.datepicker_windows.items():
			datepicker_obj.kill_win()


class NewInstrument:
	def __init__(self, account_edit_obj, parent_win, title, column_descriptor, record, instrument_type):
		"""Create a new instance of an instrument.

		New is always triggered from AccountEdit, therefore the
		column_descriptor list is available.  With that we can construct
		a 'new' window which matches the Account Edit window.
		"""

		self.account_edit_obj = account_edit_obj
		self.column_descriptor = column_descriptor
		self.rec = record
		self.instrument_type = instrument_type

		self.tracking_end_date = account_edit_obj.tracking_end_date
		self.datepicker_windows = {}  # Subordinate windows
		self.occurrence_windows = {}

		###############################################
		# The window...
		###############################################
		self.win = tk.Toplevel()
		self.win.title("New " + title)
		self.win.protocol("WM_DELETE_WINDOW", self.cancel_win)

		###############################################
		# Create the Frames
		###############################################
		self.entry_frame = local_util.add_frame(self.win)
		self.control_frame = local_util.add_button_frame(self.win)

		###############################################
		# Fill the frames
		###############################################
		add_heading_widgets(self.entry_frame, column_descriptor)

		# get new record of the appropriate type
		self.widget_row = create_widget_row(self.entry_frame,
											self.rec,
											column_descriptor,
											self.tracking_end_date)
		self.add_widgets(self.widget_row)
		self.dress_widgets(self.widget_row, column_descriptor)
		self.bind_widgets(self.widget_row, column_descriptor)

		self.add_control_buttons(self.control_frame)

		###############################################
		# Center the window
		###############################################
		util.center_popup(self.win, parent_win)

	@staticmethod
	def add_widgets(widget_row):
		# add the widgets to the frame
		col = 0
		for i in range(len(widget_row)):
			widget_row[i].grid(row=1, column=col)
			col += 1

	def bind_widgets(self, widget_row, column_descriptor):
		"""This method will bind methods to widgets in the frame.

		In this frame, only datepickers get bound."""

		for col, column in enumerate(column_descriptor):
			if column["type"] == "date":
				if column["content"] == "standard":
					widget_row[col].configure(command=lambda col=col:
											  self.open_datepicker(col))
				elif column["content"] == "latest" or \
						column["content"] == "regularity":
					widget_row[col].configure(command=lambda col=col:
											  self.open_occurrence_win(col))
				else:
					raise TypeError("Unknown date content: {}".format(
							column["content"]))

	@staticmethod
	def dress_widgets(widget_row, column_descriptor):
		"""Make the widgets look more attractive.

		If the data fields are not provided (ie empty), aAdd today's
		date to date pickers.

		"""
		for col, column in enumerate(column_descriptor):
			if column["type"] == "date":
				if widget_row[col].cget("text") == "":
					widget_row[col].configure(text=util.today_in_text())

	def add_control_buttons(self, frame):
		"""Add the control buttons (Cancel, Add) to the control frame."""

		cancel_butt = ttk.Button(frame, text='Cancel',
								 style='Medium.TButton',
								 command=self.cancel_win)
		cancel_butt.pack(side=tk.RIGHT)

		add_butt = ttk.Button(frame, text='Add',
							  style='Medium.TButton',
							  command=self.close_and_update_win)
		add_butt.pack(side=tk.RIGHT)

	def open_datepicker(self, col):
		"""User has clicked on a datepicker button. Open a date picker."""

		if col in self.datepicker_windows.keys():
			# TODO - bring the datepicker to the top
			print("Already open")
		else:
			self.datepicker_windows[col] = DatePicker(
					self,  # caller
					col,  # opaque data
					title=self.column_descriptor[col]["heading"],
					parent_win=self.win)

	def DatePicker_return(self, date, col):
		# This method is required by the datepicker
		"""User has closed a datepicker window."""

		if col in self.datepicker_windows.keys():
			del self.datepicker_windows[col]

			if date:
				self.widget_row[col].configure(text=date.strftime(
						dfc.DATE_FORMAT))
		else:
			raise TypeError("Unknown datepicker:{}".format(col))

	def open_occurrence_win(self, col):
		"""The user has clicked on an item that defines an occurrence type"""

		token = col
		if token not in self.occurrence_windows.keys():
			spec = self.rec[self.column_descriptor[col]['key']]

			# create and add the occurrence win to the list of open windows
			self.occurrence_windows[token] = OccurrenceWin(
					self,  # caller
					"Occurrences",  # title
					spec,  # occurrence spec
					self.tracking_end_date,  # last date
					token,  # opaque data
					master=self.win)  # for centering

	def OccurrenceWin_return(self, occurrence_spec, token):
		# This method is required by OccurrenceWin
		"""User has closed a Occurrence window."""

		if token in self.occurrence_windows.keys():
			del self.occurrence_windows[token]

			if occurrence_spec != "":
				col = token

				self.rec[self.column_descriptor[col]['key']] = occurrence_spec
				# Update any boxes in the display as needed
				occ = Occurrences(occurrence_spec, self.tracking_end_date)
				for col, column in enumerate(self.column_descriptor):
					if column['type'] == 'date':
						if column['content'] == 'latest':
							text = occ.get_latest_date().strftime(dfc.DATE_FORMAT)
						elif column['content'] == 'regularity':
							text = occ.get_modified_regularity()
						else:
							raise TypeError("Unknown content: {}".format(
									column['content']))
						self.widget_row[col].configure(text=text)
		else:
			raise TypeError("Unknown occurrence win:{}".format(token))

	def close_and_update_win(self):
		"""User has selected to Add the instrument to the account.

		Create the new record from the user entry and return it
		to the caller.
		"""

		self.close_subordinate_windows()  # just in case...

		update_rec_from_widgets(self.rec, self.column_descriptor, self.widget_row, self.instrument_type)

		# Return the new record and signal complete
		self.account_edit_obj.new_instrument_closed(self, self.rec)

		self.win.destroy()

	def cancel_win(self):
		"""User has decided to Cancel. Close up and signal caller"""
		self.close_subordinate_windows()  # just in case...

		self.account_edit_obj.new_instrument_closed(self, None)
		self.win.destroy()

	def close_subordinate_windows(self):
		"""Close any other windows that may be open.

		This could include datepicker windows."""

		for key, datepicker_obj in self.datepicker_windows.items():
			datepicker_obj.kill_win()

		for key, occurrence_obj in self.occurrence_windows.items():
			occurrence_obj.kill_win()

	def kill_win(self):
		"""Calling object has decided to cancel request."""

		self.close_subordinate_windows()  # just in case...

		# DO NOT INDICATE CLOSED to caller. it already knows
		self.win.destroy()


# ===========Support functions used by multiple classes ========================

def add_heading_widgets(parent, column_descriptor):
	"""Create a row of heading widgets given a column description."""

	headings = []

	for col, column in enumerate(column_descriptor):
		headings.append(ttk.Button(parent,
								   text=column["heading"],
								   width=column["width"],
								   style='Centered.TLabel'))
		headings[-1].grid(row=0, column=col, sticky='wens')
		col += 1
	return headings


def create_widget_row(frame, rec, column_descriptor, tracking_end_date):
	"""Create a row of widgets for the given rec."""

	widget_list = []
	for col, column in enumerate(column_descriptor):
		w = column["width"]
		if column["type"] == 'text':
			widget_list.append(ttk.Label(frame,
										 text=rec[column['key']],
										 width=w,
										 style=column['content']))
		elif column["type"] == "entry":
			# format text prior to inserting
			fmt = column["content"]
			text = rec[column['key']]
			if fmt == 'dollars':
				text = "{:,.2f}".format(float(text))
				justify = 'right'
			elif fmt == 'price' or fmt == 'rate':
				text = "{:,.3f}".format(float(text))
				justify = 'right'
			elif fmt == 'text' or fmt == 'cusip':
				justify = 'left'
			elif fmt == 'quantity':
				text = "{:d}".format(int(text))
				justify = 'right'
			else:
				raise TypeError("Unknown entry format:{}".format(fmt))
			widget_list.append(ttk.Entry(frame,
										 width=w,
										 style='Special.TEntry',
										 justify=justify))
			widget_list[-1].insert(0, text)
		elif column["type"] == "combo":
			widget_list.append(ttk.Combobox(frame,
											style='Special.TCombobox',
											width=w))
			widget_list[-1]['values'] = column["content"]
			widget_list[-1].set(rec[column['key']])
			widget_list[-1].configure(state="readonly")
		elif column["type"] == "date":
			if column['content'] == 'standard':
				text = rec[column['key']]
			else:
				occ = Occurrences(rec[column['key']], tracking_end_date)
				if column['content'] == 'latest':
					text = occ.get_latest_date().strftime(dfc.DATE_FORMAT)
				elif column['content'] == 'regularity':
					text = occ.get_modified_regularity()
				else:
					raise TypeError("Unknown regularity: {}".format(
							column['content']))
			widget_list.append(ttk.Button(frame,
										  text=text,
										  width=w,
										  style='Special.Thin.TButton'))
		elif column["type"] == "checkbutton":
			if column["content"] == "call":
				widget_list.append(tk.Checkbutton(frame, width=w))
				if rec[column['key']] != 0.0:
					widget_list[-1].select()
			else:
				raise TypeError("Unknown checkbutton subtype: {}".format(
						column["content"]))
		elif column["type"] == "filler":
			widget_list.append(ttk.Label(frame,
										  width=w))
		else:
			raise TypeError("Unknown widget type: {}".format(
					column["type"]))
	return widget_list


def update_rec_from_widgets(rec, column_descriptor, widget_row, instrument_type):
	"""Update the given rec with the content of a widget row.

	A row of widgets is used to hold user changes. Go through the
	row and collect the current content of each widget to update
	the record associated with that row.

	We look for changes to the account name if the account list is being edited."""

	for col, column in enumerate(column_descriptor):
		if column["type"] == "entry":
			# watch for account_name changes
			if instrument_type == 'account' and column['key'] == 'account':
				# Don't apply the nameChanged key to a new record - one which starts with "" name
				if rec[column['key']] != widget_row[col].get() and rec[column['key']] != "":
					rec['accNameChangedKey'] = rec[column['key']]   # save the old name for now
					rec[column['key']] = widget_row[col].get()       # update with the new name#729
			if column["content"] == 'text' or column["content"] == 'cusip':
				rec[column['key']] = widget_row[col].get()
			else:
				if widget_row[col].get() == "":
					rec[column['key']] = float(0)
				else:
					# Strip out commas added for display and make float()
					rec[column['key']] = float(widget_row[col].get().
											   replace(',', ''))
		elif column["type"] == "combo":
			rec[column['key']] = widget_row[col].get()
		elif column["type"] == "date":
			if column["content"] == "standard":
				rec[column['key']] = widget_row[col].cget('text')
		elif column["type"] == "checkbutton":
			pass     # we don't do anything with bond call buttons here
		elif column["type"] == "text":
			pass     # we use a text column type to display unchangeable data
		elif column["type"] == "filler":
			pass     # filler is just a spacer
		else:
			print("Unknown column type: {}".format(column["type"]))

def get_column_num_by_key(column_desc, key):
	for col, entry in enumerate(column_desc):
		if entry['key'] == key:
			return col
	raise ValueError("Unknown key: {}".format(key))

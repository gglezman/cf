#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2021 G.Glezman.  All Rights Reserved.
#
# cf - cash flows
#
# 
# Developers Notes
# 1. The ledger is a dictionary indexed by account_rec_id. The entry
#    in the dictionary is a list of transactions.  Each transaction is a
#    tuple. Each tuple has the following keys:
#           { account__rec_id: [(date, amount, balance, comment), (,,,)...]
#             account_rec_id: [(date, amount, balance, comment), (,,,)]   }
# 2. The ledger is built on restart
# 3. I used datetime internally rather than simply date. Its more overhead
#    but deposits are established with times earlier in the day than
#    debits, so they order properly (ie deposits first then withdrawals)
#    Opening balance has hour=1, deposits have hour=1, withdrawals have hr=11
# 
# 
# 
# 
import logging
from datetime import datetime, date, timedelta
import itertools
from tkinter import messagebox
from calendar import monthrange
import utilities as util
from cf_gui import CfGui
import data_file_constants as dfc
from occurrences import Occurrences
from file_manager import FileManager

#######################################################################
#  Constants used to set hour for transactions.  This forces transaction
#  to a preferred sequence in the register if they occur on the same day.
#######################################################################
INITIAL_DEPOSIT_TIME = 0
DEPOSIT_TIME = 1
INTEREST_TIME = 2
SALE_TIME = 3
WITHDRAWAL_TIME = 10
LATEST_TIME = 11


class CfAnalysis:
    def __init__(self, file_manager, logger):
        self.fm = file_manager
        self.logger = logger
        self.ledger = {}

        d = date.today()
        self.start_date = datetime(d.year, d.month, d.day)
        self.end_date = self.start_date

    def init_storage(self):
        self.ledger.clear()

    def restart(self, tracking_months):
        """Restart by reading in all the data records and recreating the ledger"""

        # tracking_months_count can be changed in Setting menu
        self.end_date = self.get_next_date(self.start_date, tracking_months) - \
            timedelta(days=1)

        ##########################################
        # Establish the balance in each cash account
        ##########################################
        self.account_set_up()

        ##########################################
        # Record all the transfers so balances
        # at any given instant are correct 
        ##########################################
        self.process_transfers()

        ##########################################
        # Process holdings prior to Cash Account/
        # Checking Account interest calculations 
        ##########################################
        self.process_loans()
        self.process_cds()
        self.process_bonds()
        self.process_funds()

        ##########################################
        # Apply interest to all interest
        # bearing holdings
        ##########################################
        self.apply_interest()
        self.logger.log(logging.INFO, "{}".format(util.f_name()))

    ################################################
    # Support Code
    ################################################
    @staticmethod
    def format_date(date):
        """ Take a datetime and return a string with just date"""
        if type(date) is not datetime:
            raise TypeError("{0}(): Input is not a datetime object".
                            format(util.f_name()))

        return "{0}-{1:02}-{2:02}".format(date.year, date.month, date.day)

    @staticmethod
    def append_register(trans, bal, register):
        """Simply append the transaction 'trans' to the 'register',
        updating the register balance.  Return the updated balance"""

        #  self.logger.log.info("{0}( {1}, {2:.2f} + {3:.2f})".format(
        #    util.f_name(), self.format_date(trans[0]), bal, trans[1]))

        if type(trans) != tuple:
            raise TypeError("{0}(): trans is wrong type".format(util.f_name()))
        if type(bal) != float:
            raise TypeError("{0}(): float is wrong type".format(util.f_name()))
        if type(register) != list:
            raise TypeError("{0}(): List is wrong type".format(util.f_name()))
        if type(trans) != tuple or type(bal) != float or type(register) != list:
            raise TypeError("{0}(): Input is wrong type".format(util.f_name()))

        bal = bal + trans[1]
        new_trans = (trans[0], trans[1], bal, trans[3])
        register.append(new_trans)

        return bal

    def trans_to_register(self, new_trans, reg):
        """Insert transaction 'new_trans' into the register 'reg' by date
        and update the balance of all following register entries.
        (Register 'reg' is a list of tuples.  Each tuple contains four elements
        in the following order:  datetime, amount, balance, comment)
        """

        if type(new_trans) != tuple or type(reg) != list:
            raise TypeError("{0}(): Input is wrong type".format(util.f_name()))

        #  self.logger.log.info("({0}: {1}, {2} {3})".format(
        #    util.f_name(),self.format_date(new_trans[0]),
        #    new_trans[1],reg[0][3]))

        inserted = False
        newlist = list()
        bal = float(reg[0][2])  # opening balance

        for trans in reg:
            if new_trans[0] > trans[0]:  # date comparision
                bal = self.append_register(trans, bal, newlist)
            else:
                if not inserted:
                    inserted = True
                    bal = self.append_register(new_trans, bal, newlist)
                bal = self.append_register(trans, bal, newlist)
        if not inserted:
            self.append_register(new_trans, bal, newlist)

        return newlist

    @staticmethod
    def get_bal_on_date(date, reg):
        """Return the balance of register 'reg' on date 'date'

        Look for a date beyond 'date' then use the balance of the previous
        register entry. This ensures the correct day's balance if there
        are multiple entries for the day.
        """
        if type(date) != datetime or type(reg) != list:
            raise TypeError("{0}(): Input is wrong type".format(util.f_name()) )

        # self.logger.log.info("{0}: Date: {1}".format(util.f_name(),
        #                                         self.format_date(date)))
        date = date.replace(hour=LATEST_TIME)

        latest_bal = reg[0][2]  # opening balance
        for trans in reg:
            if trans[0] > date:
                break
            latest_bal = trans[2]
        #  self.logger.log.info("{0}: Bal: {1}".format(util.f_name(), latest_bal))
        return float(latest_bal)

    def get_periodic_dates(self, start_date, period, end_date):
        """ Return a list of periodic dates, starting with 'start_date',
        at interval 'period', up to and possibly *including* 'end_date'
        This can go in either the forward or backward direction based
        on the relationship between 'start_date' and 'end_date'"""

        if type(start_date) != datetime or type(end_date) != datetime or \
                type(period) != str:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        #  self.logger.log.info("{0}() {1}, {2}, {3})".format(
        #    util.f_name(), self.format_date(start_date),
        #    period, self.format_date(end_date)))

        dates = []

        month_interval = self.period_to_months(period)

        if start_date <= end_date:
            # generate dates forward from the start date
            for i in itertools.count():  # infinite loop
                next_date = self.get_next_date(start_date, i * month_interval)
                if next_date <= end_date:
                    dates.append(next_date)
                else:
                    break
        else:
            # generate dates backward from the end date
            for i in itertools.count():  # infinite loop
                prev_date = self.get_previous_date(start_date, i * month_interval)
                # if next_date >= today and next_date <= end_date:
                if prev_date >= end_date:
                    dates.append(prev_date)
                else:
                    dates.reverse()  # date to ascending order
                    break

        # for date in dates:
        #    self.logger.log.info"  {0}".format(date))

        return dates

    @staticmethod
    def get_next_date(start_date, months):
        """Return a date 'months' months from 'start_date.  Correct 
        for short months (eg 1 month from jan 31st is feb 28th"""

        if type(start_date) != datetime or type(months) != int:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        next_year = start_date.year + ((start_date.month + months - 1) // 12)
        next_month = start_date.month + months  # modulo months avoids next loop
        while next_month > 12:
            next_month -= 12
        days_next_month = monthrange(next_year, next_month)[1]

        return start_date.replace(
                year=next_year,
                month=next_month,
                day=min(start_date.day, days_next_month))

    @staticmethod
    def get_previous_date(start_date, months):
        """Return a date 'months' months back from 'start_date.  Correct 
        for short months (eg 1 month from jan 31st is feb 28th"""

        if type(start_date) != datetime or type(months) != int:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        # // for negative numbers rounds instead of truncating !!!!
        prev_year = start_date.year - ((-(start_date.month - months - 12)) // 12)
        prev_month = start_date.month - months
        while prev_month <= 0:
            prev_month += 12
        days_next_month = monthrange(prev_year, prev_month)[1]

        return start_date.replace(
                year=prev_year,
                month=prev_month,
                day=min(start_date.day, days_next_month))

    def credit(self, accnt_rec_id, amount, date, comment, credit_type=DEPOSIT_TIME):
        """Credit account 'accnt_rec_id' on 'date' in the 'amount' with 'comment'.
        The register balance will be recalculated and updated"""

        self.logger.log(logging.INFO,"{0}() account_rec_id: {1}, amount: {2}, {3})".format(
            util.f_name(), accnt_rec_id, amount, self.format_date(date)))

        if type(accnt_rec_id) != int or type(amount) != float or type(date) != datetime:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        date = date.replace(hour=credit_type)
        transaction = (date, amount, 0, comment)
        self.ledger[accnt_rec_id] = self.trans_to_register(transaction,
                                                    self.ledger[accnt_rec_id])

    def debit(self, accnt_rec_id, amount, date, comment):
        """Debit account 'accnt_rec_id' on 'date' in the amount 'amount' with 'comment'"""

        #  self.logger.log.info("{0}() {1}, {2}, {3})".format(
        #    util.f_name(), accnt, amount, self.format_date(date)))

        if type(accnt_rec_id) != int or type(amount) != float or type(date) != datetime:
            raise TypeError("{0}() : Input type error".
                            format(util.f_name()))

        date = date.replace(hour=WITHDRAWAL_TIME)
        transaction = (date, -amount, 0, comment)
        self.ledger[accnt_rec_id] = self.trans_to_register(transaction,
                                                    self.ledger[accnt_rec_id])

    @staticmethod
    def period_to_months(period):
        """Convert a string defining the period (eg quarterly) to 
        months in the period"""

        if type(period) != str:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        if period == "once":
            months = 999  # ensure single date in list; return start_date
        elif period == "monthly":
            months = 1
        elif period == "annual":
            months = 12
        elif period == "semi-annual":
            months = 6
        elif period == "quarterly":
            months = 3
        else:
            raise ValueError("Unsupported compounding freq: {}".format(period))
        return months

    @staticmethod
    def period_to_rate_factor(period):
        """Convert a string defining the period (eg quarterly) to a divisor that
        converts an annual rate to an applicable rate (eg quarterly => 4)"""

        if type(period) != str:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        if period == "monthly":
            factor = 12
        elif period == "annual":
            factor = 1
        elif period == "semi-annual":
            factor = 2
        elif period == "quarterly":
            factor = 4
        else:
            raise ValueError("Unsupported compounding freq: {}".format(period))
        return factor

    def bond_purchase_price(self, purchase_date, bond_price, quantity,
                            rate, first_coupon, period_months):
        """ standard bond pricing - bond_price  """
        principal = 1000 * quantity
        bond_cost = bond_price * 10 * quantity
        pd = self.get_previous_date(first_coupon, period_months)
        # ratio is percentage of year for which interest is due
        ratio = self.calc_30_360(pd, purchase_date)
        accrued_interest = ratio * rate / 100 * principal
        return bond_cost, accrued_interest

    ###########################################################
    # The following group of functions are to support unit test
    ###########################################################
    def reset_ledger(self):
        """This is used to facilitate unit test"""

        self.ledger.clear()

    # todo - if I take out internal storage of accounts, CAs, bonds, etc
    #        I need to re-write unit test to work off test database files!
    def append_accounts(self, entry):
        self.accounts.append(entry)

    def append_cash_accounts(self, entry):
        self.cash_accounts.append(entry)

    def append_bonds(self, entry):
        self.bonds.append(entry)

    def append_funds(self, entry):
        self.funds.append(entry)

    def append_cds(self, entry):
        self.cds.append(entry)

    def append_loans(self, entry):
        self.loans.append(entry)

    def append_transfers(self, entry):
        self.transfers.append(entry)

    def get_register(self, account_rec_id):
        if account_rec_id in self.ledger:
            return self.ledger[account_rec_id]
        else:
            raise ValueError("Unknown account: {0}".format(account_rec_id))

    ###########################################################
    # end of unit test support code
    ###########################################################

    def account_set_up(self):
        """Establish the opening balance of all cash accounts in the ledger"""

        self.logger.log(logging.INFO, "Entering: {}".format(util.f_name()))

        # todo entry= { account, balance,  } Use dictionary instead of tuple
        for entry in self.get_from_db('ca'):
            #  self.logger.log.info("{0} account balance on {1}: ${2} ".format(
            #    entry['account'], entry['opening_date'], entry['balance']))

            # The account record holds the opening date for the cash account
            account_rec = self.get_from_db('account','rec_id', entry['account_rec_id'])[0]

            start_date = datetime.strptime(account_rec['opening_date'], dfc.DATE_FORMAT)
            start_date = start_date.replace(hour=INITIAL_DEPOSIT_TIME)

            # first entry for this account in the ledger - tuple
            beg_bal = (start_date, 0, entry['balance'],
                       account_rec['account_name'] + " Opening Balance")

            # Ensure each dictionary entry is treated as a list of tuples
            self.ledger[entry['account_rec_id']] = list()
            self.ledger[entry['account_rec_id']].append(beg_bal)

    def validate_transfer(self, entry):

        #self.logger.log(logging.INFO, "Entering: {}".format(util.f_name()))

        if entry['to_account_rec_id'] == dfc.INCOME_ACCOUNT_ID:
            raise ValueError("{0}(): Transfer destination can't be 'income'".
                             format(util.f_name()))
        else:
            if entry['to_account_rec_id'] != dfc.EXPENSE_ACCOUNT_ID and \
                    entry['to_account_rec_id'] not in self.ledger:
                raise ValueError("{0}(): Unknown transfer destination: {1}".
                                 format(util.f_name(), entry['to_account_rec_id']))
        if entry['from_account_rec_id'] == dfc.EXPENSE_ACCOUNT_ID:
            raise ValueError("{0}(): Transfer source can't be 'expense'".
                             format(util.f_name()))
        else:
            if entry['from_account_rec_id'] != dfc.INCOME_ACCOUNT_ID and \
                    entry['from_account_rec_id'] not in self.ledger:
                raise ValueError("{0}(): Unknown transfer source: {1}".
                                 format(util.f_name(), entry['from_account_rec_id']))

    def process_transfers(self):
        """Record all transfers to/from accounts based on the transfer list.

        Note that transfers may have an inflation factor associated with it.
        If so, the factor is applied before the transfers are entered.
        """
        transfer_records = self.get_from_db('transfer')

        self.logger.log(logging.INFO,
                    "Entries in Transfers list: {0}".format(len(transfer_records)))

        for entry in transfer_records:
            #print(entry)
            # Fault if invalid
            self.validate_transfer(entry)
            transfer_dates = self.get_dates(entry['frequency'], self.end_date)
            transfer_amounts = self.get_inflated_amounts(entry['amount'],
                                                         entry['inflation'],
                                                         transfer_dates)

            # Find the earliest date both accounts are open
            if self.ledger[entry['from_account_rec_id']][0][0] > \
                        self.ledger[entry['to_account_rec_id']][0][0]:
                opening_date = self.ledger[entry['from_account_rec_id']][0][0]
            else:
                opening_date = self.ledger[entry['to_account_rec_id']][0][0]

            #print("Opening Date :{}".format(opening_date))
            #print(transfer_dates)
            #print(transfer_amounts)
            #print()
            for i,transDate in enumerate(transfer_dates):
                if transDate >= opening_date:
                    self.debit(entry['from_account_rec_id'],
                       transfer_amounts[i],  # float(entry['amount']),
                       transDate,
                       "Transfer to " + str(entry['to_account_name']) +
                       ", Note: " + entry['note'])
                    self.credit(entry['to_account_rec_id'],
                        transfer_amounts[i],  # float(entry['amount']),
                        transDate,
                        "Transfer from " + str(entry['from_account_name'])
                        + ", Note: " + entry['note'])

        """
            # select an opening date that is the  
            if entry['from_account_rec_id'] == dfc.INCOME_ACCOUNT_ID:
                opening_date = self.ledger[entry['to_account_rec_id']][0][0]
            elif entry['to_account_rec_id'] == dfc.EXPENSE_ACCOUNT_ID:
                opening_date = self.ledger[entry['from_account_rec_id']][0][0]
            else:
                # Earliest of to/from accounts
                if self.ledger[entry['from_account_rec_id']][0][0] < \
                        self.ledger[entry['to_account_rec_id']][0][0]:
                    opening_date = self.ledger[entry['from_account_rec_id']][0][0]
                else:
                    opening_date = self.ledger[entry['to_account_rec_id']][0][0]

            for i, transDate in enumerate(transfer_dates):       # todo use an enumeration here to get an index into the list so I can skip old values
                if transDate >= opening_date:
                    if entry['from_account_rec_id'] != dfc.INCOME_ACCOUNT_ID:
                        if transDate >= self.ledger[entry['from_account_rec_id']][0][0]:
                            self.debit(entry['from_account_rec_id'],
                                       transfer_amounts[i], # float(entry['amount']),
                                       transDate,
                                       "Transfer to " + str(entry['to_account_rec_id']) +
                                       ", Note: " + entry['note'])
                    if entry['to_account_rec_id'] != dfc.EXPENSE_ACCOUNT_ID:
                        if transDate >= self.ledger[entry['to_account_rec_id']][0][0]:
                            self.credit(entry['to_account_rec_id'],
                                        transfer_amounts[i], # float(entry['amount']),
                                        transDate,
                                        "Transfer from " + str(entry['from_account_rec_id'])
                                        + ", Note: " + entry['note'])
        """

    def process_loans(self):
        """Update each account based on loans on top of balances"""

        loan_records = self.get_from_db('loan')

        self.logger.log(logging.INFO,"Entries in Loans list: {0}".format(len(loan_records)))

        for entry in loan_records:
            # If the Loan origination date is on or after
            # the opening date,
            # enter both the debit on loan and a credit on maturity.
            # Otherwise, just enter a credit on maturity.

            opening_date = self.ledger[entry['account_rec_id']][0][0]
            origination_date = datetime.strptime(entry['orig_date'], "%Y-%m-%d") # Todo - dfc.DATE_FORMAT
            closing_date = datetime.strptime(entry['payoff_date'], "%Y-%m-%d")
            loan_bal = float(entry['balance'])

            if origination_date >= closing_date:
                raise ValueError(
                        "Loan closing date must follow origination date")

            if opening_date >= closing_date:
                # Loan is already closed
                continue

            if origination_date >= opening_date:
                self.debit(entry['account_rec_id'], loan_bal, origination_date,
                           "Loan origination " + entry['note'])

            # The loan will be entered with its origination date. The
            # opening balance should account for any interest already paid.
            # Therefore ignore any interest before the opening date
            interest_dates = self.get_periodic_dates(origination_date,
                                                     entry['frequency'],
                                                     closing_date)
            interest_dates.append(closing_date)  # last date not on list
            earlier_date = origination_date
            for date in interest_dates:
                if date >= opening_date:
                    period = date - earlier_date
                    rate = period.days / 365 * float(entry['rate']) / 100
                    interest = float(loan_bal) * rate
                    loan_bal += interest
                    earlier_date = date

            self.credit(entry['account_rec_id'], loan_bal, closing_date,
                        "Loan repayment: " + entry['note'],
                        credit_type=SALE_TIME)

    def process_cds(self):
        cd_records = self.get_from_db('cd')

        self.logger.log(logging.INFO,"Entries in CDs list: {0}".format(len(cd_records)))

        for entry in cd_records:
            # If the CD purchase date is on or after the opening date,
            # enter both the debit on purchase and a credit on maturity.
            # Otherwise, just enter a credit on maturity.
            # Zero's should be entered with the actual purchase price
            # not face value

            opening_date = self.ledger[entry['account_rec_id']][0][0]
            purchase_date = datetime.strptime(entry['purchase_date'], "%Y-%m-%d")
            maturity_date = datetime.strptime(entry['maturity_date'], "%Y-%m-%d")

            if purchase_date >= maturity_date:
                raise ValueError(
                        "CD maturity date must follow purchase date")
            if opening_date >= maturity_date:
                # pass history
                continue

            # The CD may be entered with its original purchase date.
            # The opening balance should account for any interest already
            # paid. So ignore any interest before the opening date
            if purchase_date > opening_date:
                earliest_interest_date = purchase_date
            else:
                earliest_interest_date = opening_date

            #  period_months = self.period_to_months(entry['frequency'])

            interest_dates = self.get_periodic_dates(maturity_date,
                                                     entry['frequency'],
                                                     earliest_interest_date)
            #  first_interest_date = interest_dates[0]

            purchase_price = float(entry['purchase_price']) * \
                float(entry['quantity'])
            if purchase_date >= opening_date:
                self.debit(entry['account_rec_id'], purchase_price,
                           purchase_date,
                           "CD purchase, CUSIP: " + entry['cusip'])

            earlier_date = earliest_interest_date
            principal = float(entry['purchase_price']) * float(entry['quantity'])

            for date in interest_dates:
                period = date - earlier_date
                rate = period.days / 365 * float(entry['rate']) / 100
                interest = principal * rate
                self.credit(entry['account_rec_id'], interest, date,
                            "CD Interest, CUSIP: " + entry['cusip'])
                earlier_date = date

            self.credit(entry['account_rec_id'], principal, maturity_date,
                        "CD Sale, CUSIP: " + entry['cusip'],
                        credit_type=SALE_TIME)

    def process_bonds(self):
        # TODO - handle a bond call
        #  skip coupons after the call date
        #  calc interest based on outstanding days
        #  calc final payment on call date based on call premium
        #
        bond_records = self.get_from_db('bond')
        self.logger.log(logging.INFO,"Entries in Bonds list: {0}".format(len(bond_records)))
        for entry in bond_records:
            #print(entry)
            details = self.bond_cash_flow(entry)

            # If the Bond purchase date is on or after the opening date,
            # enter both the debit on purchase and a credit on maturity.
            # Otherwise, just enter a credit on maturity.

            opening_date = self.ledger[entry['account_rec_id']][0][0]
            for record in details:
                if record['date'] >= opening_date:
                    if record['amount'] < 0:
                        self.debit(entry['account_rec_id'],
                                   -record['amount'],
                                   record['date'],
                                   record['note'] + ", CUSIP: " + entry['cusip'])
                    else:
                        if record['note'] == 'Bond Sale':
                            self.credit(entry['account_rec_id'],
                                        record['amount'],
                                        record['date'],
                                        record['note'] + ", CUSIP: " +
                                        entry['cusip'],
                                        credit_type=SALE_TIME)
                        else:
                            self.credit(entry['account_rec_id'],
                                        record['amount'],
                                        record['date'],
                                        record['note'] + ", CUSIP: " +
                                        entry['cusip'])

    def bond_cash_flow(self, entry):
        details = []
        purchase_date = datetime.strptime(entry['purchase_date'], "%Y-%m-%d")
        maturity_date = datetime.strptime(entry['maturity_date'], "%Y-%m-%d")

        # The bond wil be redeemed on either the call date or maturity
        # date. If there is no call, call_date will be set to maturity date.
        # therefore, call_date represents the redemption date in all cases.
        call_price = entry['call_price']
        if call_price == 0.0:
            # no call
            call_date = maturity_date
        else:
            call_date = datetime.strptime(entry['call_date'], "%Y-%m-%d")

        period_months = self.period_to_months(entry['frequency'])

        interest_dates = self.get_periodic_dates(maturity_date,
                                                 entry['frequency'],
                                                 purchase_date)
        first_interest_date = interest_dates[0]

        purchase_price = self.bond_purchase_price(purchase_date,
                                                  float(entry['bond_price']),
                                                  float(entry['quantity']),
                                                  float(entry['coupon']),
                                                  first_interest_date,
                                                  period_months)
        details.append({'date': purchase_date, 'amount': -purchase_price[0],
                        'note': "Bond Purchase"})
        details.append({'date': purchase_date, 'amount': -purchase_price[1],
                        'note': "Bond Accrued Interest"})
        details.append({'date': purchase_date, 'amount': -float(entry['fee']),
                        'note': "Bond Fees"})

        principal = 1000.0 * float(entry['quantity'])

        # TODO - process_bonds() does this same calculation
        # TODO - this does not pick up the proper last_interest_date
        #         if the date was before the purchase.
        #         On a call, the callee must pay interest from the
        #         last coupon through the call date.
        #         This code will pay interest from the purchase date
        #         through the call date - see parameters to calc_30_360)
        # see bond_purchase_price for fix to this
        factor = self.period_to_rate_factor(entry['frequency'])
        last_interest_date = None
        for date in interest_dates:
            if date <= call_date:
                # don't use any interest after the call_date
                interest = principal * (float(entry['coupon'] / factor / 100))
                details.append({'date': date, 'amount': interest,
                                'note': "Bond Interest"})
                last_interest_date = date

        if call_price != 0.0:
            # A called bond makes a partial coupon payment based
            # on the call date

            # ratio is percentage of year for which interest is due
            if last_interest_date is None:
                ratio = self.calc_30_360(purchase_date, call_date)
            else:
                ratio = self.calc_30_360(last_interest_date, call_date)

            rate = ratio * float(entry['coupon']) / 100
            interest = principal * rate
            details.append({'date': call_date, 'amount': interest,
                            'note': "Bond Interest (call)"})

            # A called bond may be at a premium. Use the call_price
            principal = entry['call_price'] * 10 * float(entry['quantity'])

            details.append({'date': call_date, 'amount': principal,
                            'note': "Bond Call"})
        else:
            details.append({'date': maturity_date, 'amount': principal,
                            'note': "Bond Sale"})
        return details

    def process_funds(self):
        """Process each fund entry in the list.

        The fund entry is used to set the balance in the fund.
        """
        fund_records = self.get_from_db('fund')
        self.logger.log(logging.INFO,"Entries in Funds list: {0}".format(len(fund_records)))

        for entry in fund_records:
            entry_date = datetime.strptime(entry['date'], dfc.DATE_FORMAT)

            self.credit(entry['account_rec_id'],
                        entry['balance'],
                        ca_date,
                        'balance')
            # TODO - how about interest processing ???

    def apply_interest(self):
        """Apply interest to all cash accounts"""
        cash_accounts = self.get_from_db('ca')
        self.logger.log(logging.INFO,
                    "Entries in Cash Accounts: {0}".format(len(cash_accounts)))
        for ca in cash_accounts:
            start_date = datetime.strptime(ca['interest_date'], "%Y-%m-%d")

            # push all int payment dates after opening date
            #account_rec = self.get_account(ca['account_rec_id'])
            account_rec = self.get_from_db('account', 'rec_id', ca['account_rec_id'])[0]
            opening_date = datetime.strptime(account_rec['opening_date'], "%Y-%m-%d")
            months_in_period = self.period_to_months(ca['frequency'])
            while opening_date > start_date:
                start_date = self.get_next_date(start_date,
                                                months_in_period)

            interest_dates = self.get_periodic_dates(start_date,
                                                     ca['frequency'],
                                                     self.end_date)
            rate_adj = self.period_to_rate_factor(ca['frequency'])
            rate = (float(ca['rate']) / rate_adj) / 100

            for interest_date in interest_dates:
                bal = self.get_bal_on_date(interest_date,
                                           self.ledger[ca['account_rec_id']])
                interest = bal * rate

                if interest > 0.0:
                    self.credit(ca['account_rec_id'], interest, interest_date,
                                "Interest", credit_type=INTEREST_TIME)
                else:
                    # ignore negative interest
                    self.credit(ca['account_rec_id'], 0.0, interest_date,
                                "Interest", credit_type=INTEREST_TIME)

    @staticmethod
    def calc_30_360(date_1, date_2):
        """Using the 30/360 approach, calculate an interest factor.

        The resulting factor is the ratio of annual interest that should
        be applied for the period specified by the two dates.

        This is my best guess at what 30/360 used by Fidelity means.
        First, every month is assumed to have 30 days and the year has 360.
        When doing a calculation, first determine the number of whole 
        months - assume each has 30 has. Then figure the number of remaining
        days. Add those together and divide by 360.
        ::

            eg    5/1/2018 - 9/28/2018
                     4 months * 30  = 120 days     (5,6,7,8)
                     28 - 1         =  27 days     (in Sept)
                                      ----
                                      147 days

                   147/360 = % of yearly interest due
        
            eg    5/28/2018 - 9/1/2018
                     3 months       = 90 days      
                     2 + 1          =  3 days    5/29,5/30, 9/1)
                                      --- 
                                      93 days
                     93/360 = % of yearly interest due
        """
        if date_2 < date_1:
            raise ValueError("date_2 must be >= date_1")

        if date_2.month >= date_1.month:
            months = date_2.month - date_1.month + (12 * (date_2.year - date_1.year))
        else:
            months = (12 - date_1.month + 1) + (date_2.month - 1) + \
                     (12 * (date_2.year - date_1.year - 1))
        if date_1.day > date_2.day:
            months -= 1
            days = 30 - date_1.day + date_2.day
        else:
            days = date_2.day - date_1.day

        total_days = (30 * months) + days
        ratio = total_days / 360.0

        return ratio

    @staticmethod
    def get_dates(occurrence_spec, last_date):
        """Get a list of dates per the given frequency specification.

        Note: no dates are included that are beyond the last_date

        Note: this function is also used during unit test

        Args
            frequency_spec (str): occurrence specification used to generate
                date list

            last_date (datetime): last date to track based on tracking months
                specified in the settings.

        Return:
            date (list(datetime)): a list of dates, in datetime format
                matching the given input
        """
        occ = Occurrences(occurrence_spec, last_date)

        return occ.get_dates()

    @staticmethod
    def get_inflated_amounts(amount, inflation, date_list):
        """Get a list of amounts, which increase by the given inflation rate,
        for the given list of dates.

        Note the inflation factor is applied on a yearly basis, in the first month
        of each succeeding year.

        Return:
            amount_list (list(floats)): a list of inflation corrected amounts,
                 one for each day in the date_list.
        """
        if len(date_list) == 0:
            return

        year = date_list[0].year
        amount_list = []

        for date in date_list:
            next_year = date.year
            if next_year != year:
                year= next_year
                amount = amount+amount*inflation/100
            amount_list.append(amount)

        return amount_list

    def get_sorted_accounts_list(self, expense=False, income=False):
        """Return a sorted list of account names.

        The list contains only the Account Name of the account.

        By default, the expense and income pseudo accounts are removed
        but they can be included by adding the associated parameter."""
        account_names = list()

        for record in self.get_from_db('account'):
            account_names.append(record["account_name"])

        if account_names:
            account_names.sort()
            if not expense:
                account_names.remove("expenses")
            if not income:
                account_names.remove("income")

        return account_names

    def get_account_name(self, account_rec_id):
        cursor = self.fm.db_conn.execute(
            "SELECT account_name FROM account WHERE rec_id=\'{}\'".format(account_rec_id))
        return cursor.fetchone()[0]

    def get_accounts_with_bond_import_methods(self):
        # todo - this looks a little light
        return []

    # todo -this can be upgraded
    def get_account_update_method(self, acc_id):
        for account in self.get_from_db('account'):
            if account['rec_id'] == acc_id:
                return account['update_method']
        return None

    def get_accounts_with_import_methods(self):
        """Return accounts that have an import method specified

        :return: A list of account records. Each record includes the
                 account, account_rec_id and the update_method.
        """
        account_data = []
        for rec in self.get_from_db('account'):
            if rec['update_method'] != "Manual":
                account_data.append({'account_name': rec['account_name'],
                                     'account_rec_id': rec['rec_id'],
                                     'update_method': rec['update_method']})

        return account_data

    def get_account_id_map(self):
        """Map account_rec_id to account

        :return: dictionary where account_rec_id is the key to get account_name
        """
        id_map = {}
        for account in self.get_from_db('account'):
            id_map[account['rec_id']] = account['account_name']
        return id_map

    # todo - this can be adjusted
    def get_rec_id_from_acnt_name_OBFISCATED(self, name):
        for account in self.get_from_db('accounts'):
            if account['account_name'] == name:
                return account['rec_id']

        # todo - log the following as an error
        return ""

    def get_account_rec_id(self, account_name):
        """
        Return just the rec_id for the given account_name

        Note: The query returns a set of tuples, one tuple for each
              row that matches the query. In my case, one row for each account
              with a matching rec_id. Of course, by design, rec_ids are
              unique so there will only be one row (tuple) in the returned set.
              The tuple will have a component for each column in the row.
              All components in the tuple are set to None except the first
              since that is the column that contains the rec_id. (see DB schema)
        """
        try:
            query = "SELECT rec_id FROM account WHERE account_name=\'{}\'".format(account_name)
            self.logger.log(logging.INFO, query)
            cursor = self.fm.db_conn.execute(query)
            #print(cursor.description)
            account_rec_id = cursor.fetchone()[0]

        except Exception as e:
            # the following is used in case there are no accounts yet
            account_rec_id = 0

        return account_rec_id

    def get_real_accounts(self, table):
        """Get a list of real (ie not pseudo) accounts

        This function can be used on the account or cash_account table
        """
        accounts = self.get_from_db(table)

        return [i for i in accounts if not (i['rec_id'] < dfc.FIRST_REAL_ACCOUNT)]

    def get_from_db(self, table, column=None, value=None):
        """Return selected rows from the specified table/column match'

        If only table is specified, all rows in the table are returned.

        If a column is specified, value must also be specified. Any row where
        'column' data matches 'value' are returned.

        Read the column names and data from the DB and construct a python style
        dict to return.

        Return: table_content[] - list of dictionaries
        """


        """
        >>> import sqlite3
        >>> con.row_factory = sqlite3.Row
        >>> cur = con.cursor()
        >>> cur.execute("SELECT id, first_name, last_name FROM customers WHERE id = 2")
        >>> result = cur.fetchone()
        >>> id, first_name, last_name = result['id'], result['first_name'], result['last_name']
        >>> print(f"Customer: {first_name} {last_name}'s id is {id}")
        Customer: Donald Knuth's id is 2
        """
        self.logger.log(logging.INFO,
                        "get_from_db:  table: {}, column: {}, Value: {} ".format(table, column, value))
        table_content = []
        if not self.fm.is_data_file_open():
            self.logger.log(logging.INFO,"DB not open")
            return table_content

        column_names = []

        # Get the column names to be used for the dictionary
        cursor = self.fm.db_conn.execute("SELECT * FROM PRAGMA_TABLE_INFO(\'{}\');".format(table))
        for row in cursor:
            column_names.append(row[1])  # column 1 has the column name

        if column == None:
            query = "SELECT * FROM {}".format(table)
        else:
            query = "SELECT * FROM {} WHERE {} == {}".format(table, column, value)

        self.logger.log(logging.INFO,query)
        cursor = self.fm.db_conn.execute(query)

        # connect the column names and column data
        for row in cursor:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            table_content.append(row_dict)

        #self.logger.log(logging.INFO,"      {}".format(table_content))
        return table_content

    def set_setting(self, setting, value):
        update = "UPDATE setting SET \'{}\'=\'{}\'".format(setting,value)

        self.logger.log(logging.INFO, update)

        cursor = self.fm.db_conn.execute(update)
        self.fm.db_conn.commit()

    def write_to_db(self, table, rec_id, data):
        """ Write the given mods to the given rec (rec_id)

        table - table being written
        rec_id - identifies the record in the table
        data - list of modifications to the record. Each entry in the list is a
               tuples where each tuple is ( key, new_value)

        In order to shield other pieces of code from the account_rec_id,
        from/to_account_rec_id, we do the maintenance of these fields in
        this function based on the content of the corresponding 'name' field.

        Note that while the account_name can be changed in the account table,
        this table does not have an account_rec_id in the same way other tables do.
        """

        for mod in data:
            if mod[0] == 'account_name':
                if table != 'account':
                    data.append(('account_rec_id', self.get_account_rec_id(mod[1])))
            elif mod[0] == 'from_account_name':
                data.append(('from_account_rec_id', self.get_account_rec_id(mod[1])))
            elif mod[0] == 'to_account_name':
                data.append(('to_account_rec_id', self.get_account_rec_id(mod[1])))
        if data:
            update = "Update {} Set ".format(table)
            for mod in data:
                update += "\'{}\' = \'{}\' ,".format(mod[0], mod[1])
            update = update[:-1]   # remove the final comma
            update += "Where rec_id = \'{}\'".format(rec_id)

            self.logger.log(logging.INFO, update)

            cursor = self.fm.db_conn.execute(update)
            self.fm.db_conn.commit()

    def new_db_rec(self, table, rec):
        """Add a new record to the DB

        In order to shield other pieces of code from the account_rec_id,
        from/to_account_rec_id, we do the maintenance of these fields in
        this function based on the content of the corresponding 'name' field.
        """
        if table == "fund" or table == "cd" or table == "ca" or table == "bond" or table == "loan":
            rec['account_rec_id'] = self.get_account_rec_id(rec['account_name'])
        elif table == 'transfer':
            rec['from_account_rec_id'] = self.get_account_rec_id(rec['from_account_name'])
            rec['to_account_rec_id']   = self.get_account_rec_id(rec['to_account_name'])
        else:
            raise RuntimeError("Unknown Table Type : {}".format(table))

        values = "VALUES ("
        insert = "Insert into {} (".format(table)
        for key in rec.keys():
            insert += key + ","
            values += "\'{}\',".format(rec[key])
        insert = insert[:-1]       # remove the final comma
        insert += ")"
        values = values[:-1]
        values += ")"
        insert += values

        self.logger.log(logging.INFO, insert)

        self.fm.db_conn.execute(insert)
        self.fm.db_conn.commit()

    def delete_db_rec(self, table, rec_id):
        delete = "Delete from {} where rec_id = \'{}\'".format(table, rec_id)
        self.logger.log(logging.INFO, delete)

        self.fm.db_conn.execute(delete)
        self.fm.db_conn.commit()

    def account_create(self, rec):
        """User has created a new account. Create the corresponding cash account

        Notice we don't specify the rec_id because its is auto-increment.
        """


        """
        A note - wrap all the activities in a transaction
            try:
                create()
                create
                con.commit()
            except Exception e:
                con.rollback()
                Raise runtimeError()
        
        """
        # ################################################
        # First add a record to the account table
        # ################################################
        #del rec['rec_id']

        values = "VALUES ("
        insert = "Insert into account ("
        for key in rec.keys():
            insert += key + ","
            values += "\'{}\',".format(rec[key])
        insert = insert[:-1]  # remove the final comma
        insert += ")"
        values = values[:-1]
        values += ")"
        insert += values
        self.logger.log(logging.INFO, insert)

        self.fm.db_conn.execute(insert)
        self.fm.db_conn.commit()

        # ################################################
        # Now add a record to the ca table
        # ################################################
        values = "VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\',\'{}\',\'{}\')".format(
            self.get_account_rec_id(rec['account_name']),
            rec['account_name'],
            0.0,                          # opening balance
            0.0,                          # default rate
            rec['opening_date'],
            'monthly',
            "")
        insert = "Insert into ca "
        insert += "(account_rec_id,account_name,balance,rate,interest_date,frequency,note) "
        insert += values
        self.logger.log(logging.INFO, insert)

        self.fm.db_conn.execute(insert)
        self.fm.db_conn.commit()

    def account_delete(self, account_rec_id):
        """An account has been deleted.

        Delete the associated cash account and any other records in other tables
        associated with this account. Also check if the deleted account is
        the default_account in the settings. If so, select an alternate account.

        Note the structure of this function should be used as a model for all db functions
        """
        rec_list = self.get_from_db('account', column="rec_id", value=account_rec_id )
        rec = rec_list[0]

        try:
            for table in ('fund', 'cd', 'ca', 'bond', 'loan'):
                delete = "Delete from {} where account_name = \'{}\'".format(table, rec['account_name'])
                self.logger.log(logging.INFO, delete)
                cursor = self.fm.db_conn.execute(delete)

            delete = "Delete from transfer where from_account_name = \'{}\'".format(rec['account_name'])
            self.logger.log(logging.INFO, delete)
            cursor = self.fm.db_conn.execute(delete)

            delete = "Delete from transfer where to_account_name = \'{}\'".format(rec['account_name'])
            self.logger.log(logging.INFO, delete)
            cursor = self.fm.db_conn.execute(delete)

            settings = self.get_from_db('setting')
            if settings[0]['default_account'] == rec['account_name']:
                accounts = self.get_sorted_accounts_list()
                print(accounts[0])
                if len(accounts) > 0:
                    default_account = accounts[0]
                else:
                    default_account = ""
                update = "UPDATE setting SET default_account =\'{}\'".format(default_account)

                self.logger.log(logging.INFO, update)
                cursor = self.fm.db_conn.execute(update)

            self.fm.db_conn.commit()

        except Exception as e:
            self.logger.log(logging.INFO, "Account Delete Exception: {}".format(e))
            messagebox.showerror("Account Deletion Error","{}".format(e) )
            self.fm.db_conn.rollback()
            raise RuntimeError("Account delete failed")

    def account_name_changed(self, old_name, new_name):
        """An account name has changed.

        Go through all tables in the DB  and update the account name
        """
        try:
            for table in ('fund', 'cd', 'ca', 'bond', 'loan'):
                update = "Update \'{}\' Set account_name = \'{}\' Where account_name = \'{}\'".format(table, new_name, old_name)
                self.logger.log(logging.INFO, update)

                cursor = self.fm.db_conn.execute(update)

            update = "Update transfer Set from_account_name = \'{}\' where from_account_name = \'{}\'".format(new_name,old_name)
            self.logger.log(logging.INFO, update)
            cursor = self.fm.db_conn.execute(update)

            update = "Update transfer Set to_account_name = \'{}\' where to_account_name = \'{}\'".format(new_name,old_name)
            self.logger.log(logging.INFO, update)
            cursor = self.fm.db_conn.execute(update)

            update = "Update setting Set default_account = \'{}\' where default_account = \'{}\'".format(new_name,old_name)
            self.logger.log(logging.INFO, update)
            cursor = self.fm.db_conn.execute(update)

            self.fm.db_conn.commit()

        except Exception as e:
            self.logger.log(logging.INFO, "Account Name Change Exception: {}".format(e))
            self.fm.db_conn.rollback()
            raise RuntimeError("Account name change failed")

    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date

    def update_account(self, account_id, account_details):
        """ todo - when is this called and why is it called - looks like its called from import_account
        This is called when a user hits the import button and import func has returned a list if records
        :param account_id: account to update # todo - is this a text string ? account id?
        :param account_details: This is a list of dictionary entries, with each
                entry containing fields based on the investment type:

                investment_type='ca'
                {symbol, date, description, value}

                investment_type='fund'
                {symbol, date, description, quantity, value}

                investment_type='bond'
                {symbol, date, description, quantity, value}

                investment_type='unknown'
                [symbol, date, description, quantity, value}
        :return:
        """
        """
        This is being done in import_support now.
        for rec in account_details:
            if rec['investment_type'] == 'ca':
                for ca in self.cash_accounts:
                    if ca['account_id'] == account_id:
                        ca['balance'] = rec['value']
                        ca['opening_date'] = rec['date']
                        break
                messagebox.showinfo("Cash Account Update",
                                     "{} [{}] {}: ${}".format(
                                         rec['date'],
                                         rec['symbol'],
                                         rec['description'],
                                         rec['value']))
            else:
                print("{}: {}: {} / {}".format(
                    rec['investment_type'], rec['description'],
                    rec['quantity'],rec['value']))
        """

    # TODO - the following needs work. For weekly, I need to add code to
    # get_periodic.
    def get_account_data(self, account_rec_id, granularity,
                         start_date, end_date):
        """Get account data for graphing

        :param account_rec_id: from the DB
        :param granularity: 'monthly','annually','semiannually','quarterly'
                Issue - month is the lowest granularity
        :param start_date:
        :param end_date:
        :return: list of (date,balance) tuples
        """
        #    annual use 12/31
        #    monthly - use the 31
        #    weekly - I may need to add code to get_periodic
        # then get the balance for each end date and write a summary_register

        data = []
        if account_rec_id in self.ledger.keys():
            account = self.ledger[account_rec_id]
            dates = self.get_periodic_dates(start_date, granularity.lower(),
                                            end_date)
            for date in dates:
                bal = self.get_bal_on_date(date, account)
                # print("Date {} = {}".format(date,bal))
                data.append((date, bal))

        return data

class Logger:
    def __init__(self, default_level):
        self.log_connection = None
        self.default_level = default_level

        ##########################################
        # Set up logger
        ##########################################

        log_format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename="./cf_log.txt",
                        level=default_level,
                        format=log_format,
                        filemode='a')
        self.log_connection = logging.getLogger()

        self.log_connection.log(logging.INFO, "Logger setup complete")

    def log(self, lvl, debug_msg):
        if lvl == logging.CRITICAL:
            self.log_connection.log(logging.CRITICAL,debug_msg)
        elif lvl == logging.ERROR:
            self.log_connection.log(logging.ERROR, debug_msg)
        elif lvl == logging.WARNING:
            self.log_connection.log(logging.WARNING, debug_msg)
        elif lvl == logging.INFO:
            self.log_connection.log(logging.INFO, debug_msg)
        elif lvl == logging.DEBUG:
            self.log_connection.log(logging.DEBUG, debug_msg)
        else:
            self.log_connection.log(logging.INFO, debug_msg)

def main():
    ##########################################
    # Run the GUI
    ##########################################
    logger = Logger(logging.INFO)

    fm = FileManager(logger)

    cf = CfAnalysis(fm, logger)

    gui = CfGui(cf, fm, logger)

    gui.run()


if __name__ == "__main__":
    main()


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
# 1. The ledger is a dictionary indexed by account name. The entry
#    in the dictionary is a list of transactions.  Each transaction is a
#    tuple. Each tuple has the following keys:
#            (date, amount, balance, comment)
# 2. I used datetime internally rather than simply date. Its more overhead
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
    def __init__(self):
        self.ledger = {}
        # the following are read from the data file
        self.accounts = []
        self.cash_accounts = []
        self.cds = []
        self.loans = []
        self.bonds = []
        self.funds = []
        self.transfers = []

        d = date.today()
        self.start_date = datetime(d.year, d.month, d.day)
        self.end_date = self.start_date

        ##########################################
        # Set up logger
        ##########################################
        log_format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename="./cf_log.txt",
                            level=logging.INFO,  # default level
                            format=log_format,
                            filemode='a')
        self.logger = logging.getLogger()

        self.logger.log(logging.INFO, "Logger setup complete")

    def init_storage(self):
        self.ledger.clear()
        # the following are read from the data file
        self.accounts.clear()
        self.cash_accounts.clear()
        self.cds.clear()
        self.loans.clear()
        self.bonds.clear()
        self.funds.clear()
        self.transfers.clear()

    def restart(self, tracking_months):
        """Restart by reading in all the data records and recreating 
        all the account"""

        # tracking_months_count can be changes in Setting menu
        self.end_date = self.get_next_date(self.start_date, tracking_months) - \
            timedelta(days=1)

        ##########################################
        # Establish the balance in each cash account
        ##########################################
        self.account_set_up()   # todo - do we set up or calculate a balance in each account

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

    ################################################
    # Support Code
    ################################################
    @staticmethod
    def format_date(date):
        """ Take a datetime and return a string with just date"""
        # TODO is this a dup - what about the format spec
        if type(date) is not datetime:
            raise TypeError("{0}(): Input is not a datetime object".
                            format(util.f_name()))

        return "{0}-{1:02}-{2:02}".format(date.year, date.month, date.day)

    @staticmethod
    def append_register(trans, bal, register):
        """Simply append the transaction 'trans' to the 'register',
        updating the register balance.  Return the updated balance"""

        #  self.logger.info("{0}( {1}, {2:.2f} + {3:.2f})".format(
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

        #  self.logger.info("({0}: {1}, {2} {3})".format(
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
            raise TypeError("{0}(): Input is wrong type".format(util.f_name()))

        # self.logger.info("{0}: Date: {1}".format(util.f_name(),
        #                                         self.format_date(date)))
        date = date.replace(hour=LATEST_TIME)

        latest_bal = reg[0][2]  # opening balance
        for trans in reg:
            if trans[0] > date:
                break
            latest_bal = trans[2]
        #  self.logger.info("{0}: Bal: {1}".format(util.f_name(), latest_bal))
        return float(latest_bal)

    def get_periodic_dates(self, start_date, period, end_date):
        """ Return a list of periodic dates, starting with 'start_date',
        at interval 'period', up to and possibly *including* 'end_date'
        This can go in either the forward or backward direction based
        on the relationship between 'start_date' and 'end_date'"""

        if type(start_date) != datetime or type(end_date) != datetime or \
                type(period) != str:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        #  self.logger.info("{0}() {1}, {2}, {3})".format(
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
        #    self.logger.info"  {0}".format(date))

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

    def credit(self, accnt, amount, date, comment, credit_type=DEPOSIT_TIME):
        """Credit account 'accnt' on 'date' in the amount 'amount' with 'comment'.
        The register balance will be recalculated and updated"""

        #  self.logger.info("{0}() {1}, {2}, {3})".format(
        #    util.f_name(), accnt, amount, self.format_date(date)))

        if type(accnt) != str or type(amount) != float or type(date) != datetime:
            raise TypeError("{0}() : Input type error".format(util.f_name()))

        date = date.replace(hour=credit_type)
        transaction = (date, amount, 0, comment)
        self.ledger[accnt] = self.trans_to_register(transaction,
                                                    self.ledger[accnt])

    def debit(self, accnt, amount, date, comment):
        """Debit account 'accnt' on 'date' in the amount 'amount' with 'comment'"""

        #  self.logger.info("{0}() {1}, {2}, {3})".format(
        #    util.f_name(), accnt, amount, self.format_date(date)))

        if type(accnt) != str or type(amount) != float or type(date) != datetime:
            raise TypeError("{0}() : Input type error".
                            format(util.f_name()))

        date = date.replace(hour=WITHDRAWAL_TIME)
        transaction = (date, -amount, 0, comment)
        self.ledger[accnt] = self.trans_to_register(transaction,
                                                    self.ledger[accnt])

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
        self.accounts.clear()
        self.cash_accounts.clear()
        self.cds.clear()
        self.loans.clear()
        self.bonds.clear()
        self.funds.clear()
        self.transfers.clear()

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

    def get_register(self, account):
        if account in self.ledger:
            return self.ledger[account]
        else:
            raise ValueError("Unknown account: {0}".format(account))

    ###########################################################
    # end of unit test support code
    ###########################################################

    def account_set_up(self):
        """Establish the opening balance of all cash accounts in the ledger"""

        for entry in self.cash_accounts:
            #  self.logger.info("{0} account balance on {1}: ${2} ".format(
            #    entry['account'], entry['opening_date'], entry['balance']))

            # The account record holds the opening date for the cash account
            account_rec = self.get_account_rec(entry['account'])
            start_date = datetime.strptime(account_rec['opening_date'], dfc.DATE_FORMAT)
            start_date = start_date.replace(hour=INITIAL_DEPOSIT_TIME)

            # first entry for this account in the ledger - tuple
            beg_bal = (start_date, 0, entry['balance'],
                       entry['account'] + " Opening Balance")

            # Ensure each dictionary entry is treated as a list of tuples
            self.ledger[entry['account']] = list()
            self.ledger[entry['account']].append(beg_bal)

    def validate_transfer(self, entry):
        if entry['toAccount'] == "income":
            raise ValueError("{0}(): Transfer destination can't be 'income'".
                             format(util.f_name()))
        else:
            if entry['toAccount'] != "expense" and \
                    entry['toAccount'] not in self.ledger:
                raise ValueError("{0}(): Unknown transfer destination: {1}".
                                 format(util.f_name(), entry['toAccount']))
        if entry['fromAccount'] == "expense":
            raise ValueError("{0}(): Transfer source can't be 'expense'".
                             format(util.f_name()))
        else:
            if entry['fromAccount'] != "income" and \
                    entry['fromAccount'] not in self.ledger:
                raise ValueError("{0}(): Unknown transfer source: {1}".
                                 format(util.f_name(), entry['fromAccount']))

    def process_transfers(self):
        """Record all transfers to/from accounts based on the transfer list"""
        self.logger.info("Entries in Transfers list: {0}".
                         format(len(self.transfers)))

        for entry in self.transfers:
            # Fault if invalid
            self.validate_transfer(entry)
            transfer_dates = self.get_dates(entry['frequency'], self.end_date)

            if entry['fromAccount'] == "income":
                opening_date = self.ledger[entry['toAccount']][0][0]
            elif entry['toAccount'] == "expense":
                opening_date = self.ledger[entry['fromAccount']][0][0]
            else:
                # Earliest of to/from accounts
                if self.ledger[entry['fromAccount']][0][0] < \
                        self.ledger[entry['toAccount']][0][0]:
                    opening_date = self.ledger[entry['fromAccount']][0][0]
                else:
                    opening_date = self.ledger[entry['toAccount']][0][0]

            for transDate in transfer_dates:
                if transDate >= opening_date:
                    if entry['fromAccount'] != "income":
                        if transDate >= self.ledger[entry['fromAccount']][0][0]:
                            self.debit(entry['fromAccount'],
                                       float(entry['amount']),
                                       transDate,
                                       "Transfer to " + entry['toAccount'] +
                                       ", Note: " + entry['note'])
                    if entry['toAccount'] != "expense":
                        if transDate >= self.ledger[entry['toAccount']][0][0]:
                            self.credit(entry['toAccount'],
                                        float(entry['amount']),
                                        transDate,
                                        "Transfer from " + entry['fromAccount']
                                        + ", Note: " + entry['note'])

    def process_loans(self):
        """Update each account based on loans on top of balances"""
        self.logger.info("Entries in Loans list: {0}".format(len(self.loans)))

        for entry in self.loans:
            # If the Loan origination date is on or after
            # the opening date,
            # enter both the debit on loan and a credit on maturity.
            # Otherwise, just enter a credit on maturity.

            opening_date = self.ledger[entry['account']][0][0]
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
                self.debit(entry['account'], loan_bal, origination_date,
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

            self.credit(entry['account'], loan_bal, closing_date,
                        "Loan repayment: " + entry['note'],
                        credit_type=SALE_TIME)

    def process_cds(self):
        self.logger.info("Entries in CDs list: {0}".format(len(self.cds)))
        for entry in self.cds:
            # If the CD purchase date is on or after the opening date,
            # enter both the debit on purchase and a credit on maturity.
            # Otherwise, just enter a credit on maturity.
            # Zero's should be entered with the actual purchase price
            # not face value

            opening_date = self.ledger[entry['account']][0][0]
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
                self.debit(entry['account'], purchase_price,
                           purchase_date,
                           "CD purchase, CUSIP: " + entry['cusip'])

            earlier_date = earliest_interest_date
            principal = float(entry['purchase_price']) * float(entry['quantity'])

            for date in interest_dates:
                period = date - earlier_date
                rate = period.days / 365 * float(entry['rate']) / 100
                interest = principal * rate
                self.credit(entry['account'], interest, date,
                            "CD Interest, CUSIP: " + entry['cusip'])
                earlier_date = date

            self.credit(entry['account'], principal, maturity_date,
                        "CD Sale, CUSIP: " + entry['cusip'],
                        credit_type=SALE_TIME)

    def process_bonds(self):
        # TODO - handle a bond call
        #  skip coupons after the call date
        #  calc interest based on outstanding days
        #  calc final payment on call date based on call premium
        #

        self.logger.info("Entries in Bonds list: {0}".format(len(self.bonds)))
        for entry in self.bonds:

            details = self.bond_cash_flow(entry)

            # If the Bond purchase date is on or after the opening date,
            # enter both the debit on purchase and a credit on maturity.
            # Otherwise, just enter a credit on maturity.

            opening_date = self.ledger[entry['account']][0][0]
            for record in details:
                if record['date'] >= opening_date:
                    if record['amount'] < 0:
                        self.debit(entry['account'],
                                   -record['amount'],
                                   record['date'],
                                   record['note'] + ", CUSIP: " + entry['cusip'])
                    else:
                        if record['note'] == 'Bond Sale':
                            self.credit(entry['account'],
                                        record['amount'],
                                        record['date'],
                                        record['note'] + ", CUSIP: " +
                                        entry['cusip'],
                                        credit_type=SALE_TIME)
                        else:
                            self.credit(entry['account'],
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

        self.logger.info("Entries in Funds list: {0}".format(len(self.funds)))

        for entry in self.funds:
            entry_date = datetime.strptime(entry['date'], dfc.DATE_FORMAT)

            self.credit(entry['account'],
                        entry['balance'],
                        entry_date,
                        'balance')
            # TODO - how about interest processing ???

    def apply_interest(self):
        """Apply interest to all cash accounts"""

        self.logger.info("Entries in Cash Accounts: {0}".
                         format(len(self.cash_accounts)))
        for entry in self.cash_accounts:
            start_date = datetime.strptime(entry['interest_date'], "%Y-%m-%d")

            # push all int payment dates after opening date
            account_rec = self.get_account_rec(entry['account'])
            opening_date = datetime.strptime(account_rec['opening_date'], "%Y-%m-%d")
            months_in_period = self.period_to_months(entry['frequency'])
            while opening_date > start_date:
                start_date = self.get_next_date(start_date,
                                                months_in_period)

            interest_dates = self.get_periodic_dates(start_date,
                                                     entry['frequency'],
                                                     self.end_date)
            rate_adj = self.period_to_rate_factor(entry['frequency'])
            rate = (float(entry['rate']) / rate_adj) / 100

            for interest_date in interest_dates:
                bal = self.get_bal_on_date(interest_date,
                                           self.ledger[entry['account']])
                interest = bal * rate

                if interest > 0.0:
                    self.credit(entry['account'], interest, interest_date,
                                "Interest", credit_type=INTEREST_TIME)
                else:
                    # ignore negative interest
                    self.credit(entry['account'], 0.0, interest_date,
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

    def get_cash_accounts(self):
        return self.cash_accounts

        # TODO - can we allow a ca to be deleted? We store the account infor in
		#     the cash. Maybe its just cleaner to store account info in a new
		#     section in the datafile for accounts? Should the account ID be stored
		#     in the account record and not the CA record?  Does every account have
		#     to have a cash account.from

    def get_sorted_accounts_list(self):
        """Return a sorted list of accounts.

        The list contains only the Account Name of the account"""
        accounts = list()

        for record in self.accounts:
            accounts.append(record["account"])
        if accounts:
            accounts.sort()

        return accounts

    def get_accounts(self):
        """Account info is extracted by the file_manager from the data file"""
        return self.accounts

    def get_accounts_with_bond_import_methods(self):
        return []

    def get_accounts_with_import_methods(self):
        """Return accounts that have an import method specified

        :return: A list of account records. Each record includes the
                 account, account_id and the update_method.
        """
        account_data = []
        for rec in self.accounts:
            if rec['update_method'] != "Manual":
                account_data.append({'account': rec['account'],
                'account_id': rec['account_id'],
                'update_method': rec['update_method']})

        return account_data

    def get_account_id_map(self):
        """Map account_id to account

        :return: dictionary where account_id is the key to get account_name
        """
        id_map = {}
        for account in self.accounts:
            id_map[account['account_id']] = account['account_name']
        return id_map

    def get_account_rec(self, account):
        for rec in self.accounts:
            if rec['account'] == account:
                return rec
        return None

    def account_create(self, rec):
        """User has created a new account. Create the corresponding cash account"""
        ca_rec = dfc.ca_new_rec
        ca_rec['account'] = rec['account']
        ca_rec['interest_date'] = rec['opening_date']
        self.cash_accounts.append(ca_rec)

    def account_delete(self, account):
        for rec in reversed(self.cash_accounts):
            if rec['account'] == account:
                self.cash_accounts.remove(rec)
        for rec in reversed(self.cds):
            if rec['account'] == account:
                self.cds.remove(rec)
        for rec in reversed(self.loans):
            if rec['account'] == account:
                self.loans.remove(rec)
        for rec in reversed(self.bonds):
            if rec['account'] == account:
                self.bonds.remove(rec)
        for rec in reversed(self.funds):
            if rec['account'] == account:
                self.funds.remove(rec)
        for rec in reversed(self.transfers):
            if rec['fromAccount'] == account or rec['toAccount'] == account:
                self.transfers.remove(rec)

    def account_name_changed(self, old_name, new_name):
        for rec in self.cash_accounts:
            if rec['account'] == old_name:
                rec['account'] = new_name
        for rec in self.cds:
            if rec['account'] == old_name:
                rec['account'] = new_name
        for rec in self.loans:
            if rec['account'] == old_name:
                rec['account'] = new_name
        for rec in self.bonds:
            if rec['account'] == old_name:
                rec['account'] = new_name
        for rec in self.funds:
            if rec['account'] == old_name:
                rec['account'] = new_name
        for rec in self.transfers:
            if rec['fromAccount'] == old_name:
                rec['fromAccount'] = new_name
            if rec['toAccount'] == old_name:
                rec['toAccount'] = new_name





    def get_cds(self):
        return self.cds

    def get_loans(self):
        return self.loans

    def get_bonds(self):
        return self.bonds

    def get_funds(self):
        return self.funds

    def get_transfers(self):
        return self.transfers

    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date

    def update_account(self, account_id, account_details):
        """ todo - when is this called and why is it called - looks like its called from import_account

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

    def log(self, lvl, debug_msg):
        if lvl == logging.CRITICAL:
            self.logger.critical(debug_msg)
        elif lvl == logging.ERROR:
            self.logger.error(debug_msg)
        elif lvl == logging.WARNING:
            self.logger.warning(debug_msg)
        elif lvl == logging.INFO:
            self.logger.info(debug_msg)
        elif lvl == logging.DEBUG:
            self.logger.debug(debug_msg)
        else:
            self.logger.info(debug_msg)

    @staticmethod
    def get_new_rec(instrument_type):
        """Return an new data file record based on instrument_type.

        The new record will have all the keys appropriate for 
        the instrument_type and default values appropriate for the key.
        """
        if instrument_type == 'account':
            return dfc.acc_new_rec.copy()
        elif instrument_type == 'ca':
            return dfc.ca_new_rec.copy()
        elif instrument_type == 'bond':
            return dfc.bond_new_rec.copy()
        elif instrument_type == 'fund':
            return dfc.fund_new_rec.copy()
        elif instrument_type == 'cd':
            return dfc.cd_new_rec.copy()
        elif instrument_type == 'loan':
            return dfc.loan_new_rec.copy()
        elif instrument_type == 'transfer':
            new_rec = dfc.xfer_new_rec.copy()
            new_rec['frequency'] = Occurrences.default_occurrence_spec()
            return new_rec
        else:
            raise TypeError("Invalid instrument_type: {}".format(instrument_type))

    # TODO - the following needs work. For weekly, I need to add code to
    # get_periodic.
    def get_account_data(self, account_name, granularity,
                         start_date, end_date):
        """Get account data for graphing

        :param account_name:
        :param granularity: 'monthly','annually','semiannually','quarterly'
                Issue - month is the lowest granularity
        :param start_date:
        :param end_date:
        :return:
        """
        #    annual use 12/31
        #    monthly - use the 31
        #    weekly - I may need to add code to get_periodic
        # then get the balance for each end date and write a summary_register

        data = []
        if account_name in self.ledger.keys():
            account = self.ledger[account_name]
            dates = self.get_periodic_dates(start_date, granularity.lower(),
                                            end_date)
            for date in dates:
                bal = self.get_bal_on_date(date, account)
                # print("Date {} = {}".format(date,bal))
                data.append((date, bal))

        return data


def main():
    ##########################################
    # Run the GUI
    ##########################################
    cf = CfAnalysis()

    gui = CfGui(cf)

    gui.run()


if __name__ == "__main__":
    main()

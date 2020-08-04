#
# Author:  Greg Glezman
#
# SCCSID :  "%W% %G%
#
# Copyright (c) 2018 G.Glezman.  All Rights Reserved.
#
# To Run: 
#     python3 -m unitest test_cf.py
#           or 
#

import unittest
import datetime
# import sys
from cf import CfAnalysis


class TestCF(unittest.TestCase): 

    START_DATE = datetime.datetime(2018, 1, 20)
    EARLY_END_DATE = datetime.datetime(2019, 2, 28)
    END_DATE = datetime.datetime(2020, 2, 28)
    
    DATE = datetime.datetime(2018, 1, 31)
    N_DATE_1 = datetime.datetime(2018, 2, 28)
    N_DATE_2 = datetime.datetime(2018, 3, 31)
    N_DATE_3 = datetime.datetime(2018, 4, 30)
    N_DATE_4 = datetime.datetime(2018, 5, 31)
    N_DATE_5 = datetime.datetime(2018, 6, 30)
    N_DATE_6 = datetime.datetime(2018, 7, 31)
    N_DATE_7 = datetime.datetime(2018, 8, 31)
    N_DATE_8 = datetime.datetime(2018, 9, 30)
    N_DATE_9 = datetime.datetime(2018, 10, 31)
    N_DATE_10 = datetime.datetime(2018, 11, 30)
    N_DATE_11 = datetime.datetime(2018, 12, 31)
    N_DATE_12 = datetime.datetime(2019, 1, 31)
    N_DATE_13 = datetime.datetime(2019, 2, 28)
    N_DATE_60 = datetime.datetime(2023, 1, 31)

    DEFAULT_TRACKING_MONTHS = 24

    def test_types(self):     # method name must begin with "test_"
        # make sure the function validates types
        valid_datetime = datetime.datetime(2018, 2, 7)
        invalid_datetime = datetime.date(2018, 2, 7)
        i = int(1)
        f = float(0)
        s = str("test")
        t = (0, 1, 2, 3)
        lst = [1, 2, 3]

        cf = CfAnalysis()
        self.assertRaises(TypeError, cf.format_date, invalid_datetime)
        
        self.assertRaises(TypeError, cf.append_register, i, f, lst)
        self.assertRaises(TypeError, cf.append_register, t, i, lst)
        self.assertRaises(TypeError, cf.append_register, t, f, t)

        self.assertRaises(TypeError, cf.trans_to_register, f, lst)
        self.assertRaises(TypeError, cf.trans_to_register, t, t)

        self.assertRaises(TypeError, cf.get_bal_on_date, invalid_datetime, lst)
        self.assertRaises(TypeError, cf.get_bal_on_date, valid_datetime, t)

        self.assertRaises(TypeError, cf.get_periodic_dates, invalid_datetime, 
                          s, valid_datetime)
        self.assertRaises(TypeError, cf.get_periodic_dates, valid_datetime, i, 
                          valid_datetime)
        self.assertRaises(TypeError, cf.get_periodic_dates, valid_datetime, 
                          s, invalid_datetime)

        self.assertRaises(TypeError, cf.get_next_date, invalid_datetime, i)
        self.assertRaises(TypeError, cf.get_next_date, valid_datetime, s)

        self.assertRaises(TypeError, cf.debit, i, f, valid_datetime, s)
        self.assertRaises(TypeError, cf.debit, s, i, valid_datetime, s)
        self.assertRaises(TypeError, cf.debit, s, f, invalid_datetime, s)

        self.assertRaises(TypeError, cf.credit, i, f, valid_datetime, s)
        self.assertRaises(TypeError, cf.credit, s, i, valid_datetime, s)
        self.assertRaises(TypeError, cf.credit, s, f, invalid_datetime, s)

        self.assertRaises(TypeError, cf.period_to_months, f)
        self.assertRaises(TypeError, cf.period_to_months, valid_datetime)

        self.assertRaises(TypeError, cf.period_to_rate_factor, f)
        self.assertRaises(TypeError, cf.period_to_rate_factor, valid_datetime)

    def test_append_register(self): 
        pass

    def test_trans_to_register(self): 
        pass
    
    def test_get_ball_on_date(self): 
        pass

    def test_get_periodic_dates(self): 
        cf = CfAnalysis()

        self.assertRaises(ValueError, cf.get_periodic_dates, self.START_DATE, 
                          "garbage", self.END_DATE)

        ###############################################
        # Test date generation in the forward direction
        ###############################################
        result = cf.get_periodic_dates(self.START_DATE, 'once', self.END_DATE)
        self.assertEqual(result, [self.START_DATE])

        # Test some montly groups
        thirteen_month_list = [self.DATE,     self.N_DATE_1, self.N_DATE_2, 
                               self.N_DATE_3, self.N_DATE_4, self.N_DATE_5,
                               self.N_DATE_6, self.N_DATE_7, self.N_DATE_8, 
                               self.N_DATE_9, self.N_DATE_10, self.N_DATE_11, 
                               self.N_DATE_12, self.N_DATE_13]
        result = cf.get_periodic_dates(self.DATE, 'monthly', 
                                       self.EARLY_END_DATE)
        self.assertEqual(result, thirteen_month_list)

        # Test some quarterly groups
        five_quarterly_list = [self.DATE, self.N_DATE_3, self.N_DATE_6, 
                               self.N_DATE_9, self.N_DATE_12]
        result = cf.get_periodic_dates(self.DATE, 'quarterly', 
                                       self.EARLY_END_DATE)
        self.assertEqual(result, five_quarterly_list)

        # Test a semi-annual group
        s_date_1 = datetime.datetime(2018, 7, 20)
        s_date_2 = datetime.datetime(2019, 1, 20)
        s_date_3 = datetime.datetime(2019, 7, 20)
        s_date_4 = datetime.datetime(2020, 1, 20)
        five_semi_list = [self.START_DATE, s_date_1, s_date_2, 
                          s_date_3, s_date_4]
        result = cf.get_periodic_dates(self.START_DATE, 'semi-annual', 
                                       self.END_DATE)
        self.assertEqual(result, five_semi_list)

        # Annual testing
        a_date_1 = datetime.datetime(2019, 1, 20)
        a_date_2 = datetime.datetime(2020, 1, 20)
        three_annual_list = [self.START_DATE, a_date_1, a_date_2]
        result = cf.get_periodic_dates(self.START_DATE, 'annual', 
                                       self.END_DATE)
        self.assertEqual(result, three_annual_list)

        ################################################
        # Test date generation in the backward direction
        ################################################

        # Test some montly groups
        thirteen_month_list = [self.DATE,     self.N_DATE_1,  self.N_DATE_2, 
                               self.N_DATE_3, self.N_DATE_4,  self.N_DATE_5, 
                               self.N_DATE_6, self.N_DATE_7,  self.N_DATE_8, 
                               self.N_DATE_9, self.N_DATE_10, self.N_DATE_11, 
                               self.N_DATE_12]
        
        result = cf.get_periodic_dates(self.N_DATE_12, 'monthly', self.DATE)
        self.assertEqual(result, thirteen_month_list)
        
        # Test some quarterly groups
        date_1 = datetime.datetime(2018, 11, 28)
        date_2 = datetime.datetime(2018, 8, 28)
        date_3 = datetime.datetime(2018, 5, 28)
        four_quarterly_list = [self.N_DATE_1, date_3, date_2, date_1, 
                               self.N_DATE_13]
        result = cf.get_periodic_dates(self.N_DATE_13, 'quarterly', self.DATE)
        self.assertEqual(result, four_quarterly_list)
        
        # Test a semi-annual group
        three_semi_list = [self.DATE, self.N_DATE_6, self.N_DATE_12]
        result = cf.get_periodic_dates(self.N_DATE_12, 'semi-annual', self.DATE)
        self.assertEqual(result, three_semi_list)

        result = cf.get_periodic_dates(self.N_DATE_12, 'semi-annual', 
                                       self.START_DATE)
        self.assertEqual(result, three_semi_list)

        # Annual testing
        three_annual_list = [self.N_DATE_1, self. EARLY_END_DATE, self.END_DATE]
        result = cf.get_periodic_dates(self.END_DATE, 'annual', self.START_DATE)
        self.assertEqual(result, three_annual_list)

    def test_get_next_date(self): 
        
        ################################################
        # Test date generation in the forward direction
        ################################################
        cf = CfAnalysis()

        # a month at a time out
        result = cf.get_next_date(self.DATE, 1)
        self.assertEqual(result, self.N_DATE_1)
        
        result = cf.get_next_date(self.DATE, 2)
        self.assertEqual(result, self.N_DATE_2)
        
        result = cf.get_next_date(self.DATE, 3)
        self.assertEqual(result, self.N_DATE_3)
        
        result = cf.get_next_date(self.DATE, 4)
        self.assertEqual(result, self.N_DATE_4)
        
        result = cf.get_next_date(self.DATE, 5)
        self.assertEqual(result, self.N_DATE_5)

        result = cf.get_next_date(self.DATE, 10)
        self.assertEqual(result, self.N_DATE_10)

        result = cf.get_next_date(self.DATE, 12)
        self.assertEqual(result, self.N_DATE_12)

        # five years out
        result = cf.get_next_date(self.DATE, 60)
        self.assertEqual(result, self.N_DATE_60)

    def test_get_previous_date(self): 
        
        ################################################
        # Test date generation in the backward direction
        ################################################
        cf = CfAnalysis()

        # a month back at a time out
        result = cf.get_previous_date(self.N_DATE_12, 1)
        self.assertEqual(result, self.N_DATE_11)
        
        result = cf.get_previous_date(self.N_DATE_12, 2)
        self.assertEqual(result, self.N_DATE_10)
        
        result = cf.get_previous_date(self.N_DATE_12, 3)
        self.assertEqual(result, self.N_DATE_9)
        
        result = cf.get_previous_date(self.N_DATE_12, 4)
        self.assertEqual(result, self.N_DATE_8)
        
        result = cf.get_previous_date(self.N_DATE_12, 5)
        self.assertEqual(result, self.N_DATE_7)

        result = cf.get_previous_date(self.N_DATE_12, 10)
        self.assertEqual(result, self.N_DATE_2)

        result = cf.get_previous_date(self.N_DATE_12, 12)
        self.assertEqual(result, self.DATE)
        
        # five years back
        result = cf.get_previous_date(self.N_DATE_60, 60)
        self.assertEqual(result, self.DATE)

    def test_credit(self): 
        pass

    def test_debit(self): 
        pass
        
    def test_period_to_months(self): 
        cf = CfAnalysis()

        months = cf.period_to_months('once') 
        self.assertEqual(months, 999)
        
        months = cf.period_to_months('monthly') 
        self.assertEqual(months, 1)
        
        months = cf.period_to_months('annual') 
        self.assertEqual(months, 12)
        
        months = cf.period_to_months('semi-annual') 
        self.assertEqual(months, 6)
        
        months = cf.period_to_months('quarterly') 
        self.assertEqual(months, 3)

        self.assertRaises(ValueError, cf.period_to_months, 'unknown')

    def test_period_to_rate_factor(self): 
        cf = CfAnalysis()

        factor = cf.period_to_rate_factor('monthly') 
        self.assertEqual(factor, 12)
        
        factor = cf.period_to_rate_factor('annual') 
        self.assertEqual(factor, 1)
        
        factor = cf.period_to_rate_factor('semi-annual') 
        self.assertEqual(factor, 2)
        
        factor = cf.period_to_rate_factor('quarterly') 
        self.assertEqual(factor, 4)

        self.assertRaises(ValueError, cf.period_to_rate_factor, 'once')
        self.assertRaises(ValueError, cf.period_to_rate_factor, 'unknown')

    def test_interest_1(self): 
        # Basic cash account functions
        # - establish and verify opening balance
        # - verify interest entries
        # includes an interest date prior to opening

        cf = CfAnalysis()

        opening_bal = 1000.0
        rate = 12
        
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntName", "balance": opening_bal,
                                 'rate': rate, 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntName"))
        self.assertEqual(bal, opening_bal)
        # one month at 12% => 1 %
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 25), 
                                 cf.get_register("accntName"))
        self.assertEqual(bal, opening_bal)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 26), 
                                 cf.get_register("accntName"))
        self.assertEqual(bal, 1010)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 27), 
                                 cf.get_register("accntName"))
        self.assertEqual(bal, 1010)
        
        # two month at 12% 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 25), 
                                 cf.get_register("accntName"))
        self.assertEqual(bal, 1010)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 26), 
                                 cf.get_register("accntName"))
        self.assertEqual(bal, 1020.1)

        bal = cf.get_bal_on_date(datetime.datetime(2018, 4, 26), 
                                 cf.get_register("accntName"))
        self.assertAlmostEqual(bal, 1030.30, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 4, 27), 
                                 cf.get_register("accntName"))
        self.assertAlmostEqual(bal, 1030.30, 2)
        
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 26), 
                                 cf.get_register("accntName"))
        self.assertAlmostEqual(bal, 1040.60, 2)

        bal = cf.get_bal_on_date(datetime.datetime(2018, 6, 26), 
                                 cf.get_register("accntName"))
        self.assertAlmostEqual(bal, 1051.01, 2)

        bal = cf.get_bal_on_date(datetime.datetime(2018, 7, 26), 
                                 cf.get_register("accntName"))
        self.assertAlmostEqual(bal, 1061.52, 2)

    def test_cd_purchase_1(self): 
        cf = CfAnalysis()

        # Scenario testing
        # - set up an account with some cash and buy a CD
        #   then verify balance after purchase, and interest on maturity
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntCd", 
                                 "balance": 10000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_cds({'account': "accntCd", "purchase_price": 1000.0, 
                       'quantity': 5, 'rate': 1.7, 
                       'purchase_date': "2018-02-16", 
                       'maturity_date': "2018-08-15", 
                       'frequency': "once", 'cusip': "CDCDCD"})
        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # before CD purchase
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntCd"))
        self.assertEqual(bal, 10000)

        # after CD purcahse
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 16), 
                                 cf.get_register("accntCd"))
        self.assertEqual(bal, 5000)

        # before CD matures
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 14), 
                                 cf.get_register("accntCd"))
        self.assertEqual(bal, 5000)
        
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 15), 
                                 cf.get_register("accntCd"))
        self.assertAlmostEqual(bal, 10041.92, 2)

    def test_loan_3(self): 

        cf = CfAnalysis()

        # Scenario testing
        # - set up an account with some cash and make a loan
        #   then verify balance after the loan, as well as the repayment
        # no compounding
        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntLoan", 
                                 'balance': 10000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_loans({'account': "accntLoan", 
                         "balance": 5000.00, 'rate': 3.0, 
                         'orig_date': "2018-02-16", 'payoff_date': "2018-08-15",
                         'frequency': "once", 'note': "Loan"})
        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # before the loan
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntLoan"))
        self.assertEqual(bal, 10000)

        # after the loan
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 16), 
                                 cf.get_register("accntLoan"))
        self.assertEqual(bal, 5000)

        # before repayment
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 14), 
                                 cf.get_register("accntLoan"))
        self.assertEqual(bal, 5000)

        # after repayment
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 15), 
                                 cf.get_register("accntLoan"))
        self.assertAlmostEqual(bal, 10073.97, 2)

    def test_bond_purchase_1(self): 

        cf = CfAnalysis()

        # Scenario testing
        # - set up an account with some cash and buy some bonds
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntBond", 
                                 "balance": 100000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        # maturity_date.day > purchase_date.day
        cf.append_bonds({'account': "accntBond", 
                         'bond_price': 102.181, 'quantity': 5, 'coupon': 5.25, 
                         'fee': 10, 'purchase_date': "2018-02-14", 
                         'maturity_date': "2018-11-15", 
                         'frequency': "semi-annual", 'cusip': "Bond_1", 
                         'call_date': 'None', 'call_price': 0.0})
        # Same month (maturity_date and purchase_date)
        cf.append_bonds({'account': "accntBond", 
                         'bond_price': 99.181, 'quantity': 5, 'coupon': 2.75, 
                         'fee': 5, 'purchase_date': "2018-03-01", 
                         'maturity_date': "2018-03-20", 
                         'frequency': "semi-annual", 'cusip': "Bond_2", 
                         'call_date': 'None', 'call_price': 0.0})
        # maturity_date.day < purchase_date.day
        cf.append_bonds({'account': "accntBond", 
                         'bond_price': 100.227, 'quantity': 11, 'coupon': 4.66, 
                         'fee': 11, 'purchase_date': "2018-04-15", 
                         'maturity_date': "2018-11-01", 
                         'frequency': "semi-annual", 'cusip': "Bond_3", 
                         'call_date': 'None', 'call_price': 0.0})

        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # before the Bond_1 purchase
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntBond"))
        self.assertEqual(bal, 100000)

        # After the bond_1 purchase - includes accrued interest and bond fees
        # Bond Cost = 102.181 * 10 * 5 = 5109.05
        # Fees                         =  10.00
        # Accruued Interest            =  65.45
        #                                5184.50
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 14), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 94816.054, 2) 

        # After the bond_2 purchase - includes accrued interest and bond fees
        # Bond Cost = 99.181 * 10 * 5 = 4959.05
        # Fees                         =   5.00
        # Accruued Interest            =  61.03
        #                                 5025.08
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 2), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 89790.511, 3)

        # After bond_2 repayment
        # Interest 68.75 + 5000 = 5068.75
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 21), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 94859.261, 3)

        # After the bond_3 purchase - includes accrued interest and bond fees
        # Bond Cost = 100.227 * 10 * 11 = 11024.97
        # Fees                          =   11.00
        # Accruued Interest             =  231.72
        #                                 11267.69
        bal = cf.get_bal_on_date(datetime.datetime(2018, 4, 15), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 83589.773, 3)

        # After bond_3 first coupon
        # Interest =                 = 256.30
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 1), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 83846.073, 3)
        
        # After bond_1 first coupon
        # Interest = 5000 * 5.25/100 / 2 = 131.25
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 15), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 83977.323, 3)

        # After bond_3 repayment
        # interest 256.30 + 11000 = 11256.30
        bal = cf.get_bal_on_date(datetime.datetime(2018, 11, 1), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 95233.623, 3)

        # After bond_1 repayment
        # interest 131.25 + 5000  = 5131.25
        bal = cf.get_bal_on_date(datetime.datetime(2018, 11, 15), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 100364.873, 3)

    def test_bond_purchase_2(self): 

        cf = CfAnalysis()

        # Scenario testing
        # - set up an account with some cash and buy some bonds
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntBond", 
                                 "balance": 100000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        # maturity_date.day > purchase_date.day
        cf.append_bonds({'account': "accntBond", 
                         'bond_price': 100, 'quantity': 5, 'coupon': 5, 
                         'fee': 5, 'purchase_date': "2018-05-10", 
                         'maturity_date': "2018-11-15", 
                         'frequency': "semi-annual", 'cusip': "Bond_1", 
                         'call_date': '2018-05-30', 'call_price': 100.0})

        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # before the Bond_1 purchase
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntBond"))
        self.assertEqual(bal, 100000)

        # After the bond_1 purchase - includes accrued interest and bond fees
        # Bond Cost = 100 * 10 * 5  = 5000.00
        # Fees                      =   5.00
        # Accruued Interest         = 120.55
        #                             5125.55
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 11), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 94873.472, 3)

        # After bond_1 first coupon
        # Interest = 5000 * 5.0/100 / 2 = 125
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 15), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 94998.472, 3)

        # After bond_1 call
        # interest 10.42 + 5000  = 5010.42
        bal = cf.get_bal_on_date(datetime.datetime(2018, 6, 1), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 100008.889, 3)
        '''
        bal = cf.get_bal_on_date(datetime.datetime(2018, 11, 15), 
                                  cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 100124.452, 3)
        '''
        
    def test_bond_purchase_3(self): 

        cf = CfAnalysis()

        # Scenario testing
        # - set up an account with some cash and buy some bonds
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntBond", 
                                 "balance": 100000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        # maturity_date.day > purchase_date.day
        cf.append_bonds({'account': "accntBond", 
                         'bond_price': 100, 'quantity': 5, 'coupon': 5, 
                         'fee': 5, 'purchase_date': "2018-05-10", 
                         'maturity_date': "2019-01-01", 
                         'frequency': "semi-annual", 'cusip': "Bond_2", 
                         'call_date': 'None', 'call_price': 0.0})

        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # before the Bond_1 purchase
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntBond"))
        self.assertEqual(bal, 100000)

        # After the bond_1 purchase - includes accrued interest and bond fees
        # Bond Cost = 100 * 10 * 5  = 5000.00
        # Fees                      =   5.00
        # Accruued Interest         =  88.36
        #                             5093.36
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 10), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 94905.417, 3)

        # After bond_1 first coupon
        # Interest = 5000 * 5.0/100 / 2 = 125
        bal = cf.get_bal_on_date(datetime.datetime(2018, 7, 1), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 95030.417, 3)

        # After bond_1 repayment
        # interest 125 + 5000  = 5125.00
        bal = cf.get_bal_on_date(datetime.datetime(2019, 1, 1), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 100155.417, 3)

    def test_bond_purchase_4(self): 

        cf = CfAnalysis()

        # Scenario testing
        # - set up an account with some cash and buy some bonds
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntBond", 
                                 "balance": 100000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        # maturity_date.day > purchase_date.day
        cf.append_bonds({'account': "accntBond", 
                         'bond_price': 100, 'quantity': 5, 'coupon': 5, 
                         'fee': 5, 'purchase_date': "2018-12-11", 
                         'maturity_date': "2019-07-15", 
                         'frequency': "semi-annual", 'cusip': "Bond_2", 
                         'call_date': 'None', 'call_price': 0.0})

        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # before the Bond_1 purchase
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntBond"))
        self.assertEqual(bal, 100000)

        # After the bond_1 purchase - includes accrued interest and bond fees
        # Bond Cost = 100 * 10 * 5  = 5000.00
        # Fees                      =   5.00
        # Accruued Interest         = 102.05
        #                             5107.05
        bal = cf.get_bal_on_date(datetime.datetime(2018, 12, 11), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 94893.611, 3)

        # After bond_1 first coupon
        # Interest = 5000 * 5.0/100 / 2 = 125
        bal = cf.get_bal_on_date(datetime.datetime(2019, 1, 15), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 95018.611, 3)

        # After bond_1 repayment
        # interest 125 + 5000  = 5125.00
        bal = cf.get_bal_on_date(datetime.datetime(2019, 7, 15), 
                                 cf.get_register("accntBond"))
        self.assertAlmostEqual(bal, 100143.611, 3)

    def test_transfers_0(self): 
        """Transfer Error condition tetsing.

        - expense as the source
        - income as a destination
        - unknown destination account
        - unknown source account
        """

        cf = CfAnalysis()

        # Bad transfer data
        #  expense as a source
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntRunning", 
                                 "balance": 10000, 'rate': 2.0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})

        cf.append_transfers({'fromAccount': "expense",
                             'toAccount': "accntRunning", 'date': "2018-01-14",
                             'amount': 100.00, 'frequency': "monthly",
                             'note': "misc"})
        cf.account_set_up()
        self.assertRaises(ValueError, cf.process_transfers)

        #  income as a destination
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntRunning", 
                                 "balance": 10000, 'rate': 2.0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})

        cf.append_transfers({'fromAccount': "accntRunning",
                             'toAccount': "income", 'date': "2018-01-14",
                             'amount': 100.00, 'frequency': "monthly",
                             'note': "misc"})
        cf.account_set_up()
        self.assertRaises(ValueError, cf.process_transfers)

        # unknown destination account
        cf.reset_ledger()
        cf.append_cash_accounts({'account': "accntRunning", 
                                 "balance": 10000, 'rate': 2.0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})

        cf.append_transfers({'fromAccount': "income",
                             'toAccount': "garbageAccountName",
                             'date': "2018-01-14", 'amount': 100.00,
                             'frequency': "monthly", 'note': "misc"})
        cf.account_set_up()
        self.assertRaises(ValueError, cf.process_transfers)

        # unknown source account
        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntRunning", 
                                 "balance": 10000, 'rate': 2.0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})

        cf.append_transfers({'fromAccount': "garbageAccountName",
                             'toAccount': "expense",
                             'date': "2018-01-14", 'amount': 100.00,
                             'frequency': "monthly", 'note': "misc"})
        cf.account_set_up()
        self.assertRaises(ValueError, cf.process_transfers)

    def test_transfers_1(self):
        """Transfer Scenario - Transfers in from income plus interest

        - interest is accued in the destination account.
        - the first transfer is before the destination account is opened.
          That transfer is dicarded.
        - subsequent transfers credit the destiination account.
        """
        cf = CfAnalysis()

        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntRunning", 
                                 "balance": 10000, 'rate': 2.0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})

        cf.append_transfers({'fromAccount': "income",
                             'toAccount': "accntRunning", 'date': "2018-01-14",
                             'amount': 100.00,
                             'frequency': "2018-01-14;None;monthly;1",
                             'note': "misc"})

        cf.restart(self.DEFAULT_TRACKING_MONTHS)
                          
        # opening bal
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntRunning"))
        self.assertEqual(bal, 10000)

        # transfer
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 14), 
                                 cf.get_register("accntRunning"))
        self.assertAlmostEqual(bal, 10100, 2)

        # interest
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 26), 
                                 cf.get_register("accntRunning"))
        self.assertAlmostEqual(bal, 10116.83, 2)

        # transfer
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 14), 
                                 cf.get_register("accntRunning"))
        self.assertAlmostEqual(bal, 10216.83, 2)

        # interest
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 26), 
                                 cf.get_register("accntRunning"))
        self.assertAlmostEqual(bal, 10233.86, 2)

        bal = cf.get_bal_on_date(datetime.datetime(2019, 3, 27), 
                                 cf.get_register("accntRunning"))
        self.assertAlmostEqual(bal, 11653.51, 2)

    def test_transfers_2(self): 
        """Transfer Scenario - Transfers between accounts.

        - Neither source not destination accounts accrue interest
        - first transfer is before either account is opened:  discarded
        - second transfer is after src account is opened (debit) but
          before destination account is opend (no credit)
        - subsequent transfer debit the src account and credit the dest account 
        """

        cf = CfAnalysis()
        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntSrc", 
                                 "balance": 10000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_cash_accounts({'account': "accntDst", 
                                 "balance": 100, 'rate': 0, 
                                 'opening_date': "2018-02-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-01-14",
                             'amount': 100.00,
                             'frequency': "2018-01-14;None;monthly;1",
                             'note': "misc"})

        cf.restart(self.DEFAULT_TRACKING_MONTHS)
                          
        # opening bal - src
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntSrc"))
        self.assertEqual(bal, 10000)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 14), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 9900, 2)

        # opening bal - dst
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 28), 
                                 cf.get_register("accntDst"))
        self.assertEqual(bal, 100)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 14), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 9800, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 14), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 200, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 20), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 8500, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 20), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 1500, 2)

    def test_transfers_3(self): 
        """Transfer Scenario - Transfers out to expenses.

        - The source account does NOT accrue interest. (credit)
        - first transfer is before the account is opened:  discarded
        - second and subsequent transfers are after the account is opened
          hence tthey debit the account.
        """

        cf = CfAnalysis()
        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntSinking", 
                                 "balance": 10000, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        
        cf.append_transfers({'fromAccount': "accntSinking",
                             'toAccount': "expense", 'date': "2018-01-14",
                             'amount': 100.00,
                             'frequency': "2018-01-14;None;monthly;1",
                             'note': "misc"})
        
        cf.restart(self.DEFAULT_TRACKING_MONTHS)

        # opening bal
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntSinking"))
        self.assertEqual(bal, 10000)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 14), 
                                 cf.get_register("accntSinking"))
        self.assertAlmostEqual(bal, 9900, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 14), 
                                 cf.get_register("accntSinking"))
        self.assertAlmostEqual(bal, 9800, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 20), 
                                 cf.get_register("accntSinking"))
        self.assertAlmostEqual(bal, 8500, 2)

    def test_transfers_4(self): 
        """Transfer Scenario - Transfers between accounts.

        - Neither source not destination accounts accrue interest.
        - first transfer is before either account is opened:  discarded
        - second transfer is after dst account is opened (credit) but
          before source account is opend (no debit)
        - subsequent transfer debit the src account and credit the dest account 
        """
        cf = CfAnalysis()
        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntSrc", 
                                 "balance": 10000, 'rate': 0, 
                                 'opening_date': "2018-02-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_cash_accounts({'account': "accntDst", 
                                 "balance": 100, 'rate': 0, 
                                 'opening_date': "2018-01-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-01-14",
                             'amount': 100.00,
                             'frequency': "2018-01-14;None;monthly;1",
                             'note': "misc"})
        cf.restart(self.DEFAULT_TRACKING_MONTHS)
                          
        # opening bal - dst
        bal = cf.get_bal_on_date(datetime.datetime(2018, 1, 28), 
                                 cf.get_register("accntDst"))
        self.assertEqual(bal, 100)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 14), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 200, 2)

        # opening bal - src
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 28), 
                                 cf.get_register("accntSrc"))
        self.assertEqual(bal, 10000)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 14), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 9900, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 14), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 300, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 20), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 8600, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 20), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 1600, 2)

    def test_transfers_5(self): 
        """Transfer Scenario - Transfers between accounts.

        - Neither source not destination accounts accrue interest.
        - All transfers are after the src and dest accounts are opened.
        - Transfer frequencies include
            - monthly
            - quarterly
            - semi-annually
            - annually
            - once
        """
        cf = CfAnalysis()
        cf.reset_ledger()

        cf.append_cash_accounts({'account': "accntSrc", 
                                 "balance": 100000, 'rate': 0, 
                                 'opening_date': "2018-02-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_cash_accounts({'account': "accntDst", 
                                 "balance": 100, 'rate': 0, 
                                 'opening_date': "2018-02-28", 
                                 'interest_date': "2018-01-26", 
                                 'frequency': "monthly", 'note': "note"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-03-01",
                             'amount': 10.00,
                             'frequency': "2018-03-01;None;monthly;1",
                             'note': "monthly"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-03-05",
                             'amount': 12.00,
                             'frequency': "2018-03-05;None;quarterly",
                             'note': "quarterly"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-04-20",
                             'amount': 18.00,
                             'frequency': "2018-04-20;None;semi-annually",
                             'note': "semiannual"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-05-07",
                             'amount': 19.00,
                             'frequency': "2018-05-07;None;annually",
                             'note': "annual"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-07-05",
                             'amount': 23.00,
                             'frequency': "2018-07-05;2018-07-05;once",
                             'note': "once"})
        cf.append_transfers({'fromAccount': "accntSrc",
                             'toAccount': "accntDst", 'date': "2018-08-09",
                             'amount': 23.00,
                             'frequency': "2018-08-09;2018-08-09;once",
                             'note': "once"})
        cf.restart(self.DEFAULT_TRACKING_MONTHS)
                          
        # opening bal - src
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 28), 
                                 cf.get_register("accntSrc"))
        self.assertEqual(bal, 100000)

        # opening bal - dst
        bal = cf.get_bal_on_date(datetime.datetime(2018, 2, 28), 
                                 cf.get_register("accntDst"))
        self.assertEqual(bal, 100)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99990, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 110, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99978, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 3, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 122, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 4, 22), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99950, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 4, 22), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 150, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99940, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 160, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 8), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99921, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 5, 8), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 179, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 6, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99911, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 6, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 189, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 6, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99899, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 6, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 201, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 7, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99889, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 7, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 211, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 7, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99866, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 7, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 234, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99856, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 244, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 10), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99833, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 8, 10), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 267, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 9, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99823, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 9, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 277, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 9, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99811, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 9, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 289, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 10, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99801, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 10, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 299, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 10, 21), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99783, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 10, 21), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 317, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 11, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99773, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 11, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 327, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 12, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99763, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 12, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 337, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2018, 12, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99751, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2018, 12, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 349, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 1, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99741, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 1, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 359, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 2, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99731, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 2, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 369, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 3, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99721, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 3, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 379, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 3, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99709, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 3, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 391, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99699, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 401, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 21), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99681, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 4, 21), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 419, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 5, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99671, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 5, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 429, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 5, 8), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99652, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 5, 8), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 448, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 6, 2), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99642, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 6, 2), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 458, 2)

        # transfer 
        bal = cf.get_bal_on_date(datetime.datetime(2019, 6, 6), 
                                 cf.get_register("accntSrc"))
        self.assertAlmostEqual(bal, 99630, 2)
        bal = cf.get_bal_on_date(datetime.datetime(2019, 6, 6), 
                                 cf.get_register("accntDst"))
        self.assertAlmostEqual(bal, 470, 2)

    def test_transfers_6(self): 
        """This test focuses on custom date generation specifications.

        - once
        - weekly 
            - end_date:  1. prior to last, 2. None
            - interval bewteen:  1 and 2
        - bi-weekly
            - end_date:  1. prior to last, 2. None
        - twice-a-month
            - end_date:  1. prior to last, 2. None, 3. after last date
        - monthly
            - end_date:  1. prior to last, 2. None
        - quarterly
            - end_date:  1. prior to last, 2. Number of Occurrances
        - semi-annual
            - end_date:  1. prior to last, 2. Number of Occurrances
        - annual
            - end_date:  1. prior to last, 2. after last date, 3. None, 
              4. number of occurrances
        """
        cf = CfAnalysis()

        # assume current date 1/1/2019
        last_date_3months = datetime.datetime(2019, 4, 1)
        last_date_2yrs = datetime.datetime(2021, 1, 1)
        last_date_10yrs = datetime.datetime(2029, 1, 1)

        ##############################################
        # custom - once
        ##############################################
        # Valid transfer date (ie startDate)
        expected = [datetime.datetime(2018, 9, 21)]
        freq = "2018-09-21;2018-09-21;once;;"
        dates = cf.get_dates(freq, last_date_2yrs)
        self.assertEqual(expected, dates)

        # Transfer date after last_date)
        expected = []
        freq = "2025-09-21;2025-09-21;once;;"
        dates = cf.get_dates(freq, last_date_2yrs)
        self.assertEqual(expected, dates)

        ##############################################
        # custom - weekly
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 12, 3), 
                    datetime.datetime(2018, 12, 10), 
                    datetime.datetime(2018, 12, 17), 
                    datetime.datetime(2018, 12, 24), 
                    datetime.datetime(2018, 12, 31), 
                    datetime.datetime(2019, 1, 7), 
                    datetime.datetime(2019, 1, 14), 
                    datetime.datetime(2019, 1, 21), 
                    datetime.datetime(2019, 1, 28), 
                    datetime.datetime(2019, 2, 4), 
                    datetime.datetime(2019, 2, 11), 
                    datetime.datetime(2019, 2, 18), 
                    datetime.datetime(2019, 2, 25)]

        freq = "2018-12-3;2019-2-25;weekly;1;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date not specified; using None
        expected = [datetime.datetime(2019, 1, 1), 
                    datetime.datetime(2019, 1, 8), 
                    datetime.datetime(2019, 1, 15), 
                    datetime.datetime(2019, 1, 22), 
                    datetime.datetime(2019, 1, 29), 
                    datetime.datetime(2019, 2, 5), 
                    datetime.datetime(2019, 2, 12), 
                    datetime.datetime(2019, 2, 19), 
                    datetime.datetime(2019, 2, 26), 
                    datetime.datetime(2019, 3, 5), 
                    datetime.datetime(2019, 3, 12), 
                    datetime.datetime(2019, 3, 19), 
                    datetime.datetime(2019, 3, 26)]
        freq = "2019-1-1;None;weekly;1;"
        dates = cf.get_dates(freq, last_date_3months)
        self.assertEqual(expected, dates)

        # end date not specified; using None
        # weekly repeat interval = 2
        expected = [datetime.datetime(2019, 1, 1), 
                    datetime.datetime(2019, 1, 15), 
                    datetime.datetime(2019, 1, 29), 
                    datetime.datetime(2019, 2, 12), 
                    datetime.datetime(2019, 2, 26), 
                    datetime.datetime(2019, 3, 12), 
                    datetime.datetime(2019, 3, 26)]
        freq = "2019-1-1;None;weekly;2;"
        dates = cf.get_dates(freq, last_date_3months)
        self.assertEqual(expected, dates)

        ##############################################
        # custom - bi-weekly
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 12, 3), 
                    datetime.datetime(2018, 12, 17), 
                    datetime.datetime(2018, 12, 31), 
                    datetime.datetime(2019, 1, 14), 
                    datetime.datetime(2019, 1, 28), 
                    datetime.datetime(2019, 2, 11), 
                    datetime.datetime(2019, 2, 25)]

        freq = "2018-12-3;2019-2-25;bi-weekly;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date not specified; using None
        expected = [datetime.datetime(2019, 1, 1), 
                    datetime.datetime(2019, 1, 15), 
                    datetime.datetime(2019, 1, 29), 
                    datetime.datetime(2019, 2, 12), 
                    datetime.datetime(2019, 2, 26), 
                    datetime.datetime(2019, 3, 12), 
                    datetime.datetime(2019, 3, 26)]
        freq = "2019-1-1;None;bi-weekly;"
        dates = cf.get_dates(freq, last_date_3months)
        self.assertEqual(expected, dates)

        ##############################################
        # custom - twice-a-month
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 12, 1), 
                    datetime.datetime(2018, 12, 15), 
                    datetime.datetime(2019, 1, 1), 
                    datetime.datetime(2019, 1, 15), 
                    datetime.datetime(2019, 2, 1), 
                    datetime.datetime(2019, 2, 15), 
                    datetime.datetime(2019, 3, 1), 
                    datetime.datetime(2019, 3, 15)]
        freq = "2018-12-01;2019-03-30;twice-a-month;15;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date:  None
        # notice expected2 is concatneated to expected 
        expected2 = [datetime.datetime(2019, 4, 1)]
        freq = "2018-12-01;None;twice-a-month;15;"
        dates = cf.get_dates(freq, last_date_3months)
        self.assertEqual(expected+expected2, dates)

        # end date specified; after last date
        expected = [datetime.datetime(2018, 10, 31), 
                    datetime.datetime(2018, 11, 15), 
                    datetime.datetime(2018, 11, 30), 
                    datetime.datetime(2018, 12, 15), 
                    datetime.datetime(2018, 12, 31), 
                    datetime.datetime(2019, 1, 15), 
                    datetime.datetime(2019, 1, 31), 
                    datetime.datetime(2019, 2, 15), 
                    datetime.datetime(2019, 2, 28), 
                    datetime.datetime(2019, 3, 15), 
                    datetime.datetime(2019, 3, 31)]
        freq = "2018-10-31;2020-10-31;twice-a-month;15;"
        dates = cf.get_dates(freq, last_date_3months)
        self.assertEqual(expected, dates)

        ##############################################
        # custom - monthly
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2018, 10, 21), 
                    datetime.datetime(2018, 11, 21), 
                    datetime.datetime(2018, 12, 21), 
                    datetime.datetime(2019, 1, 21), 
                    datetime.datetime(2019, 2, 21), 
                    datetime.datetime(2019, 3, 21), 
                    datetime.datetime(2019, 4, 21), 
                    datetime.datetime(2019, 5, 21), 
                    datetime.datetime(2019, 6, 21), 
                    datetime.datetime(2019, 7, 21), 
                    datetime.datetime(2019, 8, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2019, 10, 21), 
                    datetime.datetime(2019, 11, 21), 
                    datetime.datetime(2019, 12, 21)]
        freq = "2018-09-21;2019-12-22;monthly;1"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date:  None
        # notice expected2 is concatneated to expected 
        expected2 = [datetime.datetime(2020, 1, 21), 
                     datetime.datetime(2020, 2, 21), 
                     datetime.datetime(2020, 3, 21), 
                     datetime.datetime(2020, 4, 21), 
                     datetime.datetime(2020, 5, 21), 
                     datetime.datetime(2020, 6, 21), 
                     datetime.datetime(2020, 7, 21), 
                     datetime.datetime(2020, 8, 21), 
                     datetime.datetime(2020, 9, 21), 
                     datetime.datetime(2020, 10, 21), 
                     datetime.datetime(2020, 11, 21), 
                     datetime.datetime(2020, 12, 21)]
        freq = "2018-09-21;None;monthly;1"
        dates = cf.get_dates(freq, last_date_2yrs)
        self.assertEqual(expected+expected2, dates)
        
        ##############################################
        # custom - quarterly
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2018, 12, 21), 
                    datetime.datetime(2019, 3, 21), 
                    datetime.datetime(2019, 6, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2019, 12, 21), 
                    datetime.datetime(2020, 3, 21), 
                    datetime.datetime(2020, 6, 21), 
                    datetime.datetime(2020, 9, 21), 
                    datetime.datetime(2020, 12, 21)]
        freq = "2018-09-21;2020-12-22;quarterly;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date not specified, use occurances
        expected = [datetime.datetime(2018, 11, 30), 
                    datetime.datetime(2019, 2, 28), 
                    datetime.datetime(2019, 5, 30), 
                    datetime.datetime(2019, 8, 30), 
                    datetime.datetime(2019, 11, 30)]
        freq = "2018-11-30;5;quarterly;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        ##############################################
        # custom - semi-annually
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2019, 3, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2020, 3, 21), 
                    datetime.datetime(2020, 9, 21), 
                    datetime.datetime(2021, 3, 21)]
        freq = "2018-09-21;2021-3-22;semi-annually;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date not specified; use occurrance count
        expected = [datetime.datetime(2018, 11, 30), 
                    datetime.datetime(2019, 5, 30), 
                    datetime.datetime(2019, 11, 30), 
                    datetime.datetime(2020, 5, 30), 
                    datetime.datetime(2020, 11, 30)]
        freq = "2018-11-30;5;semi-annually;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        ##############################################
        # custom - annually
        ##############################################
        # end date specified; prior to last date
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2020, 9, 21)]
        freq = "2018-09-21;2020-10-22;annually;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date specified; following to last date
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2020, 9, 21)]
        freq = "2018-09-21;2029-10-22;annually;"
        dates = cf.get_dates(freq, last_date_2yrs)
        self.assertEqual(expected, dates)

        # end date None
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2020, 9, 21), 
                    datetime.datetime(2021, 9, 21), 
                    datetime.datetime(2022, 9, 21), 
                    datetime.datetime(2023, 9, 21), 
                    datetime.datetime(2024, 9, 21), 
                    datetime.datetime(2025, 9, 21), 
                    datetime.datetime(2026, 9, 21), 
                    datetime.datetime(2027, 9, 21), 
                    datetime.datetime(2028, 9, 21)]
        freq = "2018-09-21;None;annually;;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)

        # end date count
        expected = [datetime.datetime(2018, 9, 21), 
                    datetime.datetime(2019, 9, 21), 
                    datetime.datetime(2020, 9, 21), 
                    datetime.datetime(2021, 9, 21)]
        freq = "2018-09-21;4;annually;;"
        dates = cf.get_dates(freq, last_date_10yrs)
        self.assertEqual(expected, dates)
        

# the following allows for simpler run syntax
# This didn't work.  The run is looking for command line args to cf.py
if __name__ == '__main__': 
    unittest.main()

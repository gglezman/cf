#
# Author: Greg Glezman
#
# SCCSID : "%W% %G%
#
# Copyright (c) 2018-2019 G.Glezman.  All Rights Reserved.
#
# This file contains classes that are used by the cash flow python script
# to edit account data. Occurrences are used for compounding, transfers, etc.

from datetime import datetime, date, timedelta
from calendar import monthrange
import itertools
import utilities as util
import data_file_constants as dfc

MONTHS_IN_YEAR = 12
MONTHS_IN_SEMI_YEAR = 6
MONTHS_IN_QUARTER = 3
MONTHS_IN_MONTH = 1


class EndDate:
    """Create a class that represents the end date of an occurrence.

    Args:
        ed_type (str): Describes the possible type of end date
            - EndDate.END_ON
            - EndDate.COUNT
            - EndDate.NONE

        date (str, optional): This field is required if type is EndDate.END_ON
            Format of date is dfc.DATE_FORMAT.

        count (int, optional): This field is required if type is EndDate.COUNT

        last_date (datetime): This field is required if type is EndDate.NONE
    """
    # End Date types
    NONE = 'none'
    END_ON = 'end_on'
    COUNT = 'count'

    def __init__(self, ed_type, date=None, count=1, last_date=None):
        if ed_type == EndDate.NONE:
            self._date = {'type': EndDate.NONE, 'date': last_date, 'None': True}
        elif ed_type == EndDate.END_ON:
            self._date = {'type': EndDate.END_ON,
                          'date': datetime.strptime(date, dfc.DATE_FORMAT)}
        elif ed_type == EndDate.COUNT:
            self._date = {'type': EndDate.COUNT, 'occurrences': count}
        else:
            raise TypeError("Unknown type {}".format(ed_type))

    def has_count(self):
        return self._date['type'] == EndDate.COUNT

    def count(self):
        return self._date['occurrences']

    def set_count(self, count):
        if self._date['type'] == EndDate.COUNT:
            self._date['occurrences'] = count
        else:
            raise TypeError("EndDate is wrong type, has no count")

    def has_no_end_date(self):
        return self._date['type'] == EndDate.NONE

    def includes_end_date(self):
        return self._date['type'] == EndDate.END_ON

    def date(self):
        """
        Returns: (datetime)
        """
        return self._date['date']

    def get_string_end_date(self):
        if self._date['type'] == EndDate.END_ON:
            # return the string version of the end date
            return self._date['date'].strftime(dfc.DATE_FORMAT)
        elif self._date['type'] == EndDate.NONE:
            return "None"
        elif self._date['type'] == EndDate.COUNT:
            return str(self._date['occurrences'])


class Occurrences:
    """Create an occurrence based on the given spec.
    
    Args
        occurrence_spec (str): defines the occurrence

        last_date (datetime): last date tracked per settings

    String Format of occurrence_spec: 'sd;ed;reg;x0;x1'

    where 
        sd is start date
           'YYYY-MM-DD'
        ed is end date
           'YYYY-MM-DD' or 
           'None' or 
           n-occurrences
        reg is regularity
           once
              - sd is the date
              - ed ignored
           weekly
              - sd specifies day_of_week
              - x0 specifies number of weeks between (int)
           bi-weekly
              - sd specifies day of week
           twice-a-month
              - sd specifies the 1st day 
              - x0 specifies the 2nd day (int)
           monthly
              - sd specifies day_of_month
              - x0 specifies the number of months between (int)
           quarterly 
              - sd specifies day_of_month
           semi-annually
              - sd specifies 1st day/month
           annually
               - sd specifies the day of the year
    """

    regularities_list = ['monthly', 'once', 'weekly', 'bi-weekly', 'twice-a-month',
                         'quarterly', 'semi-annually', 'annually']

    def __init__(self, occurrence_spec, last_date):

        # Local variables
        self.regularity = None
        self.weekly_interval = 1
        self.monthly_interval = 1
        self.second_day = 1
        self.last_date = last_date  # datetime
        self.start_date = None  # datetime
        self.end_date = None  # EndDate object

        #  parse the string
        sd, ed, self.regularity, *xtras = occurrence_spec.split(';')

        ##########################
        # validate the arguments
        ##########################
        # validate the regularity
        if self.regularity not in Occurrences.regularities_list:
            raise TypeError("Unknown regularity in occurrence spec {}".format(
                    self.regularity))
        if type(last_date) != datetime:
            raise TypeError("last_date must be a datetime")

        #######################################
        # internally we use datetime for dates
        #######################################
        self.start_date = datetime.strptime(sd, dfc.DATE_FORMAT)

        #######################################
        # end_date does not have to be a date
        #######################################
        if ed == 'None':
            self.end_date = EndDate(EndDate.NONE, last_date=last_date)
        elif '-' in ed:  # TODO - this is shaky
            self.end_date = EndDate(EndDate.END_ON, ed)
        else:
            self.end_date = EndDate(EndDate.COUNT, count=int(ed))

        #######################################
        # Act on the 'regularity' component
        #######################################
        if self.regularity == 'weekly':
            self.weekly_interval = int(xtras[0])  # num of weeks between dates
        elif self.regularity == 'twice-a-month':
            self.second_day = int(xtras[0])
        elif self.regularity == 'monthly':
            self.monthly_interval = int(xtras[0])

    def get_dates(self):
        """Get a list of dates per the given occurrence specification.
        
        Note: no dates are included that are beyond the last_date

        Return: 
            date ( list( datetime) ): a list of dates, in datetime format
                matching the given input
        """
        dates = []  # return value

        #######################################
        # Act on the 'regularity' component
        #######################################
        if self.regularity == 'once':
            if self.start_date <= self.last_date:
                dates.append(self.start_date)
        elif self.regularity == 'weekly':
            self.gen_date_list_by_weeks(self.start_date, self.weekly_interval,
                                        self.end_date,
                                        self.last_date, dates)
        elif self.regularity == 'monthly':
            self.gen_date_list_by_months(self.start_date,
                                         MONTHS_IN_MONTH * self.monthly_interval,
                                         self.end_date, self.last_date, dates)
        elif self.regularity == 'bi-weekly':
            self.gen_date_list_by_weeks(self.start_date, 2,
                                        self.end_date, self.last_date, dates)
        elif self.regularity == 'twice-a-month':
            self.gen_date_list_by_months(self.start_date, MONTHS_IN_MONTH,
                                         self.end_date, self.last_date, dates)
            # create second date
            second_date = self.start_date
            second_date = second_date.replace(day=self.second_day)
            if second_date < self.start_date:
                second_date = self.add_months(second_date, 1)

            self.gen_date_list_by_months(second_date, MONTHS_IN_MONTH,
                                         self.end_date, self.last_date, dates)
            dates.sort()  # interleave the two sets of dates

        elif self.regularity == 'quarterly':
            self.gen_date_list_by_months(self.start_date, MONTHS_IN_QUARTER,
                                         self.end_date, self.last_date, dates)
        elif self.regularity == 'semi-annually':
            self.gen_date_list_by_months(self.start_date, MONTHS_IN_SEMI_YEAR,
                                         self.end_date, self.last_date, dates)
        elif self.regularity == 'annually':
            self.gen_date_list_by_months(self.start_date, MONTHS_IN_YEAR,
                                         self.end_date, self.last_date, dates)

        """
        print("Date set for {}".format(self.get_string_spec()))
        print("  {} entries in list".format(len(dates)))
        if len(dates) > 0:
            str_list = "  "
            for d in dates:
                str_list += "{:04}-{:02}-{:02}, ".format(
                    d.year,d.month,d.day)
            print(str_list)
        """
        return dates

    def get_sample_dates(self, n):
        """Get a list of 'n' sample dates for the occurrence.

        For example, give me the first 4 dates for a quarterly
        occurrence. The year is stripped off for brevity so the 
        list will contain strings in the dfc.SHORT_DATE_FORMAT.

        If a date is not available, '-' is returned in its place."""

        dates = self.get_dates()
        s = ['-'] * n  # generate a list of n dashes
        for i, date in enumerate(dates):
            if len(dates) > i and len(s) > i:
                s[i] = dates[i].strftime(dfc.SHORT_DATE_FORMAT)
        return s

    def gen_date_list_by_months(self, start_date, interval_in_months,
                                end_date, last_date, dates):
        """
        Args:
            start_date (datetime)
            interval_in_months (int)
            end_date (EndDate)
            last_date (datetime)
            dates (list(datetime))
        """
        date = start_date
        if end_date.has_count():
            for i in range(end_date.count()):
                if date <= last_date:
                    dates.append(date)
                    date = self.get_next_date(start_date, interval_in_months * (i + 1))
                else:
                    break
        else:
            for i in itertools.count():
                if date <= end_date.date() and date <= last_date:
                    dates.append(date)
                    date = self.get_next_date(start_date, interval_in_months * (i + 1))
                else:
                    break

    def gen_date_list_by_weeks(self, start_date, interval_in_weeks,
                               end_date, last_date, dates):
        """
        Args:
            start_date (datetime)
            interval_in_weeks (int)
            end_date (EndDate)
            last_date (datetime)
            dates (list(datetime))
        """
        date = start_date
        if end_date.has_count():
            for i in range(end_date.count()):
                if date <= last_date:
                    dates.append(date)
                    date = self.get_next_date_by_weeks(start_date,
                                                       interval_in_weeks * (i + 1))
                else:
                    break
        else:
            for i in itertools.count():
                if date <= end_date.date() and date <= last_date:
                    dates.append(date)
                    date = self.get_next_date_by_weeks(start_date,
                                                       interval_in_weeks * (i + 1))
                else:
                    break

    @staticmethod
    def get_next_date_by_weeks(start_date, weeks):
        """Return a date 'weeks' weeks from 'start_date."""

        if type(start_date) != datetime:
            raise TypeError("{}(): Start_date is not a datetime".format(
                    util.f_name()))
        if type(weeks) != int:
            raise TypeError("{}(): Weeks is not an integer".format(
                    util.f_name()))

        return start_date + timedelta(days=weeks * 7)

    @staticmethod
    def get_next_date(start_date, months):
        """Return a date 'months' months from 'start_date.  Correct 
        for short months (eg 1 month from jan 31st is feb 28th"""

        if type(start_date) != datetime:
            raise TypeError("{}(): start_date not datetime".format(
                    util.f_name()))
        if type(months) != int:
            raise TypeError("{}(): months not an int".format(util.f_name()))

        next_year = start_date.year + ((start_date.month + months - 1) // 12)
        next_month = start_date.month + months  # modulo months avoids next loop
        while next_month > 12:
            next_month -= 12
        days_next_month = monthrange(next_year, next_month)[1]

        return start_date.replace(
                year=next_year,
                month=next_month,
                day=min(start_date.day, days_next_month))

    def get_latest_date(self):
        """Determine the latest date in a frequency, beyond the current date.

        Generate a list of date from a frequency spec and find the next date 
        in the list equal to or beyond the current date.
        If all dates are prior to the current, use the last in the list.
        If the first date is beyond last tracked date, show first
        """
        d = date.today()
        today = datetime(d.year, d.month, d.day)

        date_list = self.get_dates()

        best_date = self.start_date

        if len(date_list) > 0:
            for best_date in date_list:
                if best_date >= today:
                    break

        return best_date

    @staticmethod
    def add_months(date, months):
        """Pulled this from the internet."""

        if type(date) != datetime:
            raise TypeError("date must be a datetime object")

        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, monthrange(year, month)[1])
        return datetime(year, month, day)

    def get_start_date(self):
        """return the date portion of the start_date datetime"""

        return self.start_date.date()

    def set_start_date(self, start_date):
        self.start_date = start_date
        self.second_day = (self.start_date.day + 13) % 28 + 1

        if self.regularity == 'once':
            # make end_date same as start_date
            self.end_date = EndDate(
                    'end_on',
                    date=self.start_date.strftime(dfc.DATE_FORMAT))

    def get_end_date(self):
        """
        Return (EndDate)
        """
        return self.end_date

    def set_end_date(self, type, date=util.today_in_text()):
        if type == EndDate.NONE:
            self.end_date = EndDate('none', last_date=self.last_date)
        elif type == EndDate.END_ON:
            self.end_date = EndDate('end_on', date=date)
        elif type == EndDate.COUNT:
            self.end_date = EndDate('count', count=1)
        else:
            raise TypeError("Unknown type: {}".format(type))

    def get_regularity(self):
        """return the date portion of the start_date datetime"""

        return self.regularity

    def set_regularity(self, regularity):
        """Change the regularity setting."""

        if self.regularity != regularity:
            # The End  Date frame may also be affected
            if self.regularity == 'once' or regularity == 'once':
                self.end_date = EndDate(EndDate.NONE, last_date=self.last_date)

            self.regularity = regularity
            self.weekly_interval = 1
            self.monthly_interval = 1
            # attempt to generate a reasonable second date
            self.second_day = (self.start_date.day + 13) % 28 + 1

    def get_string_spec(self):
        sd = self.start_date.strftime(dfc.DATE_FORMAT)
        ed = self.end_date.get_string_end_date()

        spec = sd + ";" + ed + ";" + self.regularity
        if self.regularity == 'weekly':
            spec += ";" + str(self.weekly_interval)
        elif self.regularity == 'twice-a-month':
            spec += ";" + str(self.second_day)
        elif self.regularity == 'monthly':
            spec += ";" + str(self.monthly_interval)

        return spec

    def set_monthly_interval(self, interval):
        self.monthly_interval = interval

    def set_weekly_interval(self, interval):
        self.weekly_interval = interval

    def set_second_day(self, interval):
        self.second_day = interval

    def set_occ_count(self, interval):
        self.end_date.set_count(interval)

    # Queries
    def end_date_has_count(self):
        return self.end_date.has_count()

    def has_no_end_date(self):
        return self.end_date.has_no_end_date()

    def includes_end_date(self):
        return self.end_date.includes_end_date()

    def validate(self):
        if self.end_date.includes_end_date():
            if self.start_date > self.end_date.date():
                return "The End Date may not precede the Start Date"

        return ""

    def get_modified_regularity(self):
        """Return the regularity with an asterisk if the modified is not 1.

        Some regularities can have modifiers. That is months and weeks can
        have modifiers. If the regularity is one with a modifier and the 
        modifier is not '1', add an asterisk to the staring."""

        value = self.regularity
        if value == 'monthly':
            if self.monthly_interval != 1:
                value += '*'
        elif value == 'weekly':
            if self.weekly_interval != 1:
                value += '*'
        return value

    @staticmethod
    def default_occurrence_spec():
        sd = util.today_in_text()
        ed = sd
        regularity = 'once'

        spec = sd + ";" + ed + ";" + regularity
        return spec

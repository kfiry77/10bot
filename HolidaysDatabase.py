"""
Module: holidays_database.py
This module provides a HolidaysDatabase class to manage holiday data, loading it from CSV files and checking if
a specific date is a working day.
"""

import datetime
import logging


class HolidaysDatabase:
    """
    A class representing a database of holidays.

    Attributes:
    - HOLIDAYS_FILE (str): Path to the CSV file containing holiday data.
    - CSV_SEPARATOR (str): Separator used in the CSV file.

    Methods:
    - build(): Builds the holiday database by reading from an Excel file and filtering data.
    - load_holidays(): Loads holiday data from the CSV file into a dictionary.
    - is_working_day(date=datetime.date.today()): Checks if a given date is a working day.
    """

    HOLIDAYS_FILE = 'state/Jewish_Israeli_holidays.csv'
    CSV_SEPARATOR = '|'

    def build(self):
        """
        Builds the holiday database by reading data from an Excel file, filtering, and saving to a CSV file.
        """
        import pandas as pd  # pylint: disable=import-outside-toplevel, import-error
        # file found on : http://top-analyst.com/he/?p=317
        excel_file = 'Jewish_Israeli_holidays.xlsx'  # Replace with your Excel file path
        data = pd.read_excel(excel_file)
        filtered_data = data[data['year'] >= 2023]
        filtered_data.to_csv('Jewish_Israeli_holidays.csv')
        filtered_data.to_csv(self.HOLIDAYS_FILE, self.CSV_SEPARATOR, index=False)

    def __init__(self):
        """
        Initializes the HolidaysDatabase object.
        """
        self.logger = logging.getLogger('AppLogger')
        self.holidays = {}
        self.load_holidays()

    def load_holidays(self):
        """
          Loads holiday data from the CSV file into a dictionary.
        """
        self.holidays = {}
        selected_columns = ['eng_name', 'eng_type', 'heb_name', 'heb_type', 'is_bank_holiday']
        with open(self.HOLIDAYS_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            headers = lines[0].strip().split(self.CSV_SEPARATOR)
            col_indices = [headers.index(col) for col in selected_columns]  # Find indices of selected columns
            key_index = headers.index('date')

            for line in lines[1:]:  # Skip the header row, start reading from the second row
                values = line.strip().split(self.CSV_SEPARATOR)
                key = datetime.datetime.strptime(values[key_index], '%Y-%m-%d').date()

                # make sure only current year is scanned and fetched.
                if key.year < datetime.datetime.now().year:
                    continue
                if key.year > datetime.datetime.now().year:
                    break

                values_dict = {selected_columns[i]: values[col_indices[i]] for i in range(len(selected_columns))}
                self.holidays[key] = values_dict

    def is_working_day(self, date=datetime.date.today()):
        """
            Checks if a given date is a working day.

            Args:
            - date (datetime.date, optional): Date to check. Defaults to today's date.

            Returns:
            - bool: True if the date is a working day, False otherwise.
        """
        # check if it is a working day, if not return
        if date.weekday() == 5 or date.weekday() == 4:
            self.logger.debug('It is a weekend today')
            return False

        if date in self.holidays:
            self.logger.debug('today is %s', self.holidays[date]['eng_name'])
            self.logger.debug('today is %s',
                              'working day' if self.holidays[date]['eng_name'] != '1' else 'holiday')
            return self.holidays[date]['is_bank_holiday'] != '1'
        return True

    def get_holiday_data(self, date=datetime.date.today()):
        """
        returns the data for the given date
        """

        if date.weekday() == 5 or date.weekday() == 4:
            return {'eng_name': 'Friday/Saturday',
                    'eng_type': 'weekend',
                    'heb_name': ' שישי/שבת ',
                    'heb_type': 'סופ"ש',
                    'is_bank_holiday': '0'}

        if date in self.holidays:
            return self.holidays[date]
        return {'eng_name': 'None',
                'eng_type': 'weekday',
                'heb_name': 'יום חול',
                'heb_type': 'יום חול',
                'is_bank_holiday': '0'}

"""Testing module"""

import os
import unittest
import datetime
from acc_bot.test_data import load_test_data_1, load_test_data_2
from acc_bot.util import (
    accumulate_by_span,
    gater_week,
    check_limit,
    make_spending_prediction,
    make_pie
)

class UtilTest(unittest.TestCase):
    """Main class for util testing."""

    def test_accum_data_1_day(self):
        """Test util.accumulate_by_span with data 1 & a day span."""
        expected_res = [12543, 10238, 15035, 11014, 14629, 15293, 12154]
        self.assertEqual(accumulate_by_span(load_test_data_1(),
                         datetime.timedelta(days=1)), expected_res)

    def test_accum_data_2_day(self):
        """Test accumulate_by_span with data 2 & a day span."""
        expected_res = [21932, 19774, 20094, 12034]  # last 4 values
        self.assertEqual(accumulate_by_span(load_test_data_2(),
                         datetime.timedelta(days=1))[-4:], expected_res)

    def test_accum_data_2_week(self):
        """Test accumulate_by_span with data 2 & a week span."""
        expected_res = [1314, 115885, 129588, 117071, 123289, 128423, 132227, 135355, 122867]
        self.assertEqual(accumulate_by_span(load_test_data_2(),
                         datetime.timedelta(days=7)), expected_res)

    def test_gather_week_data_1(self):
        """Test gather_week with data 1."""
        expected_res = {
            'restaurants': 20625,
            'transport': 15048,
            'supermarkets': 12940,
            'pharmacy': 13464,
            'entertainment': 16619,
            'other': 12210
        }
        self.assertEqual(gater_week(load_test_data_1()), expected_res)

    def test_gather_week_data_2(self):
        """Test gather_week with data 2."""
        expected_res = {
            'restaurants': 18546,
            'transport': 21267,
            'supermarkets': 19803,
            'pharmacy': 17275,
            'entertainment': 25024,
            'other': 20952
        }
        self.assertEqual(gater_week(load_test_data_2()), expected_res)

    def test_check_limit_set(self):
        """Test function check_limit with data 1 & set category pharmacy."""
        data = {'data': load_test_data_1(), 'limits': {'pharmacy': 10}}
        expected_res = (13464, 10)
        self.assertEqual(check_limit(data, 'pharmacy'), expected_res)

    def test_check_limit_unset(self):
        """Test function check_limit with data 1 & unset category pharmacy."""
        data = {'data': load_test_data_1(), 'limits': {}}
        expected_res = (13464, 0)
        self.assertEqual(check_limit(data, 'pharmacy'), expected_res)

    def test_check_limit_no_lim_key_err(self):
        """Test check_limit throws KeyError in case of no 'limit' in data."""
        data = {'data': load_test_data_1()}
        self.assertRaises(KeyError, check_limit, data, 'pharmacy')

    def test_make_spending_pred(self):
        """Test make_spending_prediction with test data 2."""
        data = load_test_data_2()
        expected_res = 158550
        self.assertEqual(make_spending_prediction(data), expected_res)

    def test_make_pie(self):
        """Test make_pie functionality."""
        data = load_test_data_1()
        make_pie(data)
        self.assertIn('tmp.png', os.listdir())
        os.remove('tmp.png')
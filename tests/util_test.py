#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import unittest

import dateutil
import freezegun

from rn2md import util


def StrToDate(date_str):
    """Interprets a pretty date_str into datetime.date"""
    return dateutil.parser.parse(date_str).date()


class ParseDatesTest(unittest.TestCase):
    """Tests for the rn2md.util.ParseDates function."""

    @freezegun.freeze_time('Mar 24th, 2018')
    def testToday(self):
        self.assertListEqual(util.ParseDates('today'), [
            StrToDate('Mar 24th, 2018'),
        ])

    @freezegun.freeze_time('Fri Mar 23rd, 2018')
    def testThisWeek(self):
        self.assertListEqual(util.ParseDates('this week'), [
            StrToDate('Mon Mar 19th, 2018'),
            StrToDate('Tue Mar 20th, 2018'),
            StrToDate('Wed Mar 21st, 2018'),
            StrToDate('Thu Mar 22nd, 2018'),
            StrToDate('Fri Mar 23rd, 2018'),
            StrToDate('Sat Mar 24th, 2018'),
            StrToDate('Sun Mar 25th, 2018'),
        ])

    @freezegun.freeze_time('Mon Mar 26th, 2018')
    def testLastWeek(self):
        self.assertListEqual(util.ParseDates('last week'), [
            StrToDate('Mon Mar 19th, 2018'),
            StrToDate('Tue Mar 20th, 2018'),
            StrToDate('Wed Mar 21st, 2018'),
            StrToDate('Thu Mar 22nd, 2018'),
            StrToDate('Fri Mar 23rd, 2018'),
            StrToDate('Sat Mar 24th, 2018'),
            StrToDate('Sun Mar 25th, 2018'),
        ])

    @freezegun.freeze_time('Sat Mar 24th, 2018')
    def testTodayOnSaturdayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('today', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Sun Mar 25th, 2018')
    def testTodayOnSundayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('today', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Sat Mar 24th, 2018')
    def testWorkWeekReturnedInWorkdayOnlyMode(self):
        self.assertListEqual(util.ParseDates('this week', workdays_only=True), [
            StrToDate('Mon Mar 19th, 2018'),
            StrToDate('Tue Mar 20th, 2018'),
            StrToDate('Wed Mar 21st, 2018'),
            StrToDate('Thu Mar 22nd, 2018'),
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Sun Mar 25th, 2018')
    def testYesterdayOnSundayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('yesterday', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Mon Mar 26th, 2018')
    def testYesterdayOnMondayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('yesterday', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Fri Mar 23rd, 2018')
    def testTomorrowOnFridayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('tomorrow', workdays_only=True), [
            StrToDate('Mon Mar 26th, 2018'),
        ])

    @freezegun.freeze_time('Sat Mar 24th, 2018')
    def testTomorrowOnSaturdayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('tomorrow', workdays_only=True), [
            StrToDate('Mon Mar 26th, 2018'),
        ])


if __name__ == '__main__':
    unittest.main()
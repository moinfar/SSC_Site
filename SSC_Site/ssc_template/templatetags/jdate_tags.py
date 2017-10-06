# -*- coding: utf-8 -*-

import jdatetime

from django import template

register = template.Library()


def farsi_text(number):
    # TODO: TO BE IMPLEMENTED LATER
    return number


@register.filter()
def get_jdate(date):
    return jdatetime.GregorianToJalali(date.year, date.month, date.day)


def farsi_text_month(number):
    text = ['', 'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند', ]
    return text[number]


@register.filter()
def farsi_digits(string):
    transition = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
                  '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹', '،': ' و '}
    for en in transition:
        string = string.replace(en, transition[en])
    return string


@register.filter()
def jdateformat(jdate, _format):
    """formats date or datetime to a specific format"""
    return _format.format(d=jdate.jday, m=jdate.jmonth, y=jdate.jyear,
                          D=farsi_text(jdate.jday), M=farsi_text_month(jdate.jmonth),
                          Y=farsi_text(jdate.jyear))

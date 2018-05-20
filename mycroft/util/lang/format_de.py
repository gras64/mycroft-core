# -*- coding: utf-8 -*-
#
# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from mycroft.util.lang.format_common import convert_to_mixed_fraction

NUM_STRING_DE = {
    0: 'null',
    1: 'eins',
    2: 'zwei',
    3: 'drei',
    4: 'vier',
    5: 'fünf',
    6: 'sechs',
    7: 'sieben',
    8: 'acht',
    9: 'neun',
    10: 'zehn',
    11: 'elf',
    12: 'zwölf',
    13: 'dreizehn',
    14: 'vierzehn',
    15: 'fünfzehn',
    16: 'sechzehn',
    17: 'sibzehn',
    18: 'achzehn',
    19: 'neunzehn',
    20: 'zwanzig',
    30: 'dreisig',
    40: 'virzig',
    50: 'fünfzig',
    60: 'sechzig',
    70: 'sibzig',
    80: 'achzig',
    90: 'neunzig'
}


FRACTION_STRING_DE = {
    2: 'halbe',
    3: 'dritte',
    4: 'vierte',
    5: 'fünfte',
    6: 'sechste',
    7: 'siebte',
    8: 'achte',
    9: 'neunte',
    10: 'zehnte',
    11: 'elfte',
    12: 'zwölfte',
    13: 'dreizehnte',
    14: 'vierzehnte',
    15: 'fünfzehnte',
    16: 'sechzehnte',
    17: 'sibzehnte',
    18: 'achzehnte',
    19: 'neunzehnte',
    20: 'zwanzigste'
}


def nice_number_de(number, speech, denominators):
    """ German helper for nice_number

    This function formats a float to human understandable functions. Like
    4.5 becomes "4 and a half" for speech and "4 1/2" for text

    Args:
        number (int or float): the float to format
        speech (bool): format for speech (True) or display (False)
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """

    result = convert_to_mixed_fraction(number, denominators)
    if not result:
        # Give up, just represent as a 3 decimal number
        return str(round(number, 3))

    whole, num, den = result

    if not speech:
        if num == 0:
            # TODO: Number grouping?  E.g. "1,000,000"
            return str(whole)
        else:
            return '{} {}/{}'.format(whole, num, den)

    if num == 0:
        return str(whole)
    den_str = FRACTION_STRING_DE[den]
    if whole == 0:
        if num == 1:
            return_string = 'a {}'.format(den_str)
        else:
            return_string = '{} {}'.format(num, den_str)
    elif num == 1:
        return_string = '{} and a {}'.format(whole, den_str)
    else:
        return_string = '{} and {} {}'.format(whole, num, den_str)
    if num > 1:
        return_string += 's'
    return return_string


def pronounce_number_de(num, places=2):
    """
    Convert a number to it's spoken equivalent

    For example, '5.2' would return 'five point two'

    Args:
        num(float or int): the number to pronounce (under 100)
        places(int): maximum decimal places to speak
    Returns:
        (str): The pronounced number
    """
    if abs(num) >= 100:
        # TODO: Support for numbers over 100
        return str(num)

    result = ""
    if num < 0:
        result = "negative "
    num = abs(num)

    if num > 20:
        tens = int(num-int(num) % 10)
        result += NUM_STRING_DE[tens]
        if int(num-tens) != 0:
            result += " " + NUM_STRING_DE[int(num-tens)]
    else:
        result += NUM_STRING_DE[int(num)]

    # Deal with fractional part
    if not num == int(num) and places > 0:
        result += " punkt"
        place = 10
        while int(num*place) % 10 > 0 and places > 0:
            result += " " + NUM_STRING_DE[int(num*place) % 10]
            place *= 10
            places -= 1
    return result


def nice_time_de(dt, speech=True, use_24hour=False, use_ampm=False):
    """
    Format a time to a comfortable human format

    For example, generate 'five thirty' for speech or '5:30' for
    text display.

    Args:
        dt (datetime): date to format (assumes already in local timezone)
        speech (bool): format for speech (default/True) or display (False)=Fal
        use_24hour (bool): output in 24-hour/military or 12-hour format
        use_ampm (bool): include the am/pm for 12-hour format
    Returns:
        (str): The formatted time string
    """
    if use_24hour:
        # e.g. "03:01" or "14:22"
        string = dt.strftime("%H:%M")
    else:
        if use_ampm:
            # e.g. "3:01 AM" or "2:22 PM"
            string = dt.strftime("%I:%M %p")
        else:
            # e.g. "3:01" or "2:22"
            string = dt.strftime("%I:%M")
        if string[0] == '0':
            string = string[1:]  # strip leading zeros

    if not speech:
        return string

    # Generate a speakable version of the time
    if use_24hour:
        speak = ""

        # Either "0 8 hundred" or "13 hundred"
        if string[0] == '0':
            speak += pronounce_number_de(int(string[0])) + " "
            speak += pronounce_number_de(int(string[1]))
        else:
            speak = pronounce_number_de(int(string[0:2]))

        speak += " "
        if string[3:5] == '00':
            speak += "hundert"
        else:
            if string[3] == '0':
                speak += pronounce_number_de(0) + " "
                speak += pronounce_number_de(int(string[4]))
            else:
                speak += pronounce_number_de(int(string[3:5]))
        return speak
    else:
        if dt.hour == 0 and dt.minute == 0:
            return "morgen"
        if dt.hour == 12 and dt.minute == 0:
            return "mittag"
        # TODO: "half past 3", "a quarter of 4" and other idiomatic times

        if dt.hour == 0:
            speak = pronounce_number_de(12)
        elif dt.hour < 13:
            speak = pronounce_number_de(dt.hour)
        else:
            speak = pronounce_number_de(dt.hour-12)

        if dt.minute == 0:
            if not use_ampm:
                return speak + " Uhr"
        else:
            if dt.minute < 10:
                speak += " oh"
            speak += " " + pronounce_number_de(dt.minute)

        if use_ampm:
            if dt.hour > 11:
                speak += " Morgens"
            else:
                speak += " Mittags"

        return speak

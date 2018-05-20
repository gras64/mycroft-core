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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from mycroft.util.lang.parse_common import is_numeric, look_for_fractions


def extractnumber_de(text):
    """
    This function prepares the given text for parsing by making
    numbers consistent, getting rid of contractions, etc.
    Args:
        text (str): the string to normalize
    Returns:
        (int) or (float): The value of extracted number

    """
    aWords = text.split()
    aWords = [word for word in aWords if word not in ["des", "dem", "das", "der", "den" ,"die"]]
    and_pass = False
    valPreAnd = False
    val = False
    count = 0
    while count < len(aWords):
        word = aWords[count]
        if is_numeric(word):
            # if word.isdigit():            # doesn't work with decimals
            val = float(word)
        elif word == "erster":
            val = 1
        elif word == "dritter":
            val = 3
        elif word == "siebter":
            val = 8


        elif isFractional_de(word):
            val = isFractional_de(word)
        else:
            if word == "eins":
                val = 1
            elif word == "zwei":
                val = 2
            elif word == "drei":
                val = 3
            elif word == "vier":
                val = 4
            elif word == "fünf":
                val = 5
            elif word == "sechs":
                val = 6
            elif word == "sieben":
                val = 7
            elif word == "acht":
                val = 8
            elif word == "neun":
                val = 9
            elif word == "zehn":
                val = 10
            if val:
                if count < (len(aWords) - 1):
                    wordNext = aWords[count + 1]
                else:
                    wordNext = ""
                valNext = isFractional_de(wordNext)

                if valNext:
                    val = val * valNext
                    aWords[count + 1] = ""

        # if val == False:
        if not val:
            # look for fractions like "2/3"
            aPieces = word.split('/')
            # if (len(aPieces) == 2 and is_numeric(aPieces[0])
            #   and is_numeric(aPieces[1])):
            if look_for_fractions(aPieces):
                val = float(aPieces[0]) / float(aPieces[1])
            elif and_pass:
                # added to value, quit here
                val = valPreAnd
                break
            else:
                count += 1
                continue

        aWords[count] = ""

        if and_pass:
            aWords[count - 1] = ''  # remove "and"
            val += valPreAnd
        elif count + 1 < len(aWords) and aWords[count + 1] == 'und':
            and_pass = True
            valPreAnd = val
            val = False
            count += 2
            continue
        elif count + 2 < len(aWords) and aWords[count + 2] == 'und':
            and_pass = True
            valPreAnd = val
            val = False
            count += 3
            continue

        break

    # if val == False:
    if not val:
        return False

    # Return the string with the number related words removed
    # (now empty strings, so strlen == 0)
    aWords = [word for word in aWords if len(word) > 0]
    text = ' '.join(aWords)

    return val


def extract_datetime_de(string, currentDate=None):
    def clean_string(s):
        """
            cleans the input string of unneeded punctuation and capitalization
            among other things.
        """
        s = s.lower().replace('?', '').replace('.', '').replace(',', '') \
            .replace(' ein ', ' ').replace(' die ', ' ').replace(' das ', ' ')
        wordList = s.split()
        for idx, word in enumerate(wordList):
            word = word.replace("'s", "")

            ordinals = ["ter", "tel", "nd", "th"]
            if word[0].isdigit():
                for ordinal in ordinals:
                    if ordinal in word:
                        word = word.replace(ordinal, "")
            wordList[idx] = word

        return wordList

    def date_found():
        return found or \
            (
                datestr != "" or timeStr != "" or
                yearOffset != 0 or monthOffset != 0 or
                dayOffset is True or hrOffset != 0 or
                hrAbs != 0 or minOffset != 0 or
                minAbs != 0 or secOffset != 0
            )

    if string == "":
        return None
    if currentDate is None:
        currentDate = datetime.now()

    found = False
    daySpecified = False
    dayOffset = False
    monthOffset = 0
    yearOffset = 0
    dateNow = currentDate
    today = dateNow.strftime("%w")
    currentYear = dateNow.strftime("%Y")
    fromFlag = False
    datestr = ""
    hasYear = False
    timeQualifier = ""

    timeQualifiersList = ['morgen', 'mittag', 'abend']
    markers = ['an', 'in', 'on', 'by', 'this', 'around', 'for', 'of']
    days = ['montag', 'dienstag', 'mittwoch',
            'donnerstag', 'Freitag', 'samstag', 'sonntag']
    months = ['jannuar', 'februar', 'März', 'Aprill', 'mai', 'juni',
              'july', 'august', 'september', 'oktober', 'november',
              'dezember']
    monthsShort = ['jan', 'feb', 'mär', 'apr', 'may', 'june', 'july', 'aug',
                   'sept', 'okt', 'nov', 'dez']

    words = clean_string(string)

    for idx, word in enumerate(words):
        if word == "":
            continue
        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""

        # this isn't in clean string because I don't want to save back to words
        word = word.rstrip('s')
        start = idx
        used = 0
        # save timequalifier for later
        if word in timeQualifiersList:
            timeQualifier = word
            # parse today, tomorrow, day after tomorrow
        elif word == "heute" and not fromFlag:
            dayOffset = 0
            used += 1
        elif word == "morgen" and not fromFlag:
            dayOffset = 1
            used += 1
        elif (word == "tag" and
                wordNext == "nach" and
                wordNextNext == "morgen" and
                not fromFlag and
                not wordPrev[0].isdigit()):
            dayOffset = 2
            used = 3
            if wordPrev == "der":
                start -= 1
                used += 1
                # parse 5 days, 10 weeks, last week, next week
        elif word == "Tag":
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev)
                start -= 1
                used = 2
        elif word == "woche" and not fromFlag:
            if wordPrev[0].isdigit():
                dayOffset += int(wordPrev) * 7
                start -= 1
                used = 2
            elif wordPrev == "nächste":
                dayOffset = 7
                start -= 1
                used = 2
            elif wordPrev == "letzte":
                dayOffset = -7
                start -= 1
                used = 2
                # parse 10 months, next month, last month
        elif word == "monat" and not fromFlag:
            if wordPrev[0].isdigit():
                monthOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordPrev == "nächsten":
                monthOffset = 1
                start -= 1
                used = 2
            elif wordPrev == "letzten":
                monthOffset = -1
                start -= 1
                used = 2
                # parse 5 years, next year, last year
        elif word == "jahr" and not fromFlag:
            if wordPrev[0].isdigit():
                yearOffset = int(wordPrev)
                start -= 1
                used = 2
            elif wordPrev == "nächste":
                yearOffset = 1
                start -= 1
                used = 2
            elif wordPrev == "letzte":
                yearOffset = -1
                start -= 1
                used = 2
                # parse Monday, Tuesday, etc., and next Monday,
                # last Tuesday, etc.
        elif word in days and not fromFlag:
            d = days.index(word)
            dayOffset = (d + 1) - int(today)
            used = 1
            if dayOffset < 0:
                dayOffset += 7
            if wordPrev == "nächsten":
                dayOffset += 7
                used += 1
                start -= 1
            elif wordPrev == "letzte":
                dayOffset -= 7
                used += 1
                start -= 1
                # parse 15 of July, June 20th, Feb 18, 19 of February
        elif word in months or word in monthsShort and not fromFlag:
            try:
                m = months.index(word)
            except ValueError:
                m = monthsShort.index(word)
            used += 1
            datestr = months[m]
            if wordPrev and (wordPrev[0].isdigit() or
                             (wordPrev == "im" and wordPrevPrev[0].isdigit())):
                if wordPrev == "im" and wordPrevPrev[0].isdigit():
                    datestr += " " + words[idx - 2]
                    used += 1
                    start -= 1
                else:
                    datestr += " " + wordPrev
                start -= 1
                used += 1
                if wordNext and wordNext[0].isdigit():
                    datestr += " " + wordNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False

            elif wordNext and wordNext[0].isdigit():
                datestr += " " + wordNext
                used += 1
                if wordNextNext and wordNextNext[0].isdigit():
                    datestr += " " + wordNextNext
                    used += 1
                    hasYear = True
                else:
                    hasYear = False
        # parse 5 days from tomorrow, 10 weeks from next thursday,
        # 2 months from July
        validFollowups = days + months + monthsShort
        validFollowups.append("heute")
        validFollowups.append("morgen")
        validFollowups.append("nächste")
        validFollowups.append("letzte")
        validFollowups.append("jetzt")
        if (word == "von" or word == "nach") and wordNext in validFollowups:
            used = 2
            fromFlag = True
            if wordNext == "morgen":
                dayOffset += 1
            elif wordNext in days:
                d = days.index(wordNext)
                tmpOffset = (d + 1) - int(today)
                used = 2
                if tmpOffset < 0:
                    tmpOffset += 7
                dayOffset += tmpOffset
            elif wordNextNext and wordNextNext in days:
                d = days.index(wordNextNext)
                tmpOffset = (d + 1) - int(today)
                used = 3
                if wordNext == "nächste":
                    tmpOffset += 7
                    used += 1
                    start -= 1
                elif wordNext == "letzte":
                    tmpOffset -= 7
                    used += 1
                    start -= 1
                dayOffset += tmpOffset
        if used > 0:
            if start - 1 > 0 and words[start - 1] == "diese":
                start -= 1
                used += 1

            for i in range(0, used):
                words[i + start] = ""

            if start - 1 >= 0 and words[start - 1] in markers:
                words[start - 1] = ""
            found = True
            daySpecified = True

    # parse time
    timeStr = ""
    hrOffset = 0
    minOffset = 0
    secOffset = 0
    hrAbs = 0
    minAbs = 0
    military = False

    for idx, word in enumerate(words):
        if word == "":
            continue

        wordPrevPrev = words[idx - 2] if idx > 1 else ""
        wordPrev = words[idx - 1] if idx > 0 else ""
        wordNext = words[idx + 1] if idx + 1 < len(words) else ""
        wordNextNext = words[idx + 2] if idx + 2 < len(words) else ""
        # parse noon, midnight, morning, afternoon, evening
        used = 0
        if word == "mittag":
            hrAbs = 12
            used += 1
        elif word == "mitternacht":
            hrAbs = 0
            used += 1
        elif word == "morgen":
            if hrAbs == 0:
                hrAbs = 8
            used += 1
        elif word == "nachmittag":
            if hrAbs == 0:
                hrAbs = 15
            used += 1
        elif word == "abend":
            if hrAbs == 0:
                hrAbs = 19
            used += 1
            # parse half an hour, quarter hour
        elif word == "stunde" and \
                (wordPrev in markers or wordPrevPrev in markers):
            if wordPrev == "halb":
                minOffset = 30
            elif wordPrev == "viertel":
                minOffset = 15
            elif wordPrev == "dreiviertel":
                minOffset = 45
            elif wordPrevrev == "dreiviertel":
                minOffset = 15
                if idx > 2 and words[idx - 3] in markers:
                    words[idx - 3] = ""
                words[idx - 2] = ""
            else:
                hrOffset = 1
            if wordPrevPrev in markers:
                words[idx - 2] = ""
            words[idx - 1] = ""
            used += 1
            hrAbs = -1
            minAbs = -1
            # parse 5:00 am, 12:00 p.m., etc
        elif word[0].isdigit():
            isTime = True
            strHH = ""
            strMM = ""
            remainder = ""
            if ':' in word:
                # parse colons
                # "3:00 in the morning"
                stage = 0
                length = len(word)
                for i in range(length):
                    if stage == 0:
                        if word[i].isdigit():
                            strHH += word[i]
                        elif word[i] == ":":
                            stage = 1
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 1:
                        if word[i].isdigit():
                            strMM += word[i]
                        else:
                            stage = 2
                            i -= 1
                    elif stage == 2:
                        remainder = word[i:].replace(".", "")
                        break
                if remainder == "":
                    nextWord = wordNext.replace(".", "")
                    if nextWord == "am" or nextWord == "pm":
                        remainder = nextWord
                        used += 1
                    elif nextWord == "tonight":
                        remainder = "pm"
                        used += 1
                    elif wordNext == "am" and \
                            words[idx + 3] == "morgen":
                        remainder = "am"
                        used += 3
                    elif wordNext == "am" and \
                            words[idx + 3] == "mittag":
                        remainder = "pm"
                        used += 3
                    elif wordNext == "am" and \
                            words[idx + 3] == "abend":
                        remainder = "pm"
                        used += 3
                    elif wordNext == "am" and wordNextNext == "morgen":
                        remainder = "am"
                        used += 2
                    elif wordNext == "am" and wordNextNext == "nachmittag":
                        remainder = "pm"
                        used += 2
                    elif wordNext == "am" and wordNextNext == "abend":
                        remainder = "pm"
                        used += 2
                    elif wordNext == "heute" and wordNextNext == "morgen":
                        remainder = "am"
                        used = 2
                    elif wordNext == "heute" and wordNextNext == "nachmittag":
                        remainder = "pm"
                        used = 2
                    elif wordNext == "heute" and wordNextNext == "abend":
                        remainder = "pm"
                        used = 2
                    elif wordNext == "zur" and wordNextNext == "nacht":
                        if strHH > 5:
                            remainder = "pm"
                        else:
                            remainder = "am"
                        used += 2
                    else:
                        if timeQualifier != "":
                            military = True
                            if strHH <= 12 and \
                                    (timeQualifier == "morgens" or
                                     timeQualifier == "mittags"):
                                strHH += 12
            else:
                # try to parse # s without colons
                # 5 hours, 10 minutes etc.
                length = len(word)
                strNum = ""
                remainder = ""
                for i in range(length):
                    if word[i].isdigit():
                        strNum += word[i]
                    else:
                        remainder += word[i]

                if remainder == "":
                    remainder = wordNext.replace(".", "").lstrip().rstrip()

                if (
                        remainder == "pm" or
                        wordNext == "pm" or
                        remainder == "p.m." or
                        wordNext == "p.m."):
                    strHH = strNum
                    remainder = "pm"
                    used = 1
                elif (
                        remainder == "am" or
                        wordNext == "am" or
                        remainder == "a.m." or
                        wordNext == "a.m."):
                    strHH = strNum
                    remainder = "am"
                    used = 1
                else:
                    if wordNext == "pm" or wordNext == "p.m.":
                        strHH = strNum
                        remainder = "pm"
                        used = 1
                    elif wordNext == "am" or wordNext == "a.m.":
                        strHH = strNum
                        remainder = "am"
                        used = 1
                    elif (
                            int(word) > 100 and
                            (
                                wordPrev == "o" or
                                wordPrev == "oh"
                            )):
                        # 0800 hours (pronounced oh-eight-hundred)
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        military = True
                        if wordNext == "stunde":
                            used += 1
                    elif (
                            wordNext == "stunden" and
                            word[0] != '0' and
                            (
                                int(word) < 100 and
                                int(word) > 2400
                            )):
                        # ignores military time
                        # "in 3 hours"
                        hrOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1

                    elif wordNext == "minuten":
                        # "in 10 minutes"
                        minOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif wordNext == "sekunden":
                        # in 5 seconds
                        secOffset = int(word)
                        used = 2
                        isTime = False
                        hrAbs = -1
                        minAbs = -1
                    elif int(word) > 100:
                        strHH = int(word) / 100
                        strMM = int(word) - strHH * 100
                        military = True
                        if wordNext == "stunden":
                            used += 1
                    elif wordNext[0].isdigit():
                        strHH = word
                        strMM = wordNext
                        military = True
                        used += 1
                        if wordNextNext == "stunden":
                            used += 1
                    elif (
                            wordNext == "" or wordNext == "uhr" or
                            (
                                        wordNext == "um" and
                                        (
                                            wordNextNext == "um" or
                                            wordNextNext == timeQualifier
                                        )
                            )):
                        strHH = word
                        strMM = 00
                        if wordNext == "uhr":
                            used += 1
                        if wordNext == "am" or wordNextNext == "um" or wordNextNext == "zu":
                            used += (1 if wordNext == "in" else 2)
                            if (wordNextNext and
                                wordNextNext in timeQualifier or
                                (words[words.index(wordNextNext) + 1] and
                                 words[words.index(wordNextNext) + 1] in
                                 timeQualifier)):
                                if (wordNextNext == "nachmittag" or
                                    (len(words) >
                                     words.index(wordNextNext) + 1 and
                                     words[words.index(
                                         wordNextNext) + 1] == "nachmittag")):
                                    remainder = "pm"
                                if (wordNextNext == "abend" or
                                    (len(words) >
                                     (words.index(wordNextNext) + 1) and
                                     words[words.index(
                                         wordNextNext) + 1] == "abend")):
                                    remainder = "pm"
                                if (wordNextNext == "morgen" or
                                    (len(words) >
                                     words.index(wordNextNext) + 1 and
                                     words[words.index(
                                         wordNextNext) + 1] == "morgen")):
                                    remainder = "am"
                        if timeQualifier != "":
                            military = True
                    else:
                        isTime = False

            strHH = int(strHH) if strHH else 0
            strMM = int(strMM) if strMM else 0
            strHH = strHH + 12 if remainder == "pm" and strHH < 12 else strHH
            strHH = strHH - 12 if remainder == "am" and strHH >= 12 else strHH
            if strHH > 24 or strMM > 59:
                isTime = False
                used = 0
            if isTime:
                hrAbs = strHH * 1
                minAbs = strMM * 1
                used += 1
        if used > 0:
            # removed parsed words from the sentence
            for i in range(used):
                words[idx + i] = ""

            if wordPrev == "o" or wordPrev == "oh":
                words[words.index(wordPrev)] = ""

            if wordPrev == "früh":
                hrOffset = -1
                words[idx - 1] = ""
                idx -= 1
            elif wordPrev == "spät":
                hrOffset = 1
                words[idx - 1] = ""
                idx -= 1
            if idx > 0 and wordPrev in markers:
                words[idx - 1] = ""
            if idx > 1 and wordPrevPrev in markers:
                words[idx - 2] = ""

            idx += used - 1
            found = True

    # check that we found a date
    if not date_found:
        return None

    if dayOffset is False:
        dayOffset = 0

    # perform date manipulation

    extractedDate = dateNow
    extractedDate = extractedDate.replace(microsecond=0,
                                          second=0,
                                          minute=0,
                                          hour=0)
    if datestr != "":
        temp = datetime.strptime(datestr, "%B %d")
        if not hasYear:
            temp = temp.replace(year=extractedDate.year)
            if extractedDate < temp:
                extractedDate = extractedDate.replace(year=int(currentYear),
                                                      month=int(
                                                          temp.strftime(
                                                              "%m")),
                                                      day=int(temp.strftime(
                                                          "%d")))
            else:
                extractedDate = extractedDate.replace(
                    year=int(currentYear) + 1,
                    month=int(temp.strftime("%m")),
                    day=int(temp.strftime("%d")))
        else:
            extractedDate = extractedDate.replace(
                year=int(temp.strftime("%Y")),
                month=int(temp.strftime("%m")),
                day=int(temp.strftime("%d")))

    if timeStr != "":
        temp = datetime(timeStr)
        extractedDate = extractedDate.replace(hour=temp.strftime("%H"),
                                              minute=temp.strftime("%M"),
                                              second=temp.strftime("%S"))

    if yearOffset != 0:
        extractedDate = extractedDate + relativedelta(years=yearOffset)
    if monthOffset != 0:
        extractedDate = extractedDate + relativedelta(months=monthOffset)
    if dayOffset != 0:
        extractedDate = extractedDate + relativedelta(days=dayOffset)
    if hrAbs != -1 and minAbs != -1:

        extractedDate = extractedDate + relativedelta(hours=hrAbs,
                                                      minutes=minAbs)
        if (hrAbs != 0 or minAbs != 0) and datestr == "":
            if not daySpecified and dateNow > extractedDate:
                extractedDate = extractedDate + relativedelta(days=1)
    if hrOffset != 0:
        extractedDate = extractedDate + relativedelta(hours=hrOffset)
    if minOffset != 0:
        extractedDate = extractedDate + relativedelta(minutes=minOffset)
    if secOffset != 0:
        extractedDate = extractedDate + relativedelta(seconds=secOffset)
    for idx, word in enumerate(words):
        if words[idx] == "und" and words[idx - 1] == "" and words[
                idx + 1] == "":
            words[idx] = ""

    resultStr = " ".join(words)
    resultStr = ' '.join(resultStr.split())
    return [extractedDate, resultStr]


def isFractional_de(input_str):
    """
    This function takes the given text and checks if it is a fraction.

    Args:
        input_str (str): the string to check if fractional
    Returns:
        (bool) or (float): False if not a fraction, otherwise the fraction

    """
    if input_str.endswith('s', -1):
        input_str = input_str[:len(input_str) - 1]  # e.g. "fifths"

    aFrac = ["ganz", "halb", "dritte", "vierte", "fünft", "sechste",
             "siebte", "achte", "neunte", "zehnte", "elfte", "zwölfte"]

    if input_str.lower() in aFrac:
        return 1.0 / (aFrac.index(input_str) + 1)
    if input_str == "quartal":
        return 1.0 / 4

    return False


def normalize_de(text, remove_articles):
    """ German string normalization """ 

    words = text.split()  # this also removed extra spaces
    normalized = ""
    for word in words:
        if remove_articles and word in ["des", "dem", "das", "der", "den" ,"die"]:
            continue

        # Expand common contractions, e.g. "isn't" -> "is not"
        contraction = ["ist nicht", "sind nicht", "kippen", "könnte haben", "konnte nicht",
                       "werde", "muss",
                       "hatte nicht", "hat nicht", "habe nicht", "er würde", "er will", "er ist",
                       "wie", "wie wird", "wie ist", "Ich würde", "ich will", "Ich bin",
                       "Ich habe", "ist nicht", "es würde", "es wird", "es ist", "vielleicht nicht",
                       "könnte haben", "muss nicht", "muss", "sollte nicht",
                       "soll nicht", "Sie tat", "sie wird", "sie ist", "sollte nicht",
                       "sollte haben", "jemandes", "jemand", "jemand wird",
                       "das wird", "das ist", "das wäre",
                       "da bin ich", "da ist", "Sie würden", "sie werden", "Sie sind",
                       "Sie haben", "war nicht", "Wir machten", "wir werden", "wurden", "wir haben",
                       "waren nicht", "was", "was wird", "was ist",
                       "was ist das",  # technically incorrect but some STT outputs
                       "was hast du", "Wann ist", "wann", "Wo war ich", "wo ist",
                       "wo hast du", "Wer würde", "wer hätte", "Wer wird", "wer ist",
                       "Wer ist", "wer hat", "warum", "why's", "Warum",
                       "Ich will nicht", "würde haben", "würde nicht", "hätte nicht",
                       "ihr", "du würdest", "du hättest", "du wirst",
                       "du bist", "ja", "du bist", "du hast"]
        if word in contraction:
            expansion = ["ist nicht", "sind nicht", "kann nicht", "könnte haben",
                         "konnte nicht", "nicht", "unterlasse",
                         "gehen zu", "unterbreche", "hatte nicht", "hat nicht",
                         "nicht haben", "er würde", "er wird", "er ist",
                         "wie hast",
                         "wie wird", "wie ist", "Ich würde", "ich werde", "ich bin",
                         "ich habe", "ist nicht", "es würde", "es wird", "es ist",
                         "möglicherweise nicht", "könnte haben", "darf nicht", "haben müssen",
                         "braucht nicht", "sollte nicht", "Sie würde", "sie könnte",
                         "sie wird", "Sie ist", "sollte nicht", "sollte haben",
                         "jemand ist", "jemand würde", "jemand wird",
                         "jemand kann", "das wird", "das ist", "das würde",
                         "es würde", "Sie würden", "es gibt", "sie würden",
                         "Sie werden", "Sie sind", "Sie haben", "war nicht",
                         "wir würden", "wir werden", "wir sind", "wir haben",
                         "waren nicht", "was hat", "was wird", "Was sind",
                         "was ist", "was haben", "wann ist", "wann hat",
                         "wo war das", "wo ist", "wo haben", "wer würde",
                         "Wer hätte das getan", "Wer wird", "wer sind", "wer ist",
                         "Wer hat", "Warum", "warum sind", "warum ist",
                         "wird nicht", "wird", "hätte",
                         "würde nicht", "würde nicht haben", "ihr alle", "ihr alle",
                         "würdest", "würdest haben", "wirst",
                         "bist nicht", "bist nicht ", "hast", "habe"]
            word = expansion[contraction.index(word)]

        # Convert numbers into digits, e.g. "two" -> "2"
        textNumbers = ["nul", "eins", "zwei", "drei", "vier", "fünf", "sechs",
                       "sieben", "acht", "neun", "zehn", "elf", "zwölf",
                       "dreizehn", "vierzehn", "fünfzehn", "sechzehn",
                       "siebzehn", "achzehn", "neunzehn", "zwanzig"]
        if word in textNumbers:
            word = str(textNumbers.index(word))

        normalized += " " + word

    return normalized[1:]  # strip the initial space


#!/usr/local/opt/python/bin/python3.7
import re, csv, sys, argparse
from os import path

def cleanEncodingErrors(text):
    """Clears typical Uft8 read errors"""
    errors = {'\ufeff','\xa0','_\u200b_','\uf0b7'} #Detected bugs
    for error in errors:
            text = text.replace(error, '')
    return text


def parseFile(filePath, separator):
    """Parses a .txt file with regular separators"""
    f = open(filePath, 'r'); #Opens file in read mode.
    f_content = f.read().split(separator)
    #f_content = cleanEncodingErrors(f_content)
    hlSet = set(f_content)
    f.close()
    return hlSet


def structureSet(highlightSet):
    """Creates a dictionary where book names are keys and quotes are listed inside. 
    Cleans the text and treats UFT8 Encoding errors. To add new error edit cleanEncodingErrors()"""
    bookNames = set()
    quotesDictionary = {}
    err = 0

    bookNamePattern = re.compile("(?<=\n-\s)")
    quotePattern = re.compile("(?=\n\n)")

    for i in range(len(highlightSet)):
        actualHighlight = highlightSet.pop()
        try:
            actualBookName = bookNamePattern.split(actualHighlight)[0]
            actualQuote = quotePattern.split(actualHighlight)[1]
        except:
            err = err + 1
            continue

        #Bug corection utf-8 encoding and Text Cleaning
        actualBookName = cleanEncodingErrors(actualBookName)
        actualQuote = cleanEncodingErrors(actualQuote)
        actualBookName = actualBookName[1:-3]
        actualQuote = actualQuote[2:-1]

        #Appending to keys set
        bookNames = bookNames.union({actualBookName}) #Clear REGEX Matching chars

        #Appending content to dictionary
        if actualBookName in quotesDictionary:
            quotesDictionary[actualBookName].append(actualQuote)
        else:
            quotesDictionary[actualBookName] = [actualQuote]

    if err > 0: 
        #print(" [!] %d IMPORTING ERRORS HAVE BEEN DETECTED." %(err))
        pass
    return quotesDictionary


def isCompliant(quote):
    """Checks a few compliant parameters
    to filter bad quotes."""
    if quote == '':
        return False
    elif len(quote) < 30:
        return False
    else:
        return True


def exportCsv(CsvPath, quotesDictionary):
    """Writes quotes dictionary to new csv file on csvpath"""

    if path.exists(CsvPath):
        newCsvPath = CsvPath[:-4] + '-copy.csv'
    else:
        newCsvPath = CsvPath
    
    with open(newCsvPath, mode='w') as csv_file:
        csv_file_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        csv_file_writer.writerow(['Book Name', 'Quote'])
        
        for each_key in quotesDictionary.keys():
            for each_quote in quotesDictionary[each_key]:
                if isCompliant(each_quote): csv_file_writer.writerow([each_key, each_quote])
                    
    return 


if __name__ == "__main__":
    csv_name = "KindleHighlights.csv"
    separator = "=========="

    parser = argparse.ArgumentParser(description="Converts KindleHighlight files to Csv. Output file will be on the same path as input")
    parser.add_argument("input", type=str, help="KindleHighlights text file path")
    args = parser.parse_args()

    nb_path = args.input.rfind('/')
    if nb_path == -1:
        csv_path = './'+ csv_name
    else:
        csv_path = args.input[:nb_path] + '/' + csv_name

    highlight = parseFile(args.input,separator)
    quotes = structureSet(highlight)
    exportCsv(csv_path, quotes)

    print("Csv file created successfully on %s" %csv_path)





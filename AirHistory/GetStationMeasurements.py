import argparse
import json
import requests
import datetime
import os
import os.path
from pathlib import Path
from dateutil.relativedelta import relativedelta
from AirHistoryUtilities import GetPathFromArgument

dateFormat = "%Y-%m-%d"

def GetStartDate(inputDate):
    if inputDate is None:
        return datetime.datetime(2008,1,1)

    return datetime.datetime.strptime(inputDate, dateFormat)

def GetMeasurements(startDate, dirPath, isHourly):
    currentDate = datetime.datetime.now()
    month = relativedelta(months=+1)

    fileNamePprefix = "døgnmiddel"
    urlPath = "stats/day"

    if isHourly:
        fileNamePprefix = "timesmiddel"
        urlPath = "aq/historical"

    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

    while startDate < currentDate:
        endDate = startDate + month

        url = f'https://api.nilu.no/{urlPath}/{startDate.strftime(dateFormat)}/{endDate.strftime(dateFormat)}/all'
        
        fileName = f'{fileNamePprefix}-{startDate.strftime(dateFormat)}.json'
        filePath = os.path.join(dirPath, fileName)
        startDate = endDate

        if os.path.exists(filePath):
            print(f'{filePath} already exists. Skipping.')
            continue

        print(f'Downloading [{url}] to [{filePath}].')

        response = requests.get(url)
        response.raise_for_status()
        contents = response.text

        with open(filePath, mode="w", encoding="utf-8") as file: 
            file.write(contents)

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--outputpath", "-o", help="provide the output folder.")
argumentParser.add_argument("--startdate", "-s", help="provide the output folder in the format %Y-%m-%d")
argumentParser.add_argument("--hourly", "-t", action='store_true', help="a flag indicating that the hourly measurements should be retrieved instead of the daily.")

args = argumentParser.parse_args()

startDate = GetStartDate(args.startdate)
path = GetPathFromArgument("path", args.outputpath, False, True)

GetMeasurements(startDate, path, args.hourly)

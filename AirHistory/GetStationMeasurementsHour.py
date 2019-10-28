import json
import requests
import datetime
from datetime import timedelta
from time import time
import os
import os.path
from pathlib import Path
from dateutil.relativedelta import relativedelta

dirPath = Path('output')
dateFormat = "%Y-%m-%d"

currentDate = datetime.datetime.now()
month = relativedelta(months=+1)
startDate = datetime.datetime(2016,2,1)

if not os.path.exists(dirPath):
    os.mkdir(dirPath)

while startDate < currentDate:
    startTime = time()
    endDate = startDate + month

    url = f'https://api.nilu.no/aq/historical/{startDate.strftime(dateFormat)}/{endDate.strftime(dateFormat)}/all'
    print(url)

    response = requests.get(url, timeout=3600.0)
    response.raise_for_status()

    contents = response.text

    fileName = f'timesmiddel-{startDate.strftime(dateFormat)}.json'
    filePath = os.path.join(dirPath, fileName)

    with open(filePath, mode="w", encoding="utf-8") as file: 
        file.write(contents)
        
    duration = time() - startTime
    print(timedelta(seconds=duration).total_seconds())

    startDate = endDate




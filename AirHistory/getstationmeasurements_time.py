import json
import requests
import datetime
import os
import os.path
from pathlib import Path
from dateutil.relativedelta import relativedelta

dirPath = Path('obs')
dateFormat = "%Y-%m-%d"

currentDate = datetime.datetime.now()
month = relativedelta(months=+1)
startDate = datetime.datetime(2008,1,1)

if not os.path.exists(dirPath):
    os.mkdir(dirPath)

while startDate < currentDate:
    endDate = startDate + month

    url = f'https://api.nilu.no/obs/historical/{startDate.strftime(dateFormat)}/{endDate.strftime(dateFormat)}/all'
    print(url)

    response = requests.get(url)
    response.raise_for_status()

    contents = response.text

    fileName = f'timesmiddel-{startDate.strftime(dateFormat)}.json'
    filePath = os.path.join(dirPath, fileName)

    with open(filePath, mode="w", encoding="utf-8") as file: 
        file.write(contents)

    startDate = endDate




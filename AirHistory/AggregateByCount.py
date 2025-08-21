import argparse
import orjson
import datetime
import os
import os.path
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta
import calendar
from AirHistoryUtilities import GetPathFromArgument, GetValueTypeFromArgument

MinCoverage = 100

def InitializeThresholdList(settingsPath, valueType):
    thresholdsPath = settingsPath / f"thresholds_{valueType}.json"
    with open(thresholdsPath, "r", encoding="utf-8") as inputFile:
        raw_thresholds = orjson.loads(inputFile.read())

    global ThresholdMap
    ThresholdMap = {}
    for entry in raw_thresholds:
        for component, values in entry.items():
            if component != "ValidForYears":
                for year in entry["ValidForYears"]:
                    ThresholdMap[(component, year)] = values
    
    return ThresholdMap     

from concurrent.futures import ProcessPoolExecutor

def AggregateByThreshold(path, valueType, thresholds_totals):
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(HandleMunicipalityDir, directory, valueType, thresholds_totals)
            for directory in path.iterdir() if directory.is_dir()
        ]
        for future in futures:
            future.result()

def HandleMunicipalityDir(municipalityDir, valueType, thresholds_totals):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, valueType, thresholds_totals)

def HandleStation(entry, valueType, thresholds_totals):
    valuePath = os.path.join(entry, f"{valueType}_deduped.json")
    outputPath = os.path.join(entry, f"{valueType}_threshold.json")
    countStation = {}

    if(valueType == "hourly"):
        if("Hennig Olsen" in entry.name or "Holta øst" in entry.name):
            print("Skipping hourly data for Hennig Olsen and Holta øst")
            return None

    print(outputPath)
    startTime = time()
    with open(valuePath, mode="r", encoding="utf-8") as inputFile:
        valStation = orjson.loads(inputFile.read())
        countStation = {'components': [], **{k:v for k,v in valStation.items() if k != 'components'}}
        for component in valStation['components']:
            countComponent = HandleComponent(component, valueType, thresholds_totals)
            if not countComponent is None:
                countStation['components'].append(countComponent)

    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
         outputFile.write(orjson.dumps(countStation).decode())

    duration = time() - startTime
    print(timedelta(seconds=duration).total_seconds())

def HandleComponent(component, valueType, thresholds_totals):
    componentName = component["component"]
    countComp = None

    counts = {}
    for value in component['values']:
        UpdateCount(counts, value, componentName, valueType, thresholds_totals)
    
    if len(counts) > 0:
        countComp = {"component": componentName, "unit": component["unit"], "counts": []}
        countComp["counts"].extend(counts.values())
        
    return countComp

def UpdateCount(counts, value, componentName, valueType, thresholds_totals):
    year = GetYear(value)
    daysInYear = 366 if calendar.isleap(year) else 365
    hoursInYear = 8784  if calendar.isleap(year) else 8760

    thresholds = thresholds_totals.get((componentName, year))

    if thresholds is None:
        return

    if not year in counts:
        counts[year] = {"year":year, "validValues": 0, "lowerThreshold": 0, "upperThreshold": 0, "boundary": 0}

    if not ValidateValue(value, valueType):
        return

    if valueType == "hourly" and counts[year]["validValues"] == hoursInYear:
        raise Exception(f"Found more than 8760 hourly values in year {year}")

    if valueType == "daily" and counts[year]["validValues"] == daysInYear:
        raise Exception(f"Found more than 365 daily values in year {year}")

    counts[year]["validValues"] += 1

    val = value['value']
    if "lower" in thresholds and val >= thresholds["lower"]:
        counts[year]["lowerThreshold"] += 1

    if "upper" in thresholds and val >= thresholds["upper"]:
        counts[year]["upperThreshold"] += 1
        
    if val >= thresholds["boundary"]:
        counts[year]["boundary"] += 1

def GetYear(value):
    dateString = None
    if 'dateTime' in value:
        dateString = value['dateTime']
    elif 'fromTime' in value:
        dateString = value['fromTime']
    elif 'year' in value:
        return value['year']
    else:
        raise Exception(f"Unable to find date in value: {value}")

    startDate = parse(dateString)
    return startDate.year

def ValidateValue(value, valueType):
    global MinCoverage

    if valueType == "hourly" and value["qualityControlled"] == False:
        return False
    if valueType == "hourly" and value["timestep"] != 3600:
        raise Exception(f"Incorrect timestep found in value: {value}")
    if valueType == "daily" and value["coverage"] < MinCoverage:
        MinCoverage = value["coverage"]
    if valueType == "daily" and value["coverage"] < 75:
        #print(f"################  Invalid coverage: {value['coverage']} ################")
        return False

    return True

def main():
    path = GetPathFromArgument("path", args.path)
    settingsPath = GetPathFromArgument("thresholds", args.settings)
    valueType = GetValueTypeFromArgument(args.type)

    thresholds_totals = InitializeThresholdList(settingsPath, valueType)
    AggregateByThreshold(path, valueType, thresholds_totals )

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # For Windows compatibility

    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument("--path", "-p", help="provide the input folder")
    argumentParser.add_argument("--settings", "-s", help="provide the output folder")
    argumentParser.add_argument("--type", "-t", help="'hourly', 'daily' or 'yearly'")
    args = argumentParser.parse_args()

    main()
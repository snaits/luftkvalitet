import argparse
import json
import datetime
import os
import os.path
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta

CurrentHourFraction = 1.0

def GetPathFromArgument(argName, argValue):
    if argValue is None:
        raise Exception(f"{argName} path not provided")
    argPath = Path(argValue)
    VerifyPath(argName, argPath)
    return argPath

def VerifyPath(name, path):
    if not os.path.exists(path):
        raise Exception(f"{name} path does not exist: [{path}]")
    if not path.is_dir():
        raise Exception(f"{name} path is not a folder: [{path}]")

def AggregateByMean(path):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory)

def HandleMunicipalityDir(municipalityDir):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir)

def HandleStation(entry):
    valuePath = os.path.join(entry, f"hourly.json")
    outputPath = os.path.join(entry, f"yearly.json")
    countStation = {}

    print(outputPath)
    startTime = time()
    with open(valuePath, mode="r", encoding="utf-8") as inputFile:
        valStation = json.load(inputFile)
        countStation = valStation.copy()
        countStation['components'] = []
        for component in valStation['components']:
            countComponent = HandleComponent(component)
            if not countComponent is None:
                countStation['components'].append(countComponent)
    duration = time() - startTime
    print(timedelta(seconds=duration).total_seconds())

    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(countStation, outputFile)

def HandleComponent(component):
    componentName = component["component"]
    yearlyComp = None

    yearlyMeans = {}
    for value in component['values']:
        UpdateMean(yearlyMeans, value, componentName)
    
    if len(yearlyMeans) > 0:
        yearlyComp = {"component": componentName, "values": []}
        yearlyComp["values"].extend(yearlyMeans.values())
        
    return yearlyComp

def UpdateMean(counts, value, componentName):
    year = GetYear(value)

    if not ValidateValue:
        return

    if not year in counts:
        counts[year] = {"year":year, "validHours": 0, "aggregated": 0, "mean": 0}

    hourFraction = GetTimestepFraction(value)
    valueFraction = value['value'] * hourFraction

    counts[year]["validHours"] += hourFraction
    counts[year]["aggregated"] += valueFraction
    counts[year]["mean"] = counts[year]['aggregated'] / counts[year]["validHours"]

    global CurrentHourFraction
    if hourFraction != CurrentHourFraction:
        CurrentHourFraction = hourFraction
        print(f"---- {hourFraction} ---- {valueFraction}")

def GetYear(value):
    dateString = None
    if 'dateTime' in value:
        dateString = value['dateTime']
    elif 'fromTime' in value:
        dateString = value['fromTime']

    startDate = parse(dateString)
    return startDate.year

def ValidateValue(value):
    return value["qualityControlled"] == True

def GetTimestepFraction(value):
    timestep = value['timestep']

    if timestep > 3600:
        raise Exception(f"Timestep larger than on hour: {timestep}")

    return timestep/3600
    
def EnsurePathExists(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--path", "-p", help="provide the input folder")

args = argumentParser.parse_args()

path = GetPathFromArgument("path", args.path)

AggregateByMean(path)
import argparse
import json
import datetime
import os
import os.path
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta

ThresholdsList = []
MinCoverage = 100

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

def GetValueTypeFromArgument(valueType):
    if valueType is None:
        raise Exception("ValueType not provided")
    if valueType not in ["hourly","daily","yearly"]:
        raise Exception(f"ValueType [{valueType}] is not supported. The following types are supported: ['hourly', 'daily', 'yearly']")
    
    return valueType

def InitializeThresholdList(settingsPath, valueType):
    thresholdsPath = os.path.join(settingsPath.absolute(), f"thresholds_{valueType}.json")
    if not os.path.exists(thresholdsPath):
        raise Exception(f"Threshold file not found: [{thresholdsPath}]")

    with open(thresholdsPath, mode="r", encoding="utf-8") as inputFile:
        ThresholdsList.extend(json.load(inputFile))
        
    if len(ThresholdsList) == 0:
        raise Exception(f"Threshold file empty: [{thresholdsPath}]")
    
def AggregateByThreshold(path, valueType):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, valueType)
    print(f"MinCoverage: {MinCoverage}")

def HandleMunicipalityDir(municipalityDir, valueType):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, valueType)

def HandleStation(entry, valueType):
    valuePath = os.path.join(entry, f"{valueType}.json")
    outputPath = os.path.join(entry, f"{valueType}_threshold.json")
    countStation = {}

    print(outputPath)
    startTime = time()
    with open(valuePath, mode="r", encoding="utf-8") as inputFile:
        valStation = json.load(inputFile)
        countStation = valStation.copy()
        countStation['components'] = []
        for component in valStation['components']:
            countComponent = HandleComponent(component, valueType)
            if not countComponent is None:
                countStation['components'].append(countComponent)

    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(countStation, outputFile)

    duration = time() - startTime
    print(timedelta(seconds=duration).total_seconds())

def HandleComponent(component, valueType):
    componentName = component["component"]
    countComp = None

    counts = {}
    for value in component['values']:
        UpdateCount(counts, value, componentName, valueType)
    
    if len(counts) > 0:
        countComp = {"component": componentName, "unit": component["unit"], "counts": []}
        countComp["counts"].extend(counts.values())
        
    return countComp

def UpdateCount(counts, value, componentName, valueType):
    year = GetYear(value)

    thresholds = GetThresholds(componentName, year)
    if thresholds is None:
        return

    if not year in counts:
        counts[year] = {"year":year, "validValues": 0, "lowerThreshold": 0, "upperThreshold": 0, "boundary": 0}

    if not ValidateValue(value, valueType):
        return
    counts[year]["validValues"] += 1

    val = value['value']
    if "lower" in thresholds and val > thresholds["lower"]:
        counts[year]["lowerThreshold"] += 1

    if "upper" in thresholds and val > thresholds["upper"]:
        counts[year]["upperThreshold"] += 1
        
    if val > thresholds["boundary"]:
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
    if valueType == "daily" and value["coverage"] < 85:
        #print(f"################  Invalid coverage: {value['coverage']} ################")
        return False

    return True
    
def GetThresholds(componentName, year):
    for thresholds in ThresholdsList:
        if (componentName in thresholds) and (year in thresholds["ValidForYears"]):
            return thresholds[componentName]
            
    return None

def EnsurePathExists(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--path", "-p", help="provide the input folder")
argumentParser.add_argument("--settings", "-s", help="provide the output folder")
argumentParser.add_argument("--type", "-t", help="'hourly', 'daily' or 'yearly'")

args = argumentParser.parse_args()

path = GetPathFromArgument("path", args.path)
settingsPath = GetPathFromArgument("thresholds", args.settings)
valueType = GetValueTypeFromArgument(args.type)

InitializeThresholdList(settingsPath, valueType)
AggregateByThreshold(path, valueType)
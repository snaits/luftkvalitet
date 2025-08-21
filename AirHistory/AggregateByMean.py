import argparse
import orjson
import datetime
import os
import os.path
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta
from AirHistoryUtilities import GetPathFromArgument

PreviousWeirdComponent = ""

def AggregateByMean(path, outputFileName):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, outputFileName)

def HandleMunicipalityDir(municipalityDir, outputFileName):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, outputFileName)

def HandleStation(entry, outputFileName):
    valuePath = os.path.join(entry, "hourly_deduped.json")
    outputPath = os.path.join(entry, outputFileName)
    countStation = {}
    
    if("Hennig Olsen" in entry.name or "Holta øst" in entry.name):
        print("Skipping hourly data for ", entry.name)
        return None

    print(outputPath)
    startTime = time()
    with open(valuePath, mode="r", encoding="utf-8") as inputFile:
        valStation = orjson.loads(inputFile.read())
        countStation = valStation.copy()
        countStation['components'] = []
        for component in valStation['components']:
            countComponent = HandleComponent(component)
            if not countComponent is None:
                countStation['components'].append(countComponent)
    duration = time() - startTime
    print(timedelta(seconds=duration).total_seconds())

    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        outputFile.write(orjson.dumps(countStation).decode())

def HandleComponent(component):
    componentName = component["component"]
    yearlyComp = None

    yearlyMeans = {}
    for value in component['values']:
        UpdateMean(yearlyMeans, value, componentName)
    
    if len(yearlyMeans) > 0:
        yearlyComp = {"component": componentName, "unit": component['unit'], "values": []}
        yearlyComp["values"].extend(yearlyMeans.values())
        
    return yearlyComp

def UpdateMean(counts, value, componentName):
    year = GetYear(value)

    if not ValidateValue:
        return

    if not year in counts:
        counts[year] = {"year":year, "validHours": 0, "aggregated": 0, "value": 0}

    hourFraction = GetTimestepFraction(value, componentName)
    valueFraction = value['value'] * hourFraction

    counts[year]["validHours"] += hourFraction
    counts[year]["aggregated"] += valueFraction
    counts[year]["value"] = counts[year]['aggregated'] / counts[year]["validHours"]

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

def GetTimestepFraction(value, componentName):
    timestep = value['timestep']

    if timestep > 3600:
        raise Exception(f"Timestep larger than on hour: {timestep}")

    if timestep != 3600:
        global PreviousWeirdComponent
        if componentName != PreviousWeirdComponent:
            PreviousWeirdComponent = componentName
            print(f"---- {componentName} ---- {timestep}")

    return timestep/3600
    
argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--path", "-p", help="provide the folder containing all station folders")
argumentParser.add_argument("--outputfile", "-o", help="provide the name of the output files")

args = argumentParser.parse_args()

path = GetPathFromArgument("path", args.path)
outputFileName = args.outputfile

AggregateByMean(path, outputFileName)
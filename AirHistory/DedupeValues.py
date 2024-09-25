import argparse
import json
import datetime
import os
import os.path
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta
from AirHistoryUtilities import GetPathFromArgument, GetValueTypeFromArgument

def prYellow(skk): print("\033[93m {}\033[00m" .format(skk))

def Dedupe(path, valueType):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, valueType)

def HandleMunicipalityDir(municipalityDir, valueType):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, valueType)

def HandleStation(entry, valueType):
    valuePath = os.path.join(entry, f"{valueType}.json")
    outputPath = os.path.join(entry, f"{valueType}_deduped.json")
    dedupedStation = {}
    newComponents = {}
    valueDeduper = {}
    
    if not os.path.isfile(valuePath):
        return

    print(outputPath)
    startTime = time()
    with open(valuePath, mode="r", encoding="utf-8") as inputFile:
        valStation = json.load(inputFile)
        dedupedStation = valStation.copy()
        dedupedStation['components'] = []
        originalValueCount = {}
        for component in valStation['components']:
            componentName = component['component']
            if not componentName in newComponents:
                newComponents[componentName] = component.copy()
                newComponents[componentName]['values'] = []
                dedupedStation['components'].append(newComponents[componentName])
                valueDeduper[componentName] = {}
                originalValueCount[componentName] = 0
            
            originalValueCount[componentName] += len(component['values'])
            HandleComponent(component, valueDeduper[componentName], valueType)
        
        for newComponent in dedupedStation['components']:
            componentName = newComponent['component']
            valueCount = 0
            for value in valueDeduper[componentName].values():
                newComponent['values'].append(value)
                valueCount += 1

            removedCount = originalValueCount[componentName] - valueCount
            if removedCount > 0:
                print(f"Removed {removedCount} values from component [{componentName}] in file: {outputPath}")

    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(dedupedStation, outputFile)

    duration = time() - startTime
    print(timedelta(seconds=duration).total_seconds())

def HandleComponent(component, valueDeduper, valueType):
    componentName = component["component"]
    
    for value in component['values']:
        timestamp = value['dateTime'] if valueType == 'daily' else value['fromTime']
        valueId = f"{componentName}-{timestamp}"
        if valueId in valueDeduper and valueDeduper[valueId]['timestep'] < value['timestep']:
            continue
        valueDeduper[valueId] = value


argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--path", "-p", help="provide the input folder")
argumentParser.add_argument("--type", "-t", help="'hourly', 'daily' or 'yearly'")

args = argumentParser.parse_args()

path = GetPathFromArgument("path", args.path)
valueType = GetValueTypeFromArgument(args.type)

Dedupe(path, valueType)
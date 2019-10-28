import argparse
import json
import datetime
import os
import os.path
import csv
import calendar
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta


def GetPathFromArgument(argName, argValue):
    if argValue is None:
        raise Exception(f"{argName} path not provided")
    argPath = Path(argValue)
    VerifyPath(argName, argPath)
    return argPath

def GetValueTypeFromArgument(valueType):
    if valueType is None:
        raise Exception("ValueType not provided")
    if valueType not in ["hourly","daily","yearly"]:
        raise Exception(f"ValueType [{valueType}] is not supported. The following types are supported: ['hourly', 'daily', 'yearly']")
    
    return valueType

def VerifyPath(name, path):
    if not os.path.exists(path):
        raise Exception(f"{name} path does not exist: [{path}]")
    if not path.is_dir():
        raise Exception(f"{name} path is not a folder: [{path}]")

def AddThresholdValues(path, valueType):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, valueType)

def HandleMunicipalityDir(municipalityDir, valueType):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, valueType)


def HandleStation(stationPath, valueType):
    station = stationPath.name

    print(f"{stationPath}")

    thresholdStation = GetThresholdsStation(stationPath, valueType)
    yearlyStation = GetYearlyStation(stationPath)

    components = thresholdStation["components"]
    for component in components:
        yearlyComponent = GetOrCreateComponent(yearlyStation, component)
        for value in component["counts"]:
            yearlyValue = GetOrCreateValue(yearlyComponent, value["year"])
            AddThreshold(value, yearlyValue, valueType)

    print(f"{stationPath} : {len(components)}")

    OutputStation(stationPath, yearlyStation)

def GetOrCreateComponent(yearlyStation, component):
    for yearlyComponent in yearlyStation["components"]:
        if yearlyComponent["component"] == component["component"]:
            return yearlyComponent
    newComponent = {"component": component["component"], "values": []}
    yearlyStation["components"].append(newComponent)
    return newComponent

def GetOrCreateValue(yearlyComponent, year):
    for yearlyValue in yearlyComponent["values"]:
        if yearlyValue["year"] == year:
            return yearlyValue
    newValue = {"year": year}
    yearlyValue["values"].append(newValue)
    return newValue

def AddThreshold(value, yearlyValue, valueType):
    yearlyValue[f"{valueType}LowerCount"] = value["lowerThreshold"]
    yearlyValue[f"{valueType}UpperCount"] = value["upperThreshold"]
    yearlyValue[f"{valueType}BoundaryCount"] = value["boundary"]
    
def GetThresholdsStation(stationPath, valueType):
    inputPath = os.path.join(stationPath, f"{valueType}_threshold.json")
    with open(inputPath, mode="r", encoding="utf-8") as inputFile:
        station = json.load(inputFile)
    return station

def GetYearlyStation(stationPath):
    inputPath = os.path.join(stationPath, f"yearly.json")
    with open(inputPath, mode="r", encoding="utf-8") as inputFile:
        station = json.load(inputFile)
    return station

def OutputStation(stationPath, station):
    outputPath = os.path.join(stationPath, f"yearly.json")
    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(station, outputFile)


argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--settings", "-s", help="provide the output folder")
argumentParser.add_argument("--path", "-p", help="provide the input folder")
argumentParser.add_argument("--type", "-t", help="'hourly', 'daily'")

args = argumentParser.parse_args()

settingsPath = GetPathFromArgument("thresholds", args.settings)
path = GetPathFromArgument("path", args.path)
valueType = GetValueTypeFromArgument(args.type)

AddThresholdValues(path, valueType)
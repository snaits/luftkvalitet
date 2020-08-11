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


ThresholdsList = []

MinimumValidHours = 7403
MiminumValidHoursLeap = 7423


def InitializeThresholdList(settingsPath):
    thresholdsPath = os.path.join(settingsPath.absolute(), f"thresholds_yearly.json")
    if not os.path.exists(thresholdsPath):
        raise Exception(f"Threshold file not found: [{thresholdsPath}]")

    with open(thresholdsPath, mode="r", encoding="utf-8") as inputFile:
        ThresholdsList.extend(json.load(inputFile))
        
    if len(ThresholdsList) == 0:
        raise Exception(f"Threshold file empty: [{thresholdsPath}]")

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

def AddYearlyThresholdValues(path, inputFileName, outputFileName):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, inputFileName, outputFileName)

def HandleMunicipalityDir(municipalityDir, inputFileName, outputFileName):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, inputFileName, outputFileName)


def HandleStation(stationDir, inputFileName, outputFileName):
    print(f"{stationDir}")

    station = GetStation(stationDir, inputFileName)
    components = station["components"]
    for component in components:
        for value in component["values"]:
            AddThreshold(value, component['component'])

    print(f"{stationDir} : {len(components)}")

    OutputStation(station, stationDir, outputFileName)


def AddThreshold(value, componentName):
    year = value["year"]
    if year == 2019:
        return

    value["isValid"] = CheckValidity(value)

    thresholds = GetThresholds(componentName, year)
    if thresholds is None:
        return

    numericValue = value['value']
    value["aboveLowerThreshold"] = "lower" in thresholds and numericValue > thresholds["lower"]
    value["aboveUpperThreshold"] = "upper" in thresholds and numericValue > thresholds["upper"]
    value["aboveBoundary"] = numericValue > thresholds["boundary"]

    if value["aboveBoundary"]:
        print(f"{componentName} -- {year}")

def GetThresholds(componentName, year):
    for thresholds in ThresholdsList:
        if (componentName in thresholds) and (year in thresholds["ValidForYears"]):
            return thresholds[componentName]
            
    return None

def CheckValidity(value):
    if "qualityControlled" in value:
        return value["qualityControlled"]
    
    if "validHours" in value:
        requiredHours = MiminumValidHoursLeap if calendar.isleap(value["year"]) else MinimumValidHours
        return value["validHours"] >= requiredHours

    raise Exception(f"Unable to determine validity: {value}")


def GetStation(stationPath, inputFileName):
    inputPath = os.path.join(stationPath, inputFileName)
    with open(inputPath, mode="r", encoding="utf-8") as inputFile:
        station = json.load(inputFile)
    return station

def OutputStation(station, stationDir, outputFileName):
    outputPath = os.path.join(stationDir, outputFileName)
    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(station, outputFile)


argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--settings", "-s", help="provide the output folder")
argumentParser.add_argument("--path", "-p", help="provide the folder containing all station folders")
argumentParser.add_argument("--inputfile", "-i", help="provide the name of the input files")
argumentParser.add_argument("--outputfile", "-o", help="provide the name of the output files")

args = argumentParser.parse_args()

settingsPath = GetPathFromArgument("thresholds", args.settings)
path = GetPathFromArgument("path", args.path)
inputFileName = args.inputfile
outputFileName = args.outputfile

InitializeThresholdList(settingsPath)
AddYearlyThresholdValues(path, inputFileName, outputFileName)
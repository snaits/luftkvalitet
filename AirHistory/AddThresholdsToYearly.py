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
from AirHistoryUtilities import GetPathFromArgument, VerifyPath, GetValueTypeFromArgument

def AddThresholdValues(path, valueType, inputFileName, outputFileName):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, valueType, inputFileName, outputFileName)

def HandleMunicipalityDir(municipalityDir, valueType, inputFileName, outputFileName):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, valueType, inputFileName, outputFileName)


def HandleStation(stationPath, valueType, inputFileName, outputFileName):
    print(f"{stationPath}")

    thresholdStation = GetThresholdsStation(stationPath, valueType)
    yearlyStation = GetYearlyStation(stationPath, inputFileName)

    components = thresholdStation["components"]
    for component in components:
        yearlyComponent = GetOrCreateComponent(yearlyStation, component)
        for value in component["counts"]:
            yearlyValue = GetOrCreateValue(yearlyComponent, value["year"])
            AddThreshold(value, yearlyValue, valueType)

    print(f"{stationPath} : {len(components)}")

    OutputStation(stationPath, yearlyStation, outputFileName)

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

def GetYearlyStation(stationPath, inputFileName):
    inputPath = os.path.join(stationPath, inputFileName)
    with open(inputPath, mode="r", encoding="utf-8") as inputFile:
        station = json.load(inputFile)
    return station

def OutputStation(stationPath, station, outputFileName):
    outputPath = os.path.join(stationPath, outputFileName)
    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(station, outputFile)


argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--settings", "-s", help="provide the output folder")
argumentParser.add_argument("--path", "-p", help="provide the folder containing all station folders")
argumentParser.add_argument("--inputfile", "-i", help="provide the name of the yearly input files")
argumentParser.add_argument("--outputfile", "-o", help="provide the name of the yearly output files")
argumentParser.add_argument("--type", "-t", help="'hourly', 'daily'")

args = argumentParser.parse_args()

settingsPath = GetPathFromArgument("thresholds", args.settings)
path = GetPathFromArgument("path", args.path)
inputFileName = args.inputfile
outputFileName = args.outputfile
valueType = GetValueTypeFromArgument(args.type)

AddThresholdValues(path, valueType, inputFileName, outputFileName)
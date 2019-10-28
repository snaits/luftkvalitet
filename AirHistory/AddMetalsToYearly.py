import argparse
import json
import datetime
import os
import os.path
import csv
from pathlib import Path
from dateutil.parser import parse
from time import time
from datetime import timedelta

MetalValues = []

def InitializeMetalValues(path):
    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter = ';', skipinitialspace=True)
        
        for row in reader:
            value = {}
            for field in reader.fieldnames:
                value[field] = row[field]
            MetalValues.append(value)
                

def GetPathFromArgument(argName, argValue, isFileExpected = False):
    if argValue is None:
        raise Exception(f"{argName} path not provided")

    argPath = Path(argValue)
    VerifyPath(argName, argPath, isFileExpected)
    return argPath

def VerifyPath(name, path, isFileExpected):
    if not os.path.exists(path):
        raise Exception(f"{name} path does not exist: [{path}]")
    if (not isFileExpected) and not path.is_dir():
        raise Exception(f"{name} path is not a folder: [{path}]")
    if isFileExpected and not path.is_file():
        raise Exception(f"{name} path is not a file: [{path}]")

def AddYearlyMetalValues(path):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory)

def HandleMunicipalityDir(municipalityDir):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir)


def HandleStation(stationPath):
    station = stationPath.name
    stationMetalValues = FindStationMetalValues(station)
    
    metalComponents = AggregateUnderComponent(stationMetalValues)

    components = GetNonMetalComponents(stationPath)
    components["components"] += metalComponents

    print(f"{stationPath} : {len(metalComponents)}")

    OutputComponents(stationPath, components)


def FindStationMetalValues(station):
    stationValues = []
    for metalValue in MetalValues:
        if metalValue["Stasjon"] == station:
            stationValues.append(metalValue)
            

    return stationValues


def AggregateUnderComponent(stationMetalValues):
    components = {}
    for metalValue in stationMetalValues:
        componentName = metalValue["Komponent"]
        if not componentName in components:
            components[componentName] = {}
            components[componentName]["component"] = componentName
            components[componentName]["unit"] = metalValue["Enhet"]
            components[componentName]["values"] = []

        standardValue = CreateStandardValue(metalValue)
        components[componentName]["values"].append(standardValue)

    return components.values()

def CreateStandardValue(metalValue):
    standardValue = {}
    fromDate = parse(metalValue["Fra-tid"])
    standardValue["year"] = fromDate.year
    standardValue["qualityControlled"] = metalValue["QC-flagg"] == "4 (Kvalitetsikret data)"
    standardValue["value"] = float(metalValue["Verdi"].replace(',', '.'))
    return standardValue


def GetNonMetalComponents(stationPath):
    inputPath = os.path.join(stationPath, f"yearly-non-metal.json")
    with open(inputPath, mode="r", encoding="utf-8") as inputFile:
        components = json.load(inputFile)
    return components

def OutputComponents(stationPath, components):
    outputPath = os.path.join(stationPath, f"yearly-all.json")
    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(components, outputFile)


argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--metals", "-m", help="provide the input file for metals")
argumentParser.add_argument("--path", "-p", help="provide the input folder")

args = argumentParser.parse_args()

metalsPath = GetPathFromArgument("metals", args.metals, True)
path = GetPathFromArgument("path", args.path)

InitializeMetalValues(metalsPath)
AddYearlyMetalValues(path)
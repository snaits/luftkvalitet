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
from AirHistoryUtilities import GetPathFromArgument

MetalValues = []

def InitializeMetalValues(path):
    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, dialect='excel', delimiter = ';', skipinitialspace=True)
        
        for row in reader:
            value = {}
            for field in reader.fieldnames:
                value[field] = row[field]
            MetalValues.append(value)
            
def AddYearlyMetalValues(path, inputFileName, outputFileName):
    for directory in path.iterdir():
        if not directory.is_dir():
            continue
        HandleMunicipalityDir(directory, inputFileName, outputFileName)

def HandleMunicipalityDir(municipalityDir, inputFileName, outputFileName):
    for stationDir in municipalityDir.iterdir():
        if stationDir.is_file():
            continue
        HandleStation(stationDir, inputFileName, outputFileName)


def HandleStation(stationPath, inputFileName, outputFileName):
    station = stationPath.name
    stationMetalValues = FindStationMetalValues(station)
    
    metalComponents = AggregateUnderComponent(stationMetalValues)

    components = GetNonMetalComponents(stationPath, inputFileName)
    components["components"] += metalComponents

    print(f"{stationPath} : {len(metalComponents)}")

    OutputComponents(stationPath, components, outputFileName)


def FindStationMetalValues(station):
    stationValues = []
    for metalValue in MetalValues:
        try:
            if metalValue["Stasjon"] == station:
                stationValues.append(metalValue)
        except KeyError:
            print("key error" + str(metalValue))
            

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


def GetNonMetalComponents(stationPath, inputFileName):
    inputPath = os.path.join(stationPath, inputFileName)
    with open(inputPath, mode="r", encoding="utf-8") as inputFile:
        components = json.load(inputFile)
    return components

def OutputComponents(stationPath, components, outputFileName):
    outputPath = os.path.join(stationPath, outputFileName)
    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(components, outputFile)


argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--metals", "-m", help="provide the input file for metals")
argumentParser.add_argument("--path", "-p", help="provide the folder containing all station folders")
argumentParser.add_argument("--inputfile", "-i", help="provide the name of the input files")
argumentParser.add_argument("--outputfile", "-o", help="provide the name of the output files")

args = argumentParser.parse_args()

metalsPath = GetPathFromArgument("metals", args.metals, True)
path = GetPathFromArgument("path", args.path)
inputFileName = args.inputfile
outputFileName = args.outputfile

InitializeMetalValues(metalsPath)
AddYearlyMetalValues(path, inputFileName, outputFileName)
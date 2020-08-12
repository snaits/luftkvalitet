import argparse
import json
import datetime
import os
import os.path
from AirHistoryUtilities import EnsurePathExists, GetPathFromArgument, VerifyPath, GetValueTypeFromArgument
from pathlib import Path

# Globals
stationsByMunicipality = {}
componentsByStation = {}
municipalityNumberByName = {}

def InitializeMunicipalities(path):
    data = {}
    with open(path.absolute(), mode="r", encoding="utf-8") as inputFile:
        data = json.load(inputFile)

    counties = data["countyList"]
    for county in counties:
        municipalities = county["municipalityList"]
        for municipality in municipalities:
            municipalityNumberByName[municipality["name"]] = municipality["municipalityNumber"]

def AggregateValuesByStation(inputPath, outputPath, valueType):
    print(f"input: {inputPath.absolute()} - output: {outputPath.absolute()} - type: {valueType}")
    for inputMonthFilePath in inputPath.iterdir():
        if inputMonthFilePath.is_dir():
            continue
        HandleFile(inputMonthFilePath)

    OutputJsonFiles(outputPath, valueType)

def HandleFile(path):
    data = []
    print(f"path: {path.absolute()}")
    #with open(path.absolute(), mode="r", encoding="iso-8859-1") as inputFile:
    with open(path.absolute(), mode="r", encoding="utf-8") as inputFile:
        data = json.load(inputFile)

    for component in data:
        HandleComponent(component)

def HandleComponent(component):
    storedComponent = GetOrCreateStoredComponent(component)
    VerifyComponentCompatibility(storedComponent, component)
    AddValues(storedComponent, component)

def VerifyComponentCompatibility(oldComponent, newComponent):
    VerifyComponentPropertyCompatibility(oldComponent, newComponent, 'unit')

def VerifyComponentPropertyCompatibility(oldComponent, newComponent, propertyName):
    if(not propertyName in newComponent):
        print(f'{propertyName} not found')
        return

    if(not propertyName in oldComponent):
        oldComponent[propertyName] = newComponent[propertyName]
        print(f'{propertyName} not set with new value')
        return

    if(oldComponent[propertyName] != newComponent[propertyName]):
        message = f'Component not compatible with component from previous month(s). [component={oldComponent[propertyName]}] vs [component={newComponent[propertyName]}]'
        print(message)
        raise Exception(message) 
    
def GetOrCreateStoredComponent(component):
    componentName = component['component']
    municipality = component['municipality'] if component["municipality"] != r"N/A" else component["area"]
    stationName = component['station']

    if not municipality in stationsByMunicipality:
        stationsByMunicipality[municipality] = {}

    if not municipality in municipalityNumberByName:
        print(f"Municipality number for [{municipality}] not found")
        municipalityNumberByName[municipality] = r"N/A"

    stations = stationsByMunicipality[municipality]
    if not stationName in stations:
        stations[stationName] = {"municipality": municipality, "municipalityNumber": municipalityNumberByName[municipality],"station": stationName, "components": []}

    if not stationName in componentsByStation:
        componentsByStation[stationName] = {}

    components = componentsByStation[stationName]
    if not componentName in components:
        components[componentName] = CreateStoredComponent(component)
        stations[stationName]["components"].append(components[componentName])

    return components[componentName]

def CreateStoredComponent(component):
    storedComponent = {
        "component": component['component'],
        "unit": component['unit'],
        "values": []
    }

    return storedComponent
    
def AddValues(storedComponent, component):
    for value in component["values"]:
        value["timestep"] = component['timestep']

    storedComponent["values"] += component["values"]
  
def OutputJsonFiles(outputPath, valueType):
    for municipality in stationsByMunicipality:
        municipalityPath = os.path.join(outputPath, municipality)
        EnsurePathExists(municipalityPath)

        stations = stationsByMunicipality[municipality]
        for stationName in stations:
            stationPath = os.path.join(municipalityPath, stationName)
            EnsurePathExists(stationPath)

            outputFilePath = os.path.join(stationPath, f'{valueType}.json')
            print(stationPath)
            with open(outputFilePath, mode="w", encoding="utf-8") as stationFile:
                json.dump(stations[stationName], stationFile)

argumentParser = argparse.ArgumentParser()
argumentParser.add_argument("--input", "-i", help="provide the input folder")
argumentParser.add_argument("--output", "-o", help="provide the output folder")
argumentParser.add_argument("--municipalities", "-m", help="provide the output folder")
argumentParser.add_argument("--type", "-t", help="'hourly', 'daily' or 'yearly'")

args = argumentParser.parse_args()

inputPath = GetPathFromArgument("input", args.input)
outputPath = GetPathFromArgument("output", args.output, False, True)
municipalitiesPath = GetPathFromArgument("municipalities", args.municipalities, True)
valueType = GetValueTypeFromArgument(args.type)

InitializeMunicipalities(municipalitiesPath)
AggregateValuesByStation(inputPath, outputPath, valueType)
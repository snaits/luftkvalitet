import json
import datetime
import os
import os.path
from pathlib import Path

inputPath = Path('output')

stationsByMunicipality = {}
componentsByStation = {}

def HandleDirectory(path):
    print(inputPath.absolute())
    for entry in inputPath.iterdir():
        if entry.is_dir():
            continue
        HandleFile(entry)

    OutputJsonFiles(inputPath)

def HandleFile(entry):
    with open(entry.absolute(), mode="r", encoding="utf-8") as inputFile:
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

    stations = stationsByMunicipality[municipality]
    if not stationName in stations:
        stations[stationName] = {"municipality": municipality, "station": stationName, "components": []}

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

    storedComponent["values"].extend(component["values"])
    
def OutputJsonFiles(path):
    outputPath = os.path.join(inputPath, "Aggregated")
    EnsurePathExists(outputPath)

    for municipality in stationsByMunicipality:
        municipalityPath = os.path.join(outputPath, municipality)
        EnsurePathExists(municipalityPath)

        valuesPath = os.path.join(municipalityPath, "Values")
        EnsurePathExists(valuesPath)

        stations = stationsByMunicipality[municipality]
        for stationName in stations:
            stationPath = os.path.join(valuesPath, f'{stationName}.json')
            print(stationPath)
            with open(stationPath, mode="w", encoding="utf-8") as stationFile:
                json.dump(stations[stationName], stationFile)

def EnsurePathExists(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

HandleDirectory(inputPath)

import json
import datetime
import os
import os.path
from pathlib import Path
from dateutil.parser import parse

thresholds = {
    "SO2": { "lower": 10000, "upper": 14000,"boundary": 350},
    "NO2": {"lower": 100, "upper": 140, "boundary": 200}
    }

def HandleDirectory(path):
    for entry in path.iterdir():
        if not entry.is_dir():
            continue
        HandleMunicipalityDir(entry)

def HandleMunicipalityDir(entry):
    valuesPath = os.path.join(entry.absolute(), "Values")
    valuesDir = Path(valuesPath)
    outputDirPath = os.path.join(entry.absolute(), "ThresholdCount")
    EnsurePathExists(outputDirPath)
    for fileInDir in valuesDir.iterdir():
        if fileInDir.is_dir():
            continue
        HandleStation(fileInDir, outputDirPath)

def HandleStation(entry, outputDirPath):
    countStation = {}
    with open(entry.absolute(), mode="r", encoding="utf-8") as inputFile:
        valStation = json.load(inputFile)
        countStation = valStation.copy()
        countStation['components'] = []
        for component in valStation['components']:
            countComponent = HandleComponent(component)
            if not countComponent is None:
                countStation['components'].append(countComponent)

    outputPath = os.path.join(outputDirPath, entry.name)
    with open(outputPath, mode="w", encoding="utf-8") as outputFile:
        json.dump(countStation, outputFile)

def HandleComponent(component):
    componentName = component["component"]
    countComp = {"component": componentName, "counts": []}
    if not componentName in thresholds:
        return

    counts = {}
    for value in component['values']:
        UpdateCount(counts, value, thresholds[componentName])
    
    countComp["counts"].extend(counts.values())
    return countComp

def UpdateCount(counts, value, threshold):
    startDate = parse(value['dateTime'])
    year = startDate.year

    if not year in counts:
        counts[year] = {"year":year, "lowerThreshold": 0, "upperThreshold": 0, "boundary": 0}

    val = value['value']

    if val > threshold["lower"]:
        counts[year]["lowerThreshold"] += 1

    if val > threshold["upper"]:
        counts[year]["upperThreshold"] += 1
        
    if val > threshold["boundary"]:
        counts[year]["boundary"] += 1

def EnsurePathExists(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

inputDir = Path('output/Aggregated')
HandleDirectory(inputDir)
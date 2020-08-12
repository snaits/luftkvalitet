import os
import os.path
from pathlib import Path

def GetPathFromArgument(argName, argValue, isFileExpected = False, createFolder = False):
    assert not (isFileExpected and createFolder)

    if argValue is None:
        raise Exception(f"{argName} path not provided")

    argPath = Path(argValue)
    if createFolder:
        EnsurePathExists(argPath)

    VerifyPath(argName, argPath, isFileExpected)
    return argPath

def VerifyPath(name, path, isFileExpected):
    if not os.path.exists(path):
        raise Exception(f"{name} path does not exist: [{path}]")
    if (not isFileExpected) and not path.is_dir():
        raise Exception(f"{name} path is not a folder: [{path}]")
    if isFileExpected and not path.is_file():
        raise Exception(f"{name} path is not a file: [{path}]")

def EnsurePathExists(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath)

def GetValueTypeFromArgument(valueType):
    if valueType is None:
        raise Exception("ValueType not provided")
    if valueType not in ["hourly","daily","yearly"]:
        raise Exception(f"ValueType [{valueType}] is not supported. The following types are supported: ['hourly', 'daily', 'yearly']")
    
    return valueType

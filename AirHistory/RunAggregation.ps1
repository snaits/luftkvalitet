$startDate = "2008-01-01"

Write-Host -ForegroundColor Green "`r`nRunning GetStationMeasurements for daily measurements."
python.exe GetStationMeasurements.py --startdate $startDate --outputpath ./daily
if(-not $?){throw "GetStationMeasurements daily failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning GetStationMeasurements for hourly measurements."
python.exe GetStationMeasurements.py --hourly --startdate $startDate --outputpath ./hourly
if(-not $?){throw "GetStationMeasurements hourly failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AggregateByStation on daily."
python.exe AggregateByStation.py --type daily --input ./daily --output ./output --municipalities ./settings/municipalities.json
if(-not $?){throw "AggregateByStation failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning DedupeValues on daily."
python.exe DedupeValues.py --type daily --path ./output
if(-not $?){throw "DedupeValues failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AggregateByCount on daily."
python.exe AggregateByCount.py --type daily --path ./output --settings ./settings
if(-not $?){throw "AggregateByCount failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AggregateByStation on hourly."
python.exe AggregateByStation.py --type hourly --input ./hourly --output ./output --municipalities ./settings/municipalities.json
if(-not $?){throw "AggregateByStation failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning DedupeValues on hourly."
python.exe DedupeValues.py --type hourly --path ./output
if(-not $?){throw "DedupeValues failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AggregateByCount on hourly."
python.exe AggregateByCount.py --type hourly --path ./output --settings ./settings
if(-not $?){throw "AggregateByCount failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AggregateByMean."
python.exe AggregateByMean.py --path ./output --outputfile yearlymean.json
if(-not $?){throw "AggregateByMean failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AddMetalsToYearly."
python.exe AddMetalsToYearly.py --path ./output --inputfile yearlymean.json --metals .\metaller2.csv --outputfile yearlymetal.json
if(-not $?){throw "AddMetalsToYearly failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AddYearlyThresholdsToYearly."
python.exe AddYearlyThresholdsToYearly.py --path ./output --inputfile yearlymetal.json --outputfile yearlyWithYearlyThreshold.json --settings ./settings
if(-not $?){throw "AddYearlyThresholdsToYearly failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AddThresholdsToYearly on daily."
python.exe AddThresholdsToYearly.py --path ./output --inputfile yearlyWithYearlyThreshold.json --outputfile yearlyWithDailyThreshold.json --settings ./settings --type daily
if(-not $?){throw "AddThresholdsToYearly daily failed with exit code: $LastExitCode"}

Write-Host -ForegroundColor Green "`r`nRunning AddThresholdsToYearly on hourly."
python.exe AddThresholdsToYearly.py --path ./output --inputfile yearlyWithDailyThreshold.json --outputfile yearly.json  --settings ./settings --type hourly
if(-not $?){throw "AddThresholdsToYearly hourly failed with exit code: $LastExitCode"}

# Remove all temporary files
Get-ChildItem -Recurse ./output | Where-Object {(-not ($_ -is [System.IO.DirectoryInfo])) -and $_.Name -ne "yearly.json"} | Remove-Item
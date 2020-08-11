
python.exe AggregateByStation.py --type daily --input ./daily --output ./output --municipalities ./settings/municipalities.json
if(-not $?){throw "AggregateByStation failed with exit code: $LastExitCode"}

python.exe DedupeValues.py --type daily --path ./output
if(-not $?){throw "DedupeValues failed with exit code: $LastExitCode"}

python.exe AggregateByCount.py --type daily --path ./output --settings ./settings
if(-not $?){throw "AggregateByCount failed with exit code: $LastExitCode"}

python.exe AggregateByStation.py --type hourly --input ./hourly --output ./output --municipalities ./settings/municipalities.json
if(-not $?){throw "AggregateByStation failed with exit code: $LastExitCode"}

python.exe DedupeValues.py --type hourly --path ./output
if(-not $?){throw "DedupeValues failed with exit code: $LastExitCode"}

python.exe AggregateByCount.py --type hourly --path ./output --settings ./settings
if(-not $?){throw "AggregateByCount failed with exit code: $LastExitCode"}

python.exe AggregateByMean.py --path ./output --outputfile yearlymean.json
if(-not $?){throw "AggregateByMean failed with exit code: $LastExitCode"}

python.exe AddMetalsToYearly.py --path ./output --inputfile yearlymean.json --metals .\metaller2.csv --outputfile yearlymetal.json
if(-not $?){throw "AddMetalsToYearly failed with exit code: $LastExitCode"}

python.exe AddYearlyThresholdsToYearly.py --path ./output --inputfile yearlymetal.json --outputfile yearlyWithYearlyThreshold.json --settings ./settings
if(-not $?){throw "AddThresholdsToYearly failed with exit code: $LastExitCode"}

python.exe AddThresholdsToYearly.py --path ./output --inputfile yearlyWithYearlyThreshold.json --outputfile yearlyWithDailyThreshold.json --settings ./settings --type daily
if(-not $?){throw "AddThresholdsToYearly failed with exit code: $LastExitCode"}

python.exe AddThresholdsToYearly.py --path ./output --inputfile yearlyWithDailyThreshold.json --outputfile yearly.json  --settings ./settings --type hourly
if(-not $?){throw "AddThresholdsToYearly failed with exit code: $LastExitCode"}
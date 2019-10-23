
python.exe AggregateByStation.py --type daily --input ./daily --output ./output --municipalities ./settings/municipalities.json
python.exe AggregateByCount.py --type daily --path ./output --settings ./settings

python.exe AggregateByStation.py --type hourly --input ./obs --output ./output --municipalities ./settings/municipalities.json
python.exe AggregateByCount.py --type hourly --path ./output --settings ./settings

python.exe AggregateByMean.py --path ./output

import json

data = []
current_airport = []
sorted_airport = []
with open('results/result.json') as file:
    data = json.load(file)
    data = data['data']

with open('airport.json') as file:
    a = json.load(file)
    current_airport = a['data']

airports_iata = [airport["iata_code"] for airport in current_airport]
for destination in data:
    if destination['from'] in airports_iata:
        if destination['from'] not in sorted_airport:
            sorted_airport.append(destination['from'])

new_airports = [airport for airport in current_airport if airport['iata_code'] in sorted_airport]

with open('new_airports.json','w',encoding="utf-8") as outfile:
    json.dump(new_airports,outfile, ensure_ascii=False, indent=4)
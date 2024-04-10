import pandas as pd
import numpy as np
import json
from selenium import webdriver
import re
import os
import time



def mean(l: list) -> float:
    return sum(l) / len(l)

def getAirportsListJson(path) -> None:
    airports_dataframe = pd.read_csv('airport-codes_csv.csv')
    airports = airports_dataframe[['name', 'type', 'iso_country', 'iata_code']]

    airports = airports.dropna()
    airport_dummies = pd.get_dummies(airports, columns=['type'])
    airport_dummies = airport_dummies.replace(False, np.nan)
    df5 = airport_dummies.dropna(subset=['type_large_airport'])
    df6 = df5[['name', 'iso_country', 'iata_code']]
    with open(path, 'w', encoding='utf-8') as file:
        df6.to_json(file, orient='records', lines=True, force_ascii=False)


def transformIntoJson(path) -> None:
    json_data_string = "{\"data\":["
    with open('temp.json', 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if i != len(lines) - 1:
                json_data_string += line + ","
            else:
                json_data_string += line
    json_data_string += "]}"
    j = json.loads(json_data_string)

    with open(path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(j, indent=4, ensure_ascii=False))

def getAirportsList(path) -> list:
    f = open(path, encoding="utf-8")
    data = json.load(f)
    return [airport['iata_code'] for airport in data['data']]

def getWebSiteInfo(airport: str):
    infos_list = []

    try:
        driver = webdriver.Chrome()
        driver.get('https://www.flightsfrom.com/' + airport)

        driver.find_element('xpath', '/html/body/div[9]/div[2]/div[1]/div[2]/div[2]/button[1]').click()
        try:
            driver.find_element('xpath', '//*[@id="vue-app"]/section/div/div[2]/div[1]/div[8]/div[1]/div').click()
        except:
            pass

        ul_element = driver.find_element('xpath', '//*[@id="vue-app"]/section/div/div[2]/div[1]/div[8]/ul')
        li_element = ul_element.find_elements('xpath', './/li[@class="ff-li-list"]')

        for li in li_element:
            try:
                destination_element = li.find_element('xpath', './/div/div[1]').text.split(" ")
                flights_infos = li.find_element('xpath', './/div/div[5]')
                flight_duration = li.find_element('xpath', './/div/div[6]/span').text
                flight_per_day_element = flights_infos.find_element('xpath', './div/div[3]')
                flight_days_element = flights_infos.find_element('xpath', './div/div[1]/div[1]')
                flight_operating_day = flight_days_element.find_elements('xpath', './div[@class="flightsfrom-list-days"]')
                flight_per_day = mean(
                    list(map(int, re.sub('[^0123456789\-]', '', flight_per_day_element.text).strip().split('-'))))
                flight_days = [let.text for let in flight_operating_day]
                infos_list.append({
                    'from': airport,
                    'to': destination_element[0],
                    'city': ' '.join(destination_element[1:]).split("\n")[0],
                    'flights_per_day': flight_per_day,
                    'flight_days': flight_days,
                    'flight_duration': flight_duration
                })
            except:
                pass
        driver.close()
    except:
        print(f'ERROR - {airport}')
    return infos_list


def main():
    start = time.time()
    subdirectory = "results"
    airports_list = getAirportsList("airport.json")
    for i in range(486,1619):
        data_list = []
        for airport in airports_list[i * 8:(i + 1) * 8]:
            data_list += getWebSiteInfo(airport)
        file = 'result' + str(i) + '.json'
        path = os.path.join(subdirectory, file)
        json_format = {'data': data_list}
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(json_format, file, ensure_ascii=False, indent=4)
    end = time.time()
    print(f'Programmed finished in : {end - start}')

if __name__ == "__main__":
    main()
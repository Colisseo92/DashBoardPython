from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from flask_cors import CORS
import re


app = Flask(__name__)
CORS(app)

def getFlightDistance(text: str):
    text_list = text.replace('\u00b7','').replace('miles','').replace('km','').replace('(','').replace(')','').split(" ")
    text_list2 = [int(a) for a in text_list if a != ""]
    return text_list2
def getWebSiteInfo(airport: str, destination: str):
    infos_list = {}

    infos_list['from'] = airport
    infos_list['to'] = destination

    infos_list['max_price'] = -1
    infos_list['interval'] = -1
    infos_list['mean_price'] = -1
    infos_list['prices'] = []

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = Options()
    options.add_argument("--headless=new")  # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-gpu')  # applicable to windows os only
    options.add_argument('start-maximized')  #
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    driver.get('https://www.flightsfrom.com/' + airport + "-" + destination)

    driver.find_element('xpath', '/html/body/div[10]/div[2]/div[1]/div[2]/div[2]/button[1]').click()

    distance = driver.find_element('xpath', '/html/body/div[5]/div/div[1]/div/div[4]/div[1]/div/div[2]').text
    treated_distance = getFlightDistance(distance)
    infos_list['distance_mile'] = treated_distance[0]
    infos_list['distance_km'] = treated_distance[1]
    flight_time = driver.find_element('xpath', '/html/body/div[5]/div/div[1]/div/div[4]/div[3]/div/div[2]').text
    infos_list['flight_time'] = flight_time.strip()
    price_div = driver.find_element('xpath', '/html/body/div[5]/div/div[1]/div')
    divs = price_div.find_elements(By.TAG_NAME,'div')
    prices = []
    for div in divs:
        if "price statistics" in div.text.lower():
            print(div.text)
            p = re.compile('\$?\d{2,15}|N/A')
            prices = p.findall(div.text)
            num_prices = [int(t.replace('$','').replace('N/A','0')) for t in prices]
            m = max(num_prices)
            print(m)
            infos_list['max_price'] = (int(str(max(num_prices))[0:(len(str(m))-2)])+1)*100
            infos_list['interval'] = int(infos_list['max_price']/10)
            infos_list['mean_price'] = num_prices[0]
            infos_list['prices'] = num_prices[1:]

    driver.close()

    return infos_list


@app.route("/")
def home():
    return "home"


@app.route("/travel-infos")
def infos():
    fr = request.args.get("from")
    to = request.args.get("to")
    returned = getWebSiteInfo(fr,to)
    print(returned)
    return jsonify([returned]), 200


if __name__ == "__main__":
    app.run(debug=True,port=8081)

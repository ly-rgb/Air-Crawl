import json
import pandas as pd


def task_generate(filename: str):
    df = pd.read_json(filename)
    cache = dict()
    for price_info in df['price_info']:
        price_info = json.loads(price_info)
        for flight in price_info['result']:
            flight_info = price_info['result'][flight]
            depAirport = flight_info['fromFlights'][0]['depAirport']
            arrAirport = flight_info['fromFlights'][-1]['arrAirport']
            depDate = flight_info['fromFlights'][0]['depDate']
            flightNo = flight
            cache_key = "".join([depAirport, arrAirport, flightNo])
            if cache_key not in cache:
                cache[cache_key] = 1
            else:
                cache[cache_key] += 1
            if cache[cache_key] <= 7:
                yield ",".join([depAirport, arrAirport, depDate, flightNo])
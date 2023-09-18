a = {'data': 'AE1261', 'productClass': 'ECONOMIC', 'fromSegments': [
    {'carrier': 'AE', 'flightNumber': 'AE1261', 'depAirport': 'TSA',
     'depTime': '2023470735', 'arrAirport': 'KNH', 'arrTime': '2023470855',
     'codeshare': False, 'cabin': 'Y', 'num': 0, 'aircraftCode': '',
     'segmentType': 0}], 'cur': 'TWD', 'adultPrice': '2641', 'adultTax': 0,
     'childPrice': 0, 'childTax': 0, 'promoPrice': 0, 'adultTaxType': 0,
     'childTaxType': 0, 'priceType': 0, 'applyType': 0, 'max': 1,
     'limitPrice': True, 'info': ''}, {'data': 'AE1269',
                                       'productClass': 'ECONOMIC',
                                       'fromSegments': [{'carrier': 'AE',
                                                         'flightNumber':
                                                             'AE1269',
                                                         'depAirport': 'TSA',
                                                         'depTime':
                                                             '2023471035',
                                                         'arrAirport': 'KNH',
                                                         'arrTime':
                                                             '2023471155',
                                                         'codeshare': False,
                                                         'cabin': 'Y', 'num': 0,
                                                         'aircraftCode': '',
                                                         'segmentType': 0}],
                                       'cur': 'TWD', 'adultPrice': '2641',
                                       'adultTax': 0, 'childPrice': 0,
                                       'childTax': 0, 'promoPrice': 0,
                                       'adultTaxType': 0, 'childTaxType': 0,
                                       'priceType': 0, 'applyType': 0, 'max': 1,
                                       'limitPrice': True, 'info': ''}, {
        'data': 'AE1277', 'productClass': 'ECONOMIC', 'fromSegments': [
        {'carrier': 'AE', 'flightNumber': 'AE1277', 'depAirport': 'TSA',
         'depTime': '2023471645', 'arrAirport': 'KNH', 'arrTime': '2023471805',
         'codeshare': False, 'cabin': 'Y', 'num': 0, 'aircraftCode': '',
         'segmentType': 0}], 'cur': 'TWD', 'adultPrice': '2641', 'adultTax': 0,
        'childPrice': 0, 'childTax': 0, 'promoPrice': 0, 'adultTaxType': 0,
        'childTaxType': 0, 'priceType': 0, 'applyType': 0, 'max': 1,
        'limitPrice': True, 'info': ''}
print(type(dict(a)))
b = a.json()
print(b)

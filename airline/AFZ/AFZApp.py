import time
import random
from datetime import datetime

from robot import HoldTask
from airline.baggage import Baggage
from utils.log import robot_FZ_logger
from airline.base import AirAgentV3Development
from concurrent.futures import ThreadPoolExecutor
from airline.AFZ.cookies_pool import cookies_pool


class AFZApp(AirAgentV3Development):

    def __init__(self, proxies_type=0, retry_count=10, timeout=120):
        super().__init__(proxies_type, retry_count, timeout,
                         logger=robot_FZ_logger)

    @staticmethod
    def get_headers():
        #cookie = cookies_pool.get(random.randint(0, 4))
        # headers = {
        #     'cookie': cookie,
        #     'origin': 'https://flights2.flydubai.com',
        #     'pragma': 'no-cache',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        #                   'AppleWebKit/537.36 (KHTML, like Gecko) '
        #                   'Chrome/108.0.0.0 Safari/537.36',
        # }
        headers = {
            'authority': 'flights2.flydubai.com',
            'method': 'POST',
            'path': '/api/flights/1',
            'scheme': 'https',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'appid': 'DESKTOP',
            'cache-control': 'no-cache',
            'content-length': '298',
            'content-type': 'application/json',
            'cookie': '_abck=28B50299BE4128CD6923A298C2997632~0~YAAQJtfSFwVoomeFAQAAK5UFigm0P6nKHEsj114qnKE5RGQTxknWx7VWP65e/ploPfIiDdqGgEYG6S27EKJmT6ktlLleUMYRKuZx1vrp7LBe80eSPD+HPuJjbjXyQhAxfiQleiLx1RukzyGE15AOIPKrSL2Kb9b18orv6/Oz7yTbRL/yn4eqIMfPpMV2kE3zgwW+QMLCJxEC7t72OqpYkurVa9m/9LcLXV88uQ7u2NOIsUCEGmzNstj4MBz3+ssIbGuk10ydmR8/IfhgLphx6szU7OvThZ2r6yEC6UUkFwZ3+54dCB0Qvl9zW8ZyOT6S2lWUyDlbWDbW4YLLow+PntSe9JdAKeM8UV79I72ecsMOb9dUEDqmb00QTNG0QHd0zVMi5J56pB+4A9COd3F2Am0H/Bhsg5Q0hOI=~-1~||-1||~-1',
            'origin': 'https://flights2.flydubai.com',
            'pragma': 'no-cache',
            # 'referer': 'https://flights2.flydubai.com/en/results/ow/a1
            # /AHB_DXB/20230108?cabinClass=Economy&isOriginMetro=false
            # &isDestMetro=true&pm=cash',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }
        return headers

    # def get_home(self):
    #     url = 'https://www.flydubai.com/en/'
    #     headers = {
    #         'authority': 'www.flydubai.com',
    #         'method': 'GET',
    #         'path': '/en/',
    #         'scheme': 'https',
    #         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
    #                   'image/avif,image/webp,image/apng,*/*;q=0.8,'
    #                   'application/signed-exchange;v=b3;q=0.9',
    #         'accept-encoding': 'gzip, deflate, br',
    #         'accept-language': 'zh-CN,zh;q=0.9',
    #         'cache-control': 'no-cache',
    #         'cookie': '_gcl_au=1.1.275543187.1671615560; '
    #                   'bd4tPrivacy=%7B%22level%22%3A%22on%22%2C%22consented'
    #                   '%22%3A%22false%22%7D; '
    #                   'bd4ti=TJ6TEf3IPqy_.1671615562588; '
    #                   'osano_consentmanager_uuid=94e8ac1b-359d-4471-a4ce'
    #                   '-4d0becfdd559; '
    #                   'osano_consentmanager=Z5hTy05eO5OtRH1vXgNuz6pVVW6bj7jEQ'
    #                   '-g9xrdkB7ZujpqyRXFWNhY65GW9fWmwMGd7clwvuz5fOVCzPKmDbRqD8WhJBOnr2_vkqYRphTUUlszDOm3pFti1ZEB9_qhqewspadgRdo4Xi8pvBBJEGRGW0H7n1Vvaq2adPuWcwjgt5GYaAtLlHDlwaePZBg4p-_2Od1PTJEbb45ns1o0dxfN9T86AE7lvShl_PppnDzD-Nu6eGMYAXkB0-AOzCWTqdQR9RBF71kK0fqOA_7gD2mKtda0vagyTaQv_iw==; _ga_YD03RQ1JRG=GS1.1.1671615560.1.0.1671615560.60.0.0; _ga_YD03RQ1JRG=GS1.1.1671615560.1.0.1671615560.60.0.0; _ga=GA1.1.222027289.1671615561; _ga=GA1.1.222027289.1671615561; scarab.visitor=%224AA5760BA5E474EE%22; _ym_uid=1671615567171480176; _ym_d=1671615567; checkBookingSwap=true; mcfChannels=(direct); mcfSourceDetails=(direct); mcfDates=2023016; mcfLastInteraction=(direct) | (direct); mcfFirstInteraction=(direct) | (direct); _gid=GA1.2.312255465.1672977480; _ym_isad=2; PSCS=Search|AHB|DXB|OW|01/07/2023 12:00 AM||2023-1-6; AKA_A2=A; bm_sz=26B1172A092CC8BA10ABAB6E0A855A53~YAAQRHItF18/zCmFAQAAfK58hhJ1xSWKskIDY0RyrOSIvXmW0oknjgju4tvNdEZIIrGvH5YiMaV+P+HL1ICeHvvA8xEAjsic//pIU5H25zddV9vpDqtDvLLDkGyBGJa54GmwDMhgIbLP3fv4Y4wsi5IJE5QpemOqOQt2oeu9nv97Sv3hu864reIyqThX35P+xtdiFUgQdsePh/6ridUJQhTYMXV9gxxjjxO8VUKs8niXfIcrHjYyEqaBK+FGTS5NEPC4gI/YJ2DjHC+Ea8YzG+VSKCFkirD0acrdBcWSreiEr42aEg==~4536642~4273717; language=8; CMS-WEB-SSL=ffffffff09671f6645525d5f4f58455e445a4a423660; bm_mi=E3CB7DBD7AA2E97AA33D5B3193CCE6BA~YAAQRHItF/A/zCmFAQAAVLZ8hhLM6kpPoTQqckSgz1LpQqI6pDd92UJdNgPWNHIQIjglA3n92JYf5YEHCsOJ+QdqshwBLKSs7NGlIEtZoQu3LkPsNnrvKVLSsGLYBHtwLtg9DJFvkz2+PE5QGBSt5N7xxTFtf6X9UxpZCpuEqpArbAORw4mYPAO6ufjtcq3xhIQN+oLN9hLTiUq8PFGxmcH3qc4F1/0K149+mR3rNYzcTCZGompKb2wxP46MQB75Dlnf0gNkJ/FZgriuaxRvcx2yB6eG6vZFbk7zKFUYjiAQ/M9izfLm42CbMkgzGowtkTmZNTzmqKuLHdpAMpEWTuFej9nzoZ0hq/zHuxO3m1p2~1; ak_bmsc=07B3A32801FC3C79AAF14609249932F9~000000000000000000000000000000~YAAQRHItF1NAzCmFAQAAn7x8hhJ80QqC5bxIgEjJ+RwHxJfXGS6gE8qmfC7womwvWMROTmL6+e8ehtwhKZ+IfxJCKnXR519ATBcyZzi0BS41YvJe1+noXhmjarRnq+roL7koGGoEwTpyzeBu0INt6QD2jGvVDGl+hzl5SyJwXQ9MXCuzZW/Fqk2UgEhp7CvZ7SN0AHTtPg+/oT4oYXmb/9Mp+JeVj7s35Wm6XtWoXJUr6NPH/Q2QKg7tS4e+fxdtbAeCR9kh/wTXixxQvV6Jm45RW+PvEPBSP8Y6hDazrzr26QmksF9Hmogmwz3qPg5Vv+91Vw0WeBGd8JDTGyJezhwnUb9fpquOPPEBmbGZdlWS4OG29JTzWbsUEJPnL2I1D/2WCBndOqnSGWmjv7k5pOlObXymRkVqZytpJwDDcd3n5uYDdchOcru9i/3HZoNah6RQ2hvIXACU3CcdcDJBifMDYCTTEVqBnDhx35aNxfvSx7QslCELMMCaLprAP08gXAxZwc2t+RfhEt8wnnObXl/SxsFvDMF3XO3gbZ6qRP3UM+pE; MC_landing=1; _ga_YD03RQ1JRG=GS1.1.1672998923.2.1.1672998925.58.0.0; searchObject=eyJpc1JlZnJlcnIiOmZhbHNlLCJjYWJpbkNsYXNzIjoiRWNvbm9teSIsInBtIjoiY2FzaCIsInByb21vQ29kZSI6IiIsImpvdXJuZXlUeXBlIjoib3ciLCJsYW5ndWFnZSI6ImVuIiwiaXNEZXN0TWV0cm8iOnRydWUsImlzT3JpZ2luTWV0cm8iOmZhbHNlLCJyZWZyZXNoVHlwZSI6MSwicGF4SW5mbyI6eyJhZHVsdENvdW50IjoxLCJjaGlsZENvdW50IjowLCJpbmZhbnRDb3VudCI6MCwidG90YWxQYXhDb3VudCI6MX0sImxvYWRKb3VybmV5U2VnbWVudCI6dHJ1ZSwic2VhcmNoQ3JpdGVyaWEiOlt7ImRhdGUiOiIwMS8wNy8yMDIzIDEyOjAwIEFNIiwiZGVzdCI6IkRYQiIsIm9yaWdpbiI6IkFIQiIsImRpcmVjdGlvbiI6Im91dEJvdW5kIiwiaW5pdGlhbENhbGVuZGFyRGF0ZSI6IjAxLzA3LzIwMjMgMTI6MDAgQU0iLCJpc09yaWdpbk1ldHJvIjpmYWxzZSwiaXNEZXN0TWV0cm8iOnRydWUsIm9yaWdpbkNpdHkiOiIiLCJvcmlnaW5EZXNjIjoiIiwiZGVzdERlc2MiOiIiLCJkZXN0Q2l0eSI6IiJ9XX0=; _abck=6C11E2A68E83E63BC49CF99AEF91F32B~0~YAAQjfw7F1LFrH6FAQAAttyBhgnA9WDiIcjmt4eX1rUqi0aGzICuWkFId4h60WmVUr49iTIHEnfRnuphw8+ubgXCBEEOuh8MLNrZWZL4y2/ZF+t8XMXjToM/j9sAhXoBRuNYfhYUOLV4AYVMV0+WHW1bFRIZkIqncS4RNL4qfhcIwbpuyx2F3pOUuHNZDJnb0W1hHZ9X1P7XpvsBO/RpOUTdUa5K7SyC2t4n4HEfK1JEThZqg03L6tEwR3/bww2YpsiVPnvo9VTVDPQ2pqZY/NGQ/NMISnm7Z1kxyDiz7oS/dsQ0l4uIAacYHSfWHn6IU9MHmoYozh7IXWWuA2U9UqgtPrVwiV0akz31/G1M4LxUTY+cgNGMVUySNyFWwOQhBmC/3M+84bhyFb14YoXrfCpUttJ0TFHPiCE=~-1~-1~-1; _ga=GA1.2.222027289.1671615561; bm_sv=FB1DAE134F6F1BA15AB817344A9370BF~YAAQjfw7F9vFrH6FAQAA6vmBhhJuOw0YhNahoWHKcfEhnI1RDMfZI0azmLdnY5T62AiBVzxvQNthlRgfBf0XjIFzinjawok/iP5fNqf/gwen3zM8IVIUNzl42bOlJHx5BkfzZqUoQ8OEcp5PRWt+THM9ukynshBfGKvPXjQ7wxFN8ow+DPjnTW39pnznoFYXb9mFM+6faCQM75DPHxva5xc7Y7rRWJdejB59c9YVrzr0+xQsS48HhEecl+PVRPVJqF8D~1; _dc_gtm_UA-7803913-7=1; RT="sl=4&ss=1672998595821&tt=28647&obo=0&sh=1672998931611%3D4%3A0%3A28647%2C1672998908030%3D3%3A0%3A19806%2C1672998623896%3D2%3A0%3A14817%2C1672998599789%3D1%3A0%3A3961&dm=flydubai.com&si=746ca2f5-89ce-454b-b615-b3ee61ce8ee5&rl=1&ld=1672998931612&nu=&cl=1672999467714&r=https%3A%2F%2Fflights2.flydubai.com%2Fen%2Fresults%2Fow%2Fa1%2FAHB_DXB%2F20230107%3F79c972e35ea675971403bbe4d42b7e6b&ul=1672999467826"',
    #         'pragma': 'no-cache',
    #         'referer': 'https://flights2.flydubai.com/',
    #         'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google '
    #                      'Chrome";v="108"',
    #         'sec-ch-ua-mobile': '?0',
    #         'sec-ch-ua-platform': '"Windows"',
    #         'sec-fetch-dest': 'document',
    #         'sec-fetch-mode': 'navigate',
    #         'sec-fetch-site': 'same-site',
    #         'sec-fetch-user': '?1',
    #         'upgrade-insecure-requests': '1',
    #         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    #                       'AppleWebKit/537.36 (KHTML, like Gecko) '
    #                       'Chrome/108.0.0.0 Safari/537.36',
    #     }
    #     resp = self.get(url=url, headers=headers)
    #     cookies = resp.cookies.get_dict()
    #     return cookies

    def bookingAvailability(self, holdTask: HoldTask):
        self.holdTask = holdTask
        self.currencyCode = "SAR"

        url = 'https://flights2.flydubai.com/api/flights/1'
        headers = self.get_headers()
        json = {
                "promoCode": "",
                "cabinClass": "Economy",
                "isDestMetro": True,
                "isOriginMetro": False,
                "paxInfo": {
                    "adultCount": 1,
                    "childCount": 0,
                    "infantCount": 0
                },
                "searchCriteria": [
                    {
                        "date": holdTask.departDate,
                        "dest": holdTask.destination,
                        "direction": "outBound",
                        "origin": holdTask.origin,
                        "isOriginMetro": True,
                        "isDestMetro": False
                    }
                ],
                "variant": "1"
            }
        resp = self.post(url=url, headers=headers, json=json)
        self.logger.info(f'抓数的响应状态码为{resp.status_code}')
        time.sleep(3.2)
        if resp.status_code >= 300:
            raise Exception(f"[resp] ==> {resp.status_code}")
        securitytoken = resp.headers['securitytoken']

        self.availability_result = resp.json()
        self.logger.info(f'抓到的所有结果为{self.availability_result}')
        self.currencyCode = resp.json()['segments'][0]['currencyCode']
        return securitytoken

    def convert_search(self):

        self.flights = {}
        result = []

        def func(journey):
            flight_no = []
            fromSegments = []
            for leg in journey['legs']:
                flightNumber = leg['flightNumber']
                flight_no.append(flightNumber)
                fromSegments.append({
                        "carrier": leg['operatingCarrier'],
                        "flightNumber": flightNumber,
                        "depAirport": leg['origin'],
                        "depTime": datetime.strptime(leg['departureDate'],
                                                     "%Y-%m-%dT%H:%M:%S").strftime(
                            "%Y%m%d%H%M"),
                        "arrAirport": leg['destination'],
                        "arrTime": datetime.strptime(leg['arrivalDate'],
                                                     "%Y-%m-%dT%H:%M:%S").strftime(
                            "%Y%m%d%H%M"),
                        "codeshare": False,
                        "cabin": "Y",
                        "num": 0,
                        "aircraftCode": "",
                        "segmentType": 0
                    })
            self.flights["/".join(flight_no)] = journey

            item = {
                'data': '/'.join(flight_no),
                'productClass': 'ECONOMIC',
                'fromSegments': fromSegments,
                'cur': self.currencyCode,
                'adultPrice': journey['fareTypes'][0]['fare']['totalFare'],
                'adultTax': 0,
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': journey['fareTypes'][0]['seatsLeft'],
                'limitPrice': True,
                'info': ''
            }
            result.append(item)

        ths = ThreadPoolExecutor(max_workers=10)
        list(ths.map(func,
                     self.availability_result["segments"][0]["flights"]))
        self.logger.info(f'抓到的所有航班为{result}')
        return result

    def selectFlight(self, holdTask: HoldTask):
        self.flight = self.flights.get(holdTask.flightNumber, None)
        if not self.flight:
            raise Exception(
                f"未找到航班: {holdTask.flightNumber}, 当前航班: {self.flights}")

    def get_addflight(self, securitytoken):
        url = 'https://flights2.flydubai.com/api/itinerary/AddFlight'
        headers = {
            'appID': 'DESKTOP',
            'Referer': 'https://flights2.flydubai.com/en/results/ow/a1/'+self.flight['origin']+'_'+self.flight['dest']+'/'+self.flight['departureTime'].split('T')[0]+'?cabinClass=Economy&isOriginMetro=false&isDestMetro=true&pm=cash',
            'securitytoken': securitytoken,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/108.0.0.0 Safari/537.36'
        }
        self.flight['selectedFare'] = self.flight["fareTypes"][0]
        json = {
            "passengerList": [],
            "preferences": {
                "isReadyToSignUpForOffers": False,
                "acceptForSocialMediaUpdates": False
            },
            "searchRequest": {
                "isRefrerr": False,
                "cabinClass": "Economy",
                "pm": "cash",
                "promoCode": "",
                "journeyType": "ow",
                "language": "en",
                "isDestMetro": True,
                "isOriginMetro": False,
                "refreshType": 1,
                "paxInfo": {
                    "adultCount": 1,
                    "childCount": 0,
                    "infantCount": 0,
                    "totalPaxCount": 1
                },
                "loadJourneySegment": True,
                "searchCriteria": [
                    {
                        "date": self.flight['departureTime'],
                        "dest": self.flight['dest'],
                        "origin": self.flight['origin'],
                        "direction": "outBound",
                        "initialCalendarDate": self.flight['departureTime'],
                        "isOriginMetro": False,
                        "isDestMetro": True
                    }
                ]
            },
            "selectedFlights": [
                self.flight
            ],
            "selectedinsuranceQuotes": None,
            "itineraryAction": "1",
            "connectingODs": [],
            "displayMode": "CASH",
            "displayCurrency": "",
            "repricingKey": None
        }
        self.post(url=url, headers=headers, json=json)

    def get_bag_list(self, securitytoken):
        url = 'https://flights2.flydubai.com/api/optionalExtras'
        headers = {
            'appID': 'DESKTOP',
            'Referer': 'https://flights2.flydubai.com/en/results/ow/a1/' +
                       self.flight['origin'] + '_' + self.flight['dest'] + '/' +
                       self.flight['departureTime'].split('T')[
                           0] + '?cabinClass=Economy&isOriginMetro=false&isDestMetro=true&pm=cash',
            'securitytoken': securitytoken,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 '
                          'Safari/537.36'
        }
        json = {
  "selectedFlights": [
      self.flight
  ],
  "searchRequest": {
    "promoCode": "",
    "cabinClass": "economy",
    "journeyType": "ow",
    "isOriginMetro": False,
    "isDestMetro": True,
    "searchCriteria": [
      {
        "origin": self.flight['origin'],
        "dest": self.flight['dest'],
        "originMetroGroup": None,
        "destMetroGroup": None,
        "direction": "outBound",
        "date": self.flight['departureTime'],
        "isOriginMetro": False,
        "isDestMetro": True
      }
    ],
    "paxInfo": {
      "adultCount": 1,
      "infantCount": 0,
      "childCount": 0
    }
  },
  "passengerList": [
    {
      "passengerId": "-1",
      "passengerType": "Adult",
      "title": None,
      "firstName": "abcd",
      "middleName": "",
      "lastName": "xyz",
      "dob": None,
      "isPrimaryPassenger": None,
      "emailAddress": None,
      "nationality": None,
      "documentNumber": None,
      "documentIssueDate": None,
      "documentExpiryDate": None,
      "passportIssuingCountry": None,
      "countryOfResidence": None,
      "contactMobileContryCode": None,
      "contactMobileNumber": None,
      "socialMediaMobileContryCode": None,
      "socialMediaMobileNumber": None,
      "contactMobileNumberField": None,
      "contactTelephoneContryCode": None,
      "contactTelephoneNumber": None,
      "contactTelephoneField": None,
      "accompanyingAdult": None,
      "memberId": None,
      "tierId": None,
      "tierName": None,
      "deleteEnabled": None,
      "isMinor": None,
      "ffpEnabled": None,
      "tierInfo": None
    }
  ]
}
        resp = self.post(url=url, headers=headers, json=json)
        bag_data = resp.json()['baggageQuotes'][0]['baggageInfo']
        bag_list = []
        for i in bag_data:
            weight = i['weight']
            price = i['amount']

            bag_list.append(
                Baggage(weight, price, self.flight, price, self.currencyCode))
        self.logger.info(f'获取到的bag_list为{bag_list}')
        return bag_list[1:]



import json
import re
from airline.base import AirAgentV3Development
from robot import HoldTask
from utils.searchparser import SearchParam
from utils.log import spider_FO_logger
import traceback
from datetime import datetime, timedelta


class AFOWeb(AirAgentV3Development):
    '''

    '''

    def __init__(self, proxies_type=0, retry_count=3, timeout=60, holdTask=None):
        super().__init__(proxies_type, retry_count, timeout)
        self.holdTask: HoldTask = holdTask
        self.search_response = None

    def search(self, searchParam: SearchParam):
        self.number = searchParam.adt
        try:
            start_date = searchParam.date
            if "CRAWlLCC" in searchParam.args:
                pass

            ticket_info_url = "https://flybondi.com/graphql"
            headers = {
                'Sec-Fetch-Mode': 'cors',
                'content-type': 'application/json',
                'accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate, br',
                'Host': 'flybondi.com',
                'Origin': 'https://flybondi.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
                'x-fo-flow': 'ibe',
                'x-fo-market-origin': 'ar',
                'x-fo-ui-version': '2.68.0'
            }
            data = {
                "query": "query FlightSearchContainerQuery(\n  $input: FlightsQueryInput!\n  $origin: String!\n  $destination: String!\n  $currency: String!\n  $start: Timestamp!\n  $end: Timestamp!\n) {\n  airports(onlyActive: false) {\n    code\n    location {\n      cityName\n    }\n    description\n  }\n  viewer {\n    ...withBookingLayout_viewer\n    ...useFlowRules_viewer\n    session {\n      id\n      user {\n        id\n        groups\n        name\n        givenName\n        familyName\n        email\n      }\n      customer {\n        nationalId\n        email\n        firstName\n        lastName\n        phoneNumber\n      }\n      fareTypeSelection\n    }\n    flights(input: $input) {\n      edges {\n        node {\n          id\n          lfId\n          origin\n          destination\n          direction\n          carrier\n          departureDate\n          arrivalDate\n          flightTimeMinutes\n          international\n          flightNo\n          segmentFlightNo\n          currency\n          stops\n          connections {\n            waitingTimeMinutes\n            connectingAirport\n            connectionType\n          }\n          legs {\n            arrivalDate\n            carrier\n            departureDate\n            destination\n            flightNo\n            flightTimeMinutes\n            id\n            origin\n          }\n          fares {\n            fareRef\n            passengerType\n            class\n            basis\n            type\n            availability\n            taxes {\n              taxRef\n              taxCode\n              codeType\n              amount\n              description\n            }\n            prices {\n              afterTax\n              beforeTax\n              promotionAmount\n            }\n          }\n        }\n      }\n      ...FlightSearchResults_flights\n    }\n    ...TravelTips_viewer\n    ...BasketBar_viewer\n    ...BookingDetails_viewer\n    id\n  }\n  departures: fares(origin: $origin, destination: $destination, currency: $currency, start: $start, end: $end, sort: \"departure\") {\n    id\n    departure\n    fares {\n      price\n      fCCode\n      fBCode\n      roundtrip\n      advancedDays\n      minDays\n      maxDays\n      hasRestrictions\n    }\n    lowestPrice\n  }\n  arrivals: fares(origin: $destination, destination: $origin, currency: $currency, start: $start, end: $end, sort: \"departure\") {\n    id\n    departure\n    fares {\n      price\n      fCCode\n      fBCode\n      roundtrip\n      advancedDays\n      minDays\n      maxDays\n      hasRestrictions\n    }\n    lowestPrice\n  }\n}\n\nfragment BasketBar_viewer on Viewer {\n  ...BookingDetails_viewer\n  session {\n    ...usePriceBreakdown_session\n    user {\n      groups\n      id\n    }\n    currency\n    isClubMember\n    flights {\n      outbound {\n        id\n        arrivalDate\n        destination\n        departureDate\n        flightNo\n        origin\n        fares {\n          passengerType\n          type\n          taxes {\n            amount\n            taxCode\n            taxRef\n          }\n          prices {\n            afterTax\n            beforeTax\n          }\n        }\n      }\n      inbound {\n        id\n        arrivalDate\n        destination\n        departureDate\n        flightNo\n        origin\n        fares {\n          passengerType\n          type\n          taxes {\n            amount\n            taxCode\n            taxRef\n          }\n          prices {\n            afterTax\n            beforeTax\n          }\n        }\n      }\n    }\n    pax {\n      adults\n      children\n      infants\n    }\n    passengers {\n      id\n      firstName\n      lastName\n      type\n      gender\n      nationality\n      documentType\n      nationalId\n      assistanceCodes\n      notifyMe\n      phoneType\n      phone\n      email\n      birthDate\n      isPrimary\n      ssrs {\n        id\n        code\n        ssrId\n        flightId\n        service\n        category\n        quantity\n        taxes {\n          amount\n          description\n          taxCode\n          taxRef\n        }\n        price {\n          beforeTax\n          afterTax\n        }\n      }\n      seats {\n        id\n        flightId\n        type\n        letter\n        row\n        amount\n        price {\n          beforeTax\n          afterTax\n        }\n        taxes {\n          amount\n          description\n          taxCode\n          taxRef\n        }\n        exit\n      }\n    }\n    fareTypeSelection\n    clubSSR {\n      id\n      code\n      ssrId\n      flightId\n      service\n      category\n      quantity\n      taxes {\n        amount\n        description\n      }\n      price {\n        beforeTax\n        afterTax\n      }\n    }\n    id\n  }\n}\n\nfragment BookingDetails_viewer on Viewer {\n  airports(onlyActive: false) {\n    code\n    metroGroup\n    location {\n      cityName\n    }\n  }\n  session {\n    ...usePriceBreakdown_session\n    user {\n      groups\n      id\n    }\n    customer {\n      pass {\n        code\n      }\n    }\n    isClubMember\n    discountAmount\n    discount {\n      __typename\n      type\n      amount\n      ... on PromoCode {\n        code\n      }\n    }\n    flights {\n      outbound {\n        arrivalDate\n        carrier\n        currency\n        departureDate\n        destination\n        fares {\n          availability\n          passengerType\n          prices {\n            afterTax\n            beforeTax\n            promotionAmount\n          }\n          taxes {\n            amount\n            taxCode\n            taxRef\n          }\n          type\n        }\n        flightTimeMinutes\n        id\n        connections {\n          waitingTimeMinutes\n          connectingAirport\n          connectionType\n        }\n        legs {\n          arrivalDate\n          carrier\n          departureDate\n          destination\n          flightNo\n          flightTimeMinutes\n          id\n          origin\n        }\n        origin\n        segmentFlightNo\n        stops\n      }\n      inbound {\n        arrivalDate\n        carrier\n        currency\n        departureDate\n        destination\n        fares {\n          availability\n          passengerType\n          prices {\n            afterTax\n            beforeTax\n            promotionAmount\n          }\n          taxes {\n            amount\n            taxCode\n            taxRef\n          }\n          type\n        }\n        flightTimeMinutes\n        id\n        connections {\n          waitingTimeMinutes\n          connectingAirport\n          connectionType\n        }\n        legs {\n          arrivalDate\n          carrier\n          departureDate\n          destination\n          flightNo\n          flightTimeMinutes\n          id\n          origin\n        }\n        origin\n        segmentFlightNo\n        stops\n      }\n    }\n    pax {\n      adults\n      children\n      infants\n    }\n    passengers {\n      id\n      firstName\n      lastName\n      type\n      gender\n      nationality\n      documentType\n      nationalId\n      assistanceCodes\n      notifyMe\n      phoneType\n      phone\n      email\n      birthDate\n      isPrimary\n      ssrs {\n        id\n        code\n        ssrId\n        flightId\n        service\n        category\n        quantity\n        taxes {\n          amount\n          description\n          taxCode\n          taxRef\n        }\n        price {\n          beforeTax\n          afterTax\n        }\n      }\n      seats {\n        id\n        flightId\n        type\n        letter\n        row\n        amount\n        price {\n          beforeTax\n          afterTax\n        }\n        taxes {\n          amount\n          description\n          taxCode\n          taxRef\n        }\n        exit\n      }\n    }\n    vouchers {\n      amount\n      number\n      id\n    }\n    fareTypeSelection\n    currency\n    clubSSR {\n      id\n      code\n      ssrId\n      flightId\n      service\n      category\n      quantity\n      taxes {\n        amount\n        description\n      }\n      price {\n        beforeTax\n        afterTax\n      }\n    }\n    id\n  }\n}\n\nfragment FlightItem_flight on FlightInfo {\n  id\n  arrivalDate\n  carrier\n  currency\n  departureDate\n  origin\n  destination\n  flightNo\n  segmentFlightNo\n  flightTimeMinutes\n  stops\n  connections {\n    waitingTimeMinutes\n    connectionType\n    connectingAirport\n  }\n  legs {\n    arrivalDate\n    carrier\n    departureDate\n    destination\n    flightNo\n    flightTimeMinutes\n    id\n    origin\n  }\n  fares {\n    availability\n    passengerType\n    prices {\n      afterTax\n      promotionAmount\n    }\n    type\n  }\n}\n\nfragment FlightList_flights on FlightInfoEdge {\n  node {\n    id\n    origin\n    destination\n    departureDate\n    arrivalDate\n    flightNo\n    international\n    fares {\n      fareRef\n      passengerType\n      class\n      basis\n      type\n      availability\n      taxes {\n        taxRef\n        taxCode\n        codeType\n        amount\n        description\n      }\n      prices {\n        afterTax\n        beforeTax\n        promotionAmount\n      }\n    }\n    ...FlightItem_flight\n  }\n}\n\nfragment FlightSearchResults_flights on FlightInfoConnection {\n  edges {\n    ...FlightList_flights\n    node {\n      origin\n      destination\n      direction\n      id\n    }\n  }\n}\n\nfragment MMBHeader_viewer on Viewer {\n  session {\n    mmb {\n      pnr\n      blockedReasonCode\n      reservation {\n        balance\n        flights {\n          origin\n          active\n          cancelled\n          destination\n          departureDate\n          direction\n          legs {\n            cancelled\n            id\n          }\n          id\n        }\n        id\n      }\n    }\n    id\n  }\n  configuration {\n    destinations {\n      code\n      name\n      mmb {\n        width\n        height\n        handle\n      }\n      id\n    }\n  }\n}\n\nfragment SearchHeader_viewer on Viewer {\n  allAirports: airports(onlyActive: false) {\n    code\n    location {\n      cityName\n    }\n    description\n    metroGroup\n  }\n  ...useFlowRules_viewer\n  ...StepperPanel_viewer\n  session {\n    currency\n    flights {\n      inbound {\n        id\n        departureDate\n      }\n      outbound {\n        id\n        destination\n        departureDate\n        origin\n      }\n    }\n    pax {\n      adults\n      children\n      infants\n    }\n    user {\n      name\n      id\n    }\n    discount {\n      __typename\n      type\n      amount\n      ... on PromoCode {\n        code\n      }\n    }\n    id\n  }\n}\n\nfragment StepperPanel_viewer on Viewer {\n  allAirports: airports(onlyActive: false) {\n    code\n    location {\n      cityName\n    }\n    description\n    metroGroup\n  }\n  ...useFlowRules_viewer\n  session {\n    currency\n    pax {\n      adults\n      children\n      infants\n    }\n    flights {\n      outbound {\n        id\n        origin\n        destination\n        departureDate\n        connections {\n          connectionType\n        }\n      }\n      inbound {\n        id\n        arrivalDate\n        connections {\n          connectionType\n        }\n      }\n    }\n    discount {\n      __typename\n      type\n      amount\n      ... on PromoCode {\n        code\n      }\n    }\n    id\n  }\n}\n\nfragment TravelTips_viewer on Viewer {\n  airports(onlyActive: false) {\n    code\n    metroGroup\n    location {\n      placeId\n      lat\n      lon\n    }\n    active\n  }\n  session {\n    flights {\n      outbound {\n        stops\n        id\n      }\n      inbound {\n        stops\n        id\n      }\n    }\n    mmb {\n      pnr\n      digest\n      reservation {\n        flights {\n          origin\n          legs {\n            waitingTimeMinutes\n            id\n          }\n          id\n        }\n        id\n      }\n    }\n    id\n  }\n}\n\nfragment useFlowRules_viewer on Viewer {\n  flowRules {\n    flow\n    maxPaxType {\n      adults\n      children\n      infants\n    }\n    canChooseExtras\n    canChooseSeats\n    canChangePaymentMethod\n    canUseVoucher\n    canUsePromoCode\n    canUseFlexibleDates\n    canViewPrices\n    canViewBookingSummary\n    canUseSearchBarTabs\n    canViewAgreementPaymentSummary\n    allowCashPaymentOption\n    allowVoucherPaymentOption\n    allowOneWay\n    allowSearchWithEmptyFields\n  }\n}\n\nfragment usePriceBreakdown_session on UserSession {\n  clubSSR {\n    price {\n      afterTax\n    }\n    id\n  }\n  discountAmount\n  discount {\n    __typename\n    type\n    amount\n    ... on PromoCode {\n      code\n    }\n    ... on ClubDiscount {\n      membership {\n        __typename\n        club\n        number\n      }\n    }\n  }\n  isClubMember\n  fareTypeSelection\n  currency\n  pax {\n    adults\n    children\n    infants\n  }\n  passengers {\n    id\n    ssrs {\n      id\n      code\n      ssrId\n      flightId\n      service\n      category\n      quantity\n      taxes {\n        amount\n        description\n        taxCode\n        taxRef\n      }\n      price {\n        beforeTax\n        afterTax\n      }\n    }\n    seats {\n      id\n      flightId\n      type\n      letter\n      row\n      amount\n      price {\n        beforeTax\n        afterTax\n      }\n      taxes {\n        amount\n        description\n        taxCode\n        taxRef\n      }\n      exit\n    }\n  }\n  vouchers {\n    amount\n    number\n    id\n  }\n  flights {\n    outbound {\n      id\n      carrier\n      flightNo\n      segmentFlightNo\n      departureDate\n      arrivalDate\n      origin\n      destination\n      international\n      currency\n      fares {\n        fareRef\n        passengerType\n        class\n        basis\n        availability\n        type\n        taxes {\n          taxRef\n          taxCode\n          codeType\n          amount\n          description\n        }\n        prices {\n          afterTax\n          beforeTax\n          promotionAmount\n        }\n      }\n    }\n    inbound {\n      id\n      carrier\n      flightNo\n      segmentFlightNo\n      departureDate\n      arrivalDate\n      origin\n      destination\n      international\n      currency\n      fares {\n        fareRef\n        passengerType\n        class\n        basis\n        availability\n        type\n        taxes {\n          taxRef\n          taxCode\n          codeType\n          amount\n          description\n        }\n        prices {\n          afterTax\n          beforeTax\n          promotionAmount\n        }\n      }\n    }\n  }\n}\n\nfragment withBookingLayout_viewer on Viewer {\n  ...MMBHeader_viewer\n  ...SearchHeader_viewer\n  ...useFlowRules_viewer\n  session {\n    id\n    currency\n    passengers {\n      id\n      firstName\n    }\n    flights {\n      inbound {\n        id\n        departureDate\n      }\n      outbound {\n        id\n        destination\n        departureDate\n        origin\n      }\n    }\n    pax {\n      adults\n      children\n      infants\n    }\n    user {\n      name\n      id\n    }\n  }\n}\n",
                "variables": {"input": {"origin": searchParam.dep, "destination": searchParam.arr,
                                        "departureDate": searchParam.date, "currency": "ARS",
                                        "pax": {"adults": searchParam.adt, "children": 0, "infants": 0}},
                              "origin": searchParam.dep, "destination": searchParam.arr, "currency": "ARS",
                              "start": 1664208000000, "end": 1727539199999}}
            ticket_info_res = self.post(url=ticket_info_url, headers=headers, data=json.dumps(data))
            # print(ticket_info_res.text)
            if ticket_info_res.status_code == 200:
                self.ticket_info = ticket_info_res.json()
            else:
                raise Exception('ticket_info获取失败..')


        except Exception as e:
            spider_FO_logger.error(f"请求失败, 失败结果：{e}")
            spider_FO_logger.error(f"{traceback.format_exc()}")

    def parse_info(self, edges):
        result = []
        for edge in edges:
            ep_data = {
                'data': '',
                'productClass': 'ECONOMIC',
                'fromSegments': [],
                'cur': 'ARS',
                'adultPrice': 999999,
                'adultTax': 1,
                'childPrice': 0,
                'childTax': 0,
                'promoPrice': 0,
                'adultTaxType': 0,
                'childTaxType': 0,
                'priceType': 0,
                'applyType': 0,
                'max': 0,
                'limitPrice': True,
                'info': ""
            }
            ep_data['cur'] = edge['node']['currency']
            ep_data['max'] = [fare['availability'] for fare in edge['node']['fares'] if fare['type'] == "STANDARD"][0]
            ep_data['adultPrice'] = [fare['prices']['afterTax']-1 for fare in edge['node']['fares'] if fare['type'] == "STANDARD"][0]
            cabin = [fare['class'] for fare in edge['node']['fares'] if fare['type'] == "STANDARD"][0]
            sgs = []
            for leg in edge['node']['legs']:
                sg = {
                    'carrier': '',
                    'flightNumber': '',
                    'depAirport': '',
                    'depTime': '',
                    'arrAirport': '',
                    'arrTime': '',
                    'codeshare': False,
                    'cabin': '',
                    'num': 0,
                    'aircraftCode': '',
                    'segmentType': 0
                }
                sg['carrier'] = leg['carrier']
                sg['flightNumber'] = leg['carrier'] + str(leg['flightNo'])
                sg['depAirport'] = leg['origin']
                sg['depTime'] = datetime.strptime(leg['departureDate'], "%Y-%m-%dT%H:%M:%S.000-03:00").strftime(
                    "%Y%m%d%H%M")
                sg['arrAirport'] = leg['destination']
                sg['arrTime'] = datetime.strptime(leg['arrivalDate'] , "%Y-%m-%dT%H:%M:%S.000-03:00").strftime(
                    "%Y%m%d%H%M")
                sg['cabin'] = cabin
                sgs.append(sg)
            ep_data['fromSegments'] = sgs
            ep_data['data'] = '/'.join([i['flightNumber'] for i in sgs])
            result.append(ep_data)
        return result

    def convert_search(self):

        try:
            if self.ticket_info.get('errors'):
                return []
            else:
                edges = self.ticket_info['data']['viewer']['flights']['edges']
                result = self.parse_info(edges)
                return result

        except Exception:
            spider_FO_logger.error("解析数据失败，请查看json结构")
            spider_FO_logger.error(f"{traceback.format_exc()}")

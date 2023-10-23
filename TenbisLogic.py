import requests
import urllib3
import json
import os
import pickle
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TENBIS_FQDN = "https://www.10bis.co.il"
CWD = os.getcwd()
DEBUG = True
DRYRUN = True


def print_hebrew(heb_txt):
    print(heb_txt[::-1])


COUPONS_IDS = {
    15: 6552646,
    30: 2046839,
    40: 2046840,
    50: 2046841,
    100: 2046845
}


def load_pickle(path):
    with open(path, 'rb') as session_file:
        obj = pickle.load(session_file)
        return obj


def create_pickle(obj, path):
    with open(path, 'wb') as session_file:
        pickle.dump(obj, session_file)


class Tenbis:
    SESSION_PATH = f"{CWD}/sessions.pickle"
    TOKEN_PATH = f"{CWD}/usertoken.pickle"

    def __init__(self):
        self.cart_guid = None
        self.user_id = None
        self.email = None
        if os.path.exists(self.SESSION_PATH) and os.path.exists(self.TOKEN_PATH):
            self.session = load_pickle(self.SESSION_PATH)
            self.user_token = load_pickle(self.TOKEN_PATH)
            return
        if not self.auth():
            raise Exception('Error Authenticating')

    def post_next_api(self, endpoint, payload, include_user_token_on_header=True):
        endpoint = TENBIS_FQDN + "/NextApi/" + endpoint
        headers = {"content-type": "application/json"}
        if include_user_token_on_header:
            headers['user-token'] = self.user_token
        response = self.session.post(endpoint, data=json.dumps(payload), headers=headers)
        resp_json = json.loads(response.text)
        error_msg = resp_json['Errors']
        success_code = resp_json['Success']
        if DEBUG:
            print("Request:" + endpoint + "\nHeaders:" + json.dumps(headers) + "\n" +
                  "Request Payload:" + json.dumps(payload))
            print("Response: " + str(response.status_code))
            print(resp_json)
        if not success_code:
            raise Exception('NextApi call failure:' + (error_msg[0]['ErrorDesc'][::-1]))

        return resp_json

    def auth(self):
        # Phase one -> Email
        self.email = input("Enter Email: ")
        payload = {"culture": "he-IL", "uiCulture": "he", "email": self.email}
        self.session = requests.session()
        resp_json = self.post_next_api('GetUserAuthenticationDataAndSendAuthenticationCodeToUser', payload, False)

        # Phase two -> OTP
        auth_token = resp_json['Data']['codeAuthenticationData']['authenticationToken']
        shop_cart_guid = resp_json['ShoppingCartGuid']
        otp = input("Enter OTP: ")
        payload = {"shoppingCartGuid": shop_cart_guid,
                   "culture": "he-IL",
                   "uiCulture": "he",
                   "email": self.email,
                   "authenticationToken": auth_token,
                   "authenticationCode": otp}

        resp_json = self.post_next_api('GetUserV2', payload, False)
        user_token = resp_json['Data']['userToken']

        create_pickle(user_token, self.TOKEN_PATH)
        self.user_token = user_token
        self.session.cart_guid = resp_json['ShoppingCartGuid']
        self.session.user_id = resp_json['Data']['userId']

        create_pickle(self.session, self.SESSION_PATH)
        return True

    def is_budget_available(self):
        # check if it is a working day, if not return
        today = datetime.today()
        if today.weekday() == 5 or today.weekday() == 4:
            if DEBUG:
                print(f'{today} Is Non working day')
            return False

        # check holiday according to Israel gov calendar:
        today = datetime.today()
        date_format = '%Y-%m-%dT%H:%M:%S'
        url = 'https://data.gov.il/api/3/action/datastore_search?resource_id=67492cda-b36e-45f4-9ed1-0471af297e8b'
        r = requests.get(url)
        holidays = json.loads(r.text)
        # maybe there is no need for iteration since the result is sorted.
        for h in holidays['result']['records']:
            h_start = datetime.strptime(h['HolidayStart'], date_format)
            h_ends = datetime.strptime(h['HolidayEnds'], date_format)
            h_name = h['Name']
            if h_start <= today <= h_ends:
                if DEBUG:
                    print(f'{today} is {h_name}')
                return False

        payload = {"culture": "he-IL", "uiCulture": "he", "dateBias": 0}
        report = self.post_next_api('UserTransactionsReport', payload)

        # option1 - check the last order, and check
        last_order_is_today = (report['Data']['orderList'][-1]['orderDateStr'] == datetime.today().strftime("%d.%m.%y"))
        if last_order_is_today:
            if DEBUG:
                print(f'last_order_check:{last_order_is_today}')
            return False

        # check if usage for today > 0
        daily_usage = report['Data']['moneycards'][0]['usage']['daily']
        if daily_usage > 0:
            if DEBUG:
                print(f'Today usage is:{daily_usage}')
            return False

        return True

    def buy_coupon(self, coupon):
        session = self.session

        payload = {"culture": "he-IL", "uiCulture": "he"}
        resp_json = self.post_next_api('GetUser', payload)
        self.cart_guid = resp_json['ShoppingCartGuid']
        self.user_id = resp_json['Data']['userId']

        payload = {"culture": "he-IL", "uiCulture": "he"}
        resp_json = self.post_next_api('GetUserAddresses', payload)
        address = resp_json['Data'][0]

        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he"}
        payload.update(address.copy())
        self.post_next_api('SetAddressInOrder', payload)

        # SetDeliveryMethodInOrder
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he",
                   "deliveryMethod": "delivery"}
        self.post_next_api('SetDeliveryMethodInOrder', payload)

        # SetRestaurantInOrder
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he", "isMobileDevice": True,
                   "restaurantId": "26698"}
        self.post_next_api('SetRestaurantInOrder', payload)

        # SetDishListInShoppingCart
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he",
                   "dishList": [{"dishId": COUPONS_IDS[int(coupon)], "shoppingCartDishId": 1, "quantity": 1,
                                 "assignedUserId": self.user_id, "choices": [], "dishNotes": None,
                                 "categoryId": 278344}]}
        self.post_next_api('SetDishListInShoppingCart', payload)

        # GetPayments
        endpoint = TENBIS_FQDN + f"/NextApi/GetPayments?shoppingCartGuid={self.cart_guid}&culture=he-IL&uiCulture=he"
        headers = {"content-type": "application/json"}
        headers.update({'user-token': self.user_token})
        response = session.get(endpoint, headers=headers, verify=False)
        resp_json = json.loads(response.text)
        # TO_DO (original) - make sure to use only 10BIS cards
        error_msg = resp_json['Errors']
        success_code = resp_json['Success']
        if not success_code:
            print_hebrew((error_msg[0]['ErrorDesc']))
            return
        if DEBUG:
            print("Request:" + endpoint)
            print("Response: " + str(response.status_code))
            print(resp_json)
        main_user = current = [x for x in resp_json['Data'] if x['userId'] == self.user_id]

        # SetPaymentsInOrder
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he", "payments": [
            {"paymentMethod": "Moneycard", "creditCardType": "none", "cardId": main_user[0]['cardId'], "cardToken": "",
             "userId": self.user_id, "userName": main_user[0]['userName'],
             "cardLastDigits": main_user[0]['cardLastDigits'], "sum": coupon, "assigned": True, "remarks": None,
             "expirationDate": None, "isDisabled": False, "editMode": False}]}
        self.post_next_api('SetPaymentsInOrder', payload)

        if DRYRUN:
            return

        # SubmitOrder
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he", "isMobileDevice": True,
                   "dontWantCutlery": False, "orderRemarks": None}
        resp_json = self.post_next_api('SubmitOrder', payload)

        session.cart_guid = resp_json['ShoppingCartGuid']
        # save the last session state to the pickle file for next auth.
        create_pickle(session, self.SESSION_PATH)

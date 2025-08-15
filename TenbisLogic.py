""" 10 Bis logic processor module """
import json
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
import urllib3
import cloudscraper
from PickleSerializer import PickleSerializer

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TENBIS_FQDN = "https://www.10bis.co.il"

COUPONS_IDS = {
    15: 6552646,
    30: 2046839,
    40: 2046840,
    50: 2046841,
    100: 2046845
}

class Tenbis:
    """
    A class used to interact with the 10bis website.
    ...

    Attributes
    ----------
    args : dict
        The arguments passed to the class.
    session : requests.Session
        The session used for making requests.
    cart_guid : str
        The shopping cart GUID.
    user_id : str
        The user ID.
    session_pickle : PickleSerializer
        The PickleSerializer used for storing the session.

    Methods
    -------
    post_next_api(endpoint, payload):
        Makes a POST request to the specified endpoint with the given payload.
    auth():
        Authenticates the user.
    is_budget_available():
        Checks if budget is available.
    buy_coupon(coupon):
        Buys a coupon.
    get_unused_coupons():
        Gets unused coupons.
    """

    def __init__(self, args):
        self.args = args
        self.session = None
        self.cart_guid = None
        self.user_id = None
        self.logger = logging.getLogger('AppLogger')
        self.session_pickle = PickleSerializer("sessions")
        self.scraper = cloudscraper.create_scraper()  # This creates a requests-like session
        self.scraper.get('https://www.10bis.co.il')

        if not self.auth():
            self.logger.info("10Bis logged in Failure")
            raise RuntimeError('Error Authenticating')
        self.logger.info("10Bis logged in Success")

    def post_next_api(self, endpoint, payload):
        """ Makes a POST request to the specified endpoint with the given payload.

        :param endpoint:
        :param payload:
        :return:
        """
        endpoint = TENBIS_FQDN + "/NextApi/" + endpoint
        headers = { "content-type": "application/json" }
        response = self.scraper.post(endpoint, data=json.dumps(payload), headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(f'NextApi http failure:{response.status_code} message:{response.text}')

        resp_json = json.loads(response.text)
        error_msg = resp_json['Errors']
        success_code = resp_json['Success']
        self.logger.debug("Request: %s \nHeaders: %s \n Request Payload: %s", endpoint,
                          json.dumps(headers), json.dumps(payload))
        self.logger.debug("Response: %s", str(response.status_code))
        self.logger.debug(resp_json)
        if not success_code:
            raise RuntimeError('NextApi call failure:' + (error_msg[0]['ErrorDesc'][::-1]))

        return resp_json

    def auth(self):
        """
        Authenticates the user.

        Returns
        -------
        bool
            True if the user is authenticated, False otherwise.
        """
        if self.session_pickle.exists():
            self.session = self.session_pickle.load()
            self.scraper.cookies.set('Authorization', self.session['Authorization'],
                                     domain=".10bis.co.il", secure=True, rest={"HttpOnly": True})
            self.scraper.cookies.set('RefreshToken', self.session['RefreshToken'],
                                     domain=".10bis.co.il", secure=True, rest={"HttpOnly": True})

            payload = {"culture": "he-IL", "uiCulture": "he"}
            try:
                # should fail if the token is expired.
                response = self.post_next_api('GetUser', payload)
                self.logger.debug("User %s Logged In", response['Data']['email'])
                return True
            except RuntimeError:
                self.logger.debug("Refreshing Token")
                headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.9,he-IL;q=0.8,he;q=0.7",
                    "X-App-Type": "web",
                    "Language": "en",
                    "User-Agent": self.scraper.user_agent.headers['User-Agent']
                }

                response = self.scraper.post('https://api.10bis.co.il/api/v1/Authentication/RefreshToken',
                                             headers=headers)
                if response.status_code != 200:
                    self.logger.info(
                        'Error on RefreshToken call status:%s message:%s',
                        response.status_code, response.text)
                    return False

                self.session['Authorization'] = response.cookies.get_dict()['Authorization']
                self.session['RefreshToken'] = response.cookies.get_dict()['RefreshToken']

                response = self.post_next_api('GetUser', payload)
                self.logger.debug('User %s Logged In', response['Data']['email'])

                self.session["user_id"] = response['Data']['userId']
                self.session["cart_guid"] = response['ShoppingCartGuid']

                self.session_pickle.create(self.session)

                return True

        # Phase one -> Email
        email = input("Enter Email: ")
        payload = {"culture": "he-IL", "uiCulture": "he", "email": email}
        self.session = { "cookies" : self.scraper.cookies.get_dict() }
        resp_json = self.post_next_api('GetUserAuthenticationDataAndSendAuthenticationCodeToUser', payload)

        # Phase two -> OTP
        auth_token = resp_json['Data']['codeAuthenticationData']['authenticationToken']
        shop_cart_guid = resp_json['ShoppingCartGuid']
        otp = input("Enter OTP: ")
        payload = {"shoppingCartGuid": shop_cart_guid,
                   "culture": "he-IL",
                   "uiCulture": "he",
                   "email": email,
                   "authenticationToken": auth_token,
                   "authenticationCode": otp}

        resp_json = self.post_next_api('GetUserV2', payload)

        self.session = self.scraper.cookies.get_dict().copy()
        self.session["cart_guid"] = resp_json['ShoppingCartGuid']
        self.session["user_id"] = resp_json['Data']['userId']

        self.session_pickle.create(self.session)
        return True

    def budget_available(self):
        """
        Checks if budget is available.

        Returns
        -------
        int
            Amount of daily unused budget
        """
        payload = {"culture": "he-IL", "uiCulture": "he", "dateBias": 0}
        report = self.post_next_api('UserTransactionsReport', payload)
        available_amount = report['Data']['moneycards'][0]['tenbisCreditConversion']['availableAmount']
        return available_amount

    def buy_coupon(self, coupon):
        """
        Buys a coupon.

        Parameters
        ----------
        coupon : int
            The coupon to buy.
        """
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
                   "dishList": [{"dishId": COUPONS_IDS[coupon], "shoppingCartDishId": 1, "quantity": 1,
                                 "assignedUserId": self.user_id, "choices": [], "dishNotes": None,
                                 "categoryId": 278344}]}
        self.post_next_api('SetDishListInShoppingCart', payload)

        # GetPayments
        endpoint = TENBIS_FQDN + f"/NextApi/GetPayments?shoppingCartGuid={self.cart_guid}&culture=he-IL&uiCulture=he"
        headers = {"content-type": "application/json"}
        response = self.scraper.get(endpoint, headers=headers, verify=False)
        resp_json = json.loads(response.text)

        # TO_DO (original) - make sure to use only 10BIS cards
        error_msg = resp_json['Errors']
        success_code = resp_json['Success']
        if not success_code:
            self.logger.error(error_msg[0]['ErrorDesc'][::-1])
            return
        self.logger.debug("Request: %s", endpoint)
        self.logger.debug("Response: %s", str(response.status_code))
        self.logger.debug(resp_json)
        main_user = [x for x in resp_json['Data'] if x['userId'] == self.user_id]

        # SetPaymentsInOrder
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he", "payments": [
            {"paymentMethod": "Moneycard", "creditCardType": "none", "cardId": main_user[0]['cardId'], "cardToken": "",
             "userId": self.user_id, "userName": main_user[0]['userName'],
             "cardLastDigits": main_user[0]['cardLastDigits'], "sum": coupon, "assigned": True, "remarks": None,
             "expirationDate": None, "isDisabled": False, "editMode": False}]}
        self.post_next_api('SetPaymentsInOrder', payload)

        if self.args.dryrun:
            self.logger.info("Dry Run success, purchase will be skipped.")
            return

        # SubmitOrder
        payload = {"shoppingCartGuid": self.cart_guid, "culture": "he-IL", "uiCulture": "he", "isMobileDevice": True,
                   "dontWantCutlery": False, "orderRemarks": None}
        resp_json = self.post_next_api('SubmitOrder', payload)
        self.logger.info("Order submitted successfully")

        session.cart_guid = resp_json['ShoppingCartGuid']
        # save the last session state to the pickle file for next auth.
        self.session_pickle.create(session)

    def get_unused_coupons(self):
        """
        Gets unused coupons.

        Returns
        -------
        dict
            A dictionary containing the unused coupons.
        """
        month_empty_count = 3
        month_bias = 0
        min_month_with_coupons = date(2010, 1, 1)
        scanned_month = date(date.today().year, date.today().month, 1)
        state_pickle = PickleSerializer('last_state')
        if state_pickle.exists():
            min_month_with_coupons = state_pickle.load()
        actual_min_month_with_coupons = scanned_month
        restaurants = {}
        while month_empty_count != 0 and scanned_month >= min_month_with_coupons:
            self.logger.debug('scanning Month:%s', scanned_month)
            payload = {"culture": "he-IL", "uiCulture": "he", "dateBias": month_bias}
            report = self.post_next_api('UserTransactionsReport', payload)
            all_orders = report['Data']['orderList']
            if len(all_orders) == 0:
                month_empty_count -= 1
            barcode_orders = [x for x in all_orders if x['isBarCodeOrder']]
            for b in barcode_orders:
                restaurants, found_unused_coupons = self.__process_barcode_orders(b, restaurants)
                if found_unused_coupons:
                    actual_min_month_with_coupons = scanned_month
            month_bias -= 1
            scanned_month = scanned_month + relativedelta(months=-1)
        for _, v in restaurants.items():
            v['orders'].sort(key=lambda x: x['unixTime'])

        state_pickle.create(actual_min_month_with_coupons)
        self.logger.debug('Created report between %d/%d and %d/%d',
                          scanned_month.year, scanned_month.month + 1,
                          actual_min_month_with_coupons.year, actual_min_month_with_coupons.month + 1)
        return restaurants

    def __process_barcode_orders(self, b, restaurants):
        """
        Process each barcode order.

        Parameters
        ----------
        b : dict
            The barcode order to process.
        restaurants : dict
            The current restaurants' dictionary.

        Returns
        -------
        dict
            The updated restaurants' dictionary.
        """
        order_id = b['orderId']
        res_id = b['restaurantId']
        endpoint = (TENBIS_FQDN +
                    f"/NextApi/GetOrderBarcode?culture=he-IL&uiCulture=he&orderId={order_id}&resId={res_id}")
        headers = {"content-type": "application/json"}
        response = self.scraper.get(endpoint, headers=headers)
        found_unused_coupons = False
        self.logger.debug("%s\n%s\n%s", endpoint, response.status_code, response.text)
        r = json.loads(response.text)
        error_msg = r['Error']
        success_code = r['Success']
        if not success_code:
            self.logger.error(error_msg['ErrorDesc'][::-1])
            self.logger.error("Error, trying moving to the next barcode")
            return restaurants
        voucher = r['Data']['Vouchers'][0]
        if not voucher['Used']:
            found_unused_coupons = True
            barcode_num = voucher['BarCodeNumber']
            if res_id not in restaurants:
                restaurants[res_id] = {'restaurantName': b['restaurantName'],
                                       'vendorName': voucher['Vendor'],
                                       'orders': []}
            restaurants[res_id]['orders'].append({'Date': b['orderDateStr'],
                                                  'unixTime': b['orderDate'],
                                                  'barcode': '-'.join(
                                                      barcode_num[i:i + 4] for i in
                                                      range(0, len(barcode_num), 4)),
                                                  'barcode_url': voucher['BarCodeImgUrl'],
                                                  'amount': voucher['Amount']})
        return restaurants, found_unused_coupons

    def load_remaining_amount_to_credit(self):
        """
        Loads the remaining amount of daily budget to credit.

        This method checks if the 10Bis credit conversion is enabled. If enabled, it moves the available amount
        to the credit.

        Returns
        -------
        None
        """
        payload = {"culture": "he-IL", "uiCulture": "he", "dateBias": 0}
        report = self.post_next_api('UserTransactionsReport', payload)

        # check the available amount
        if  not report['Data']['moneycards'][0]['tenbisCreditConversion']['isEnabled']:
            self.logger.info("10Bis credit is disabled")
            return

        available_amount = report['Data']['moneycards'][0]['tenbisCreditConversion']['availableAmount']
        moneycardId = report['Data']['moneycards'][0]['moneycardId']

        if self.args.dryrun:
            self.logger.info("Dry Run success, purchase will be skipped.")
            return

        endpoint = 'https://api.10bis.co.il/api/v1/Payments/LoadTenbisCredit'
        payload = {"amount": str(available_amount), "moneycardIdToCharge": moneycardId}
        headers = {"content-type": "application/json"}
        resp_json = self.scraper.patch(endpoint, json=payload, headers=headers)
        if resp_json.status_code != 200:
            self.logger.info("Moving amount to credit failed with errors: %s", resp_json['Errors'])
            self.logger.debug("Error dump: %s", resp_json)
        else:
            self.logger.info("%d NIS moved to credit successfully", available_amount)

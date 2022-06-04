import datetime
import pytz
import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# to: -1 -> Down , 1 -> Up
def roundPrice(price, to=-1, tick=1):
    price = int(price)
    if to == -1:
        price = price - (price % (10 ** tick))
    elif to == 1:
        price - (price % (10 ** tick)) + (10 ** tick)
    return price


class Order:
    def __init__(self, orderType: str, name: str, price: float, amount: int):
        self.type = orderType  # buy, sell
        self.name = name
        self.price = price
        self.amount = amount
        self.datetime = datetime.datetime.now(tz=pytz.timezone('Asia/Tehran'))
        pass


class Broker:
    def __init__(self):
        self.stockTick = {}

        self.defaultSellMargin = 1
        self.minSellMargin = 0.3

        self.stocksToSell = []
        if 'CHROME_PROFILE_DIR' in os.environ and 'CHROME_PROFILE' in os.environ:
            print("Chrome Profile Detected")
            options = webdriver.ChromeOptions()
            options.add_argument("--user-data-dir={}".format(os.environ.get('CHROME_PROFILE_DIR')))
            options.add_argument('--profile-directory={}'.format(os.environ.get('CHROME_PROFILE')))
            self.web = webdriver.Chrome(executable_path="chromedriver", options=options)
        else:
            self.web = webdriver.Chrome(executable_path="chromedriver")

        self.web.get('https://firouzex.ephoenix.ir/')

    def clearPage(self):
        try:
            closeBtns = self.web.find_elements_by_css_selector(".close")
            for btn in closeBtns:
                try:
                    btn.click()
                except:
                    try:
                        self.web.execute_script("arguments[0].click();", btn)
                    except:
                        pass
        except:
            pass

        self.web.find_element_by_css_selector('body').click()
        time.sleep(0.2)
        self.web.find_element_by_css_selector('body').click()
        time.sleep(0.2)
        self.web.find_element_by_css_selector('body').click()
        time.sleep(0.2)
        self.web.find_element_by_css_selector('body').click()
        time.sleep(0.2)

    def addBuy(self, stockName, amount, x, price):
        try:
            self.clearPage()
            yFinalPrice = self.getYesterdayFinalPrice(stockName, addIfMissing=True)
            price = int(price)
            x = float(x)
            amount = int(amount)

            if price != -1:
                orderPrice = int(price)
            else:
                orderPrice = int(yFinalPrice * (100 - float(x)) / 100)

            stockElem = self.selectStock(stockName, addIfMissing=True)
            if stockElem is None:
                print("Stock Element not Found")
                return None

            buyButton = stockElem.find_element_by_css_selector(".buyPart")
            buyButton.click()
            modalExists = False
            retries = 0
            while not modalExists:
                try:
                    if self.web \
                            .find_element_by_css_selector(".modal.order-buy [data-name]") \
                            .get_attribute('value') \
                            == stockName:
                        modalExists = True
                        time.sleep(0.01)
                        retries += 1
                        if retries >= 500:
                            print("Maximum retries reached for modalExists")
                            return None
                    continue
                except:
                    continue

            time.sleep(2)
            modalFilledCorrectly = False
            retries = 0
            while not modalFilledCorrectly:
                formInput = self.web.find_element_by_css_selector('.modal.order-buy [data-price]')
                while formInput.get_attribute('value') != '':
                    formInput.send_keys(Keys.BACK_SPACE)
                time.sleep(0.2)
                for digit in list(str(orderPrice)):
                    formInput.send_keys(digit)
                    time.sleep(0.01)

                formInput = self.web.find_element_by_css_selector('.modal.order-buy [data-quantity]')
                while formInput.get_attribute('value') != '':
                    formInput.send_keys(Keys.BACK_SPACE)
                time.sleep(0.2)
                for digit in list(str(amount)):
                    formInput.send_keys(digit)
                    time.sleep(0.01)

                amountOnModal = self.web.find_element_by_css_selector('.modal.order-buy [data-quantity]') \
                    .get_attribute("value")
                priceOnModal = self.web.find_element_by_css_selector('.modal.order-buy [data-price]') \
                    .get_attribute("value")
                if priceOnModal.replace(',', '').replace('\n', '').replace(' ', '') == str(orderPrice) \
                        and \
                        amountOnModal.replace(',', '').replace('\n', '').replace(' ', '') == str(amount):
                    modalFilledCorrectly = True

                retries += 1
                time.sleep(0.01)
                if retries >= 500:
                    print("Maximum retries reached for modalFilledCorrectly")
                    return None

            stockNameOnModal = self.web.find_element_by_css_selector('.modal.order-buy [data-name]').get_attribute(
                "value")
            amountOnModal = self.web.find_element_by_css_selector('.modal.order-buy [data-quantity]').get_attribute(
                "value")
            priceOnModal = self.web.find_element_by_css_selector('.modal.order-buy [data-price]').get_attribute("value")

            return {'name': stockNameOnModal, 'amount': amountOnModal, 'price': priceOnModal}
        except:
            print("Error!")
            return None

    def addBuyConfirm(self):
        try:
            submitBtn = self.web.find_element_by_css_selector('.modal.order-buy .btnBuy')
            submitBtn.click()
            time.sleep(0.5)
            try:
                self.web.find_element_by_css_selector('.modalError')
                msg = self.web.find_element_by_css_selector('.modalError [data-msg]').get_attribute('innerHTML')
                return msg
            except:
                try:
                    self.web.find_element_by_css_selector('.modalWarning')
                    msg = self.web.find_element_by_css_selector('.modalWarning [data-msg]').get_attribute('innerHTML')
                    return msg
                except:
                    return 1
        except:
            return None

    def editBuy(self, orderID, stockName, price, tick=1):
        try:
            self.clearPage()
            price = int(price)

            orderElem = self.web.find_element_by_id(orderID)
            orderElem.click()
            time.sleep(0.2)
            buyButton = orderElem.find_element_by_css_selector("span[data-edit]")
            self.web.execute_script("arguments[0].click()", buyButton)
            time.sleep(0.2)
            modalExists = False
            retries = 0
            while not modalExists:
                time.sleep(0.01)
                retries += 1
                if retries >= 500:
                    return None
                try:
                    if self.web \
                            .find_element_by_css_selector(".modal.order-buy [data-name]") \
                            .get_attribute('value') \
                            == stockName:
                        modalExists = True
                    continue
                except:
                    continue
            time.sleep(1)

            modalFilledCorrectly = False
            retries = 0
            while not modalFilledCorrectly:
                time.sleep(0.01)
                retries += 1
                if retries >= 500:
                    return None
                formInput = self.web.find_element_by_css_selector('.modal.order-buy [data-price]')
                while formInput.get_attribute('value') != '':
                    formInput.send_keys(Keys.BACK_SPACE)
                time.sleep(0.2)
                for digit in list(str(price)):
                    formInput.send_keys(digit)
                    time.sleep(0.01)

                priceOnModal = self.web.find_element_by_css_selector('.modal.order-buy [data-price]') \
                    .get_attribute("value")
                if priceOnModal.replace(',', '').replace('\n', '').replace(' ', '') == str(price):
                    modalFilledCorrectly = True

            submitBtn = self.web.find_element_by_css_selector('.modal.order-buy .btnBuy')
            submitBtn.click()
            time.sleep(0.5)

            try:
                self.web.find_element_by_css_selector('.modalError')
                msg = self.web.find_element_by_css_selector('.modalError [data-msg]').get_attribute('innerHTML')
                return None
            except:
                try:
                    self.web.find_element_by_css_selector('.modalWarning')
                    msg = self.web.find_element_by_css_selector('.modalWarning [data-msg]').get_attribute('innerHTML')
                    if msg.replace('\n', '') == "Price must be valid against tick table":
                        print("Modify Tick")
                        return self.editBuy(orderID, stockName, price - (price % (10 ** tick)) + (10 ** tick), tick + 1)
                    else:
                        return None
                except:
                    self.stockTick[stockName] = tick
                    return 1
        except:
            return None

    def addSell(self, assetID, stockName, price, tick=1):
        self.clearPage()
        price = int(price)

        try:
            self.web.find_element_by_css_selector("#DataTables_Table_4 tbody tr#" + assetID)
        except:
            return None
        orderElem = self.web.find_element_by_css_selector("#DataTables_Table_4 tbody tr#" + assetID)
        sellButton = orderElem.find_element_by_css_selector("[data-cancel]")
        self.web.execute_script("arguments[0].click()", sellButton)
        time.sleep(0.2)

        modalExists = False
        retries = 0
        while not modalExists:
            time.sleep(0.01)
            retries += 1
            if retries >= 500:
                return None
            try:
                if self.web \
                        .find_element_by_css_selector(".modal.order-sale [data-name]") \
                        .get_attribute('value') \
                        == stockName:
                    modalExists = True
                continue
            except:
                continue
        time.sleep(1)

        modalFilledCorrectly = False
        retries = 0
        while not modalFilledCorrectly:
            retries += 1
            time.sleep(0.01)
            if retries >= 500:
                return None
            formInput = self.web.find_element_by_css_selector('.modal.order-sale [data-price]')
            while formInput.get_attribute('value') != '':
                formInput.send_keys(Keys.BACK_SPACE)
            time.sleep(0.2)
            for digit in list(str(price)):
                formInput.send_keys(digit)
                time.sleep(0.01)

            priceOnModal = self.web.find_element_by_css_selector('.modal.order-sale [data-price]') \
                .get_attribute("value").replace(',', '').replace('\n', '').replace(' ', '')
            priceOnModal = int(priceOnModal)
            if priceOnModal == price:
                modalFilledCorrectly = True

        submitBtn = self.web.find_element_by_css_selector('.modal.order-sale .btnSale')
        submitBtn.click()
        time.sleep(0.5)

        try:
            self.web.find_element_by_css_selector('.modalError')
            msg = self.web.find_element_by_css_selector('.modalError [data-msg]').get_attribute('innerHTML')
            return None
        except:
            try:
                self.web.find_element_by_css_selector('.modalWarning')
                msg = self.web.find_element_by_css_selector('.modalWarning [data-msg]').get_attribute('innerHTML')
                if msg.replace('\n', '') == "Price must be valid against tick table":
                    print("Modify Tick")
                    return self.addSell(assetID, stockName, price - (price % (10 ** tick)), tick + 1)
                else:
                    self.stockTick[stockName] = tick
                    return None
            except:
                return 1

    def editSell(self, orderID, stockName, price, tick=1):
        try:
            self.clearPage()
            price = int(price)

            orderElem = self.web.find_element_by_id(orderID)
            sellButton = orderElem.find_element_by_css_selector("[data-edit]")
            self.web.execute_script("arguments[0].click()", sellButton)
            time.sleep(0.2)

            modalExists = False
            retries = 0
            while not modalExists:
                time.sleep(0.01)
                retries += 1
                if retries >= 500:
                    return None
                try:
                    if self.web \
                            .find_element_by_css_selector(".modal.order-sale [data-name]") \
                            .get_attribute('value') \
                            == stockName:
                        modalExists = True

                    continue
                except:
                    continue
            time.sleep(1)

            modalFilledCorrectly = False
            retries = 0
            while not modalFilledCorrectly:
                time.sleep(0.01)
                retries += 1
                if retries >= 500:
                    return None
                formInput = self.web.find_element_by_css_selector('.modal.order-sale [data-price]')
                while formInput.get_attribute('value') != '':
                    formInput.send_keys(Keys.BACK_SPACE)
                time.sleep(0.2)
                for digit in list(str(price)):
                    formInput.send_keys(digit)
                    time.sleep(0.01)

                priceOnModal = self.web.find_element_by_css_selector('.modal.order-sale [data-price]') \
                    .get_attribute("value").replace(',', '').replace('\n', '').replace(' ', '')
                priceOnModal = int(priceOnModal)
                if priceOnModal == price:
                    modalFilledCorrectly = True

            time.sleep(0.2)
            submitBtn = self.web.find_element_by_css_selector('.modal.order-sale .btnSale')
            submitBtn.click()
            time.sleep(0.5)

            try:
                self.web.find_element_by_css_selector('.modalError')
                msg = self.web.find_element_by_css_selector('.modalError [data-msg]').get_attribute('innerHTML')
                return None
            except:
                try:
                    self.web.find_element_by_css_selector('.modalWarning')
                    msg = self.web.find_element_by_css_selector('.modalWarning [data-msg]').get_attribute('innerHTML')
                    if msg.replace('\n', '') == "Price must be valid against tick table":
                        print("Modify Tick")
                        return self.editSell(orderID, stockName, price - (price % (10 ** tick)), tick + 1)
                    else:
                        return None
                except:
                    self.stockTick[stockName] = tick
                    return 1
        except:
            return None

    def removeSell(self, orderID):
        try:
            self.clearPage()
            orderElem = self.web.find_element_by_id(orderID)
            sellButton = orderElem.find_element_by_css_selector("[data-cancel]")
            self.web.execute_script("arguments[0].click()", sellButton)
            time.sleep(0.2)
            return 1
        except:
            return None

    def selectStock(self, stockName, addIfMissing=False):
        try:
            elements = self.web.find_elements_by_class_name('tradingCellTitle')
            for element in elements:
                if element.get_attribute('innerHTML') == stockName:
                    element.click()
                    retries = 0
                    while self.web.find_element_by_css_selector('[data-instrument-details] [data-symbol]') \
                            .get_attribute('innerHTML') != stockName:
                        time.sleep(0.01)
                        retries += 1
                        element.click()
                        if retries >= 500:
                            return None
                        continue
                    return element.find_element_by_xpath("../..")

            if addIfMissing:
                self.web.find_element_by_css_selector("[data-btn-add-instrument]").click()
                time.sleep(0.4)
                textSearch = self.web.find_element_by_css_selector("[data-instrument-list-dlg] [data-txt-search]")

                while textSearch.get_attribute('value') != '':
                    textSearch.send_keys(Keys.BACK_SPACE)
                time.sleep(0.2)

                for character in list(str(stockName)):
                    buttons = self.web.find_elements_by_css_selector("[data-key-list] button")
                    for button in buttons:
                        print(character, button.get_attribute('innerText'))
                        if button.get_attribute('innerText') == character:
                            self.web.execute_script("arguments[0].click();", button)
                            break
                    time.sleep(0.05)

                time.sleep(1)

                symbols = self.web.find_elements_by_css_selector("[data-search-result-container] li .symbol")
                for symbol in symbols:
                    if symbol.get_attribute('innerText') == stockName:
                        self.web.execute_script("arguments[0].click();", symbol)
                        break
                time.sleep(2)

                elements = self.web.find_elements_by_class_name('tradingCellTitle')
                for element in elements:
                    if element.get_attribute('innerHTML') == stockName:
                        element.click()
                        retries = 0
                        while self.web.find_element_by_css_selector(
                                '[data-instrument-details] [data-symbol]') \
                                .get_attribute('innerHTML') != stockName:
                            time.sleep(0.01)
                            retries += 1
                            element.click()
                            if retries >= 500:
                                return None
                            continue
                        return element.find_element_by_xpath("../..")
            return None
        except:
            return None

    def getYesterdayFinalPrice(self, stockName, addIfMissing=False):
        try:
            if self.selectStock(stockName, addIfMissing) is None:
                return None

            element = self.web.find_element_by_css_selector('[data-yesterday-last-price]')
            price = element.get_attribute('innerHTML')
            price = int(price.replace(',', ''))
            return price
        except:
            return None

    def getBuyOrderBookLastPrice(self, stockName):
        try:
            if self.selectStock(stockName) is None:
                return None
            price = None
            tables = self.web \
                .find_element_by_css_selector('[data-instrument-details]') \
                .find_elements_by_css_selector('table')
            for table in tables:
                last_td_of_first_tr = table \
                    .find_element_by_css_selector('tbody tr td:last-child') \
                    .get_attribute('innerHTML') \
                    .replace(' ', '').replace('\n', '')
                if last_td_of_first_tr == 'خرید':
                    price = table \
                        .find_element_by_css_selector('tbody tr:nth-child(2) td:last-child') \
                        .get_attribute('innerHTML') \
                        .replace(' ', '').replace('\n', '').replace(',', '')
                    price = int(price)

            return price
        except:
            return None

    def getSellOrderBookLastPrice(self, stockName):
        try:
            if self.selectStock(stockName) is None:
                return None
            price = None
            tables = self.web \
                .find_element_by_css_selector('[data-instrument-details]') \
                .find_elements_by_css_selector('table')
            for table in tables:
                first_td_of_first_tr = table \
                    .find_element_by_css_selector('tbody tr td') \
                    .get_attribute('innerHTML') \
                    .replace(' ', '').replace('\n', '')
                if first_td_of_first_tr == 'فروش':
                    price = table \
                        .find_element_by_css_selector('tbody tr:nth-child(2) td') \
                        .get_attribute('innerHTML') \
                        .replace(' ', '').replace('\n', '').replace(',', '')
                    price = int(price)

            return price
        except:
            return None

    def getActiveBuyOrders(self):
        try:
            self.clearPage()
            orderList = []
            trs = self.web.find_elements_by_css_selector("[data-order-list-container] [data-status='Active']")
            for tr in trs:
                orderType = tr.find_element_by_css_selector('td:nth-child(8)').get_attribute('innerHTML') \
                    .replace(' ', '').replace('\n', '').replace(',', '')
                if orderType != 'خرید':
                    continue
                orderID = tr.get_attribute('id')
                name = tr.find_element_by_css_selector('td:nth-child(3)').get_attribute('innerHTML')
                amount = tr.find_element_by_css_selector('td:nth-child(5)').get_attribute('innerHTML')
                price = tr.find_element_by_css_selector('td:nth-child(6)').get_attribute('innerHTML') \
                    .replace(' ', '').replace('\n', '').replace(',', '')

                top = self.getBuyOrderBookLastPrice(name)

                yesterdayPrice = self.getYesterdayFinalPrice(name, True)

                amount = int(amount)
                price = int(price)
                top = int(top)
                yesterdayPrice = int(yesterdayPrice)

                orderList.append({'id': orderID, 'name': name, 'amount': amount, 'price': price,
                                  'top': top, 'yesterday': yesterdayPrice})
            return orderList
        except:
            return []

    def getPortfolio(self):
        try:
            portfolio = []
            self.clearPage()
            trs = self.web.find_elements_by_css_selector("#DataTables_Table_4 tbody tr")
            for tr in trs:
                orderID = tr.get_attribute('id')
                stockName = tr.find_element_by_css_selector('td:nth-child(1)').get_attribute('innerText')
                amount = tr.find_element_by_css_selector('td:nth-child(2)').get_attribute('innerText') \
                    .replace(' ', '').replace('\n', '').replace(',', '')
                avgBuyPrice = tr.find_element_by_css_selector('td:nth-child(3)').get_attribute('innerText') \
                    .replace(' ', '').replace('\n', '').replace(',', '')

                amount = int(amount)
                avgBuyPrice = int(avgBuyPrice)

                portfolio.append({'id': orderID, 'name': stockName, 'amount': amount, 'avgBuyPrice': avgBuyPrice})
                self.getYesterdayFinalPrice(stockName, True)
            return portfolio
        except:
            return []

    def getActiveSellOrders(self):
        try:
            self.clearPage()
            orderList = []
            trs = self.web.find_elements_by_css_selector("[data-order-list-container] [data-status='Active']")
            for tr in trs:
                orderType = tr.find_element_by_css_selector('td:nth-child(8)').get_attribute('innerHTML') \
                    .replace(' ', '').replace('\n', '').replace(',', '')
                if orderType != 'فروش':
                    continue
                orderID = tr.get_attribute('id')
                name = tr.find_element_by_css_selector('td:nth-child(3)').get_attribute('innerHTML')
                amount = tr.find_element_by_css_selector('td:nth-child(5)').get_attribute('innerHTML')
                price = tr.find_element_by_css_selector('td:nth-child(6)').get_attribute('innerHTML') \
                    .replace(' ', '').replace('\n', '').replace(',', '')

                top = self.getSellOrderBookLastPrice(name)

                yesterdayPrice = self.getYesterdayFinalPrice(name, True)

                amount = int(amount)
                price = int(price)
                top = int(top)
                yesterdayPrice = int(yesterdayPrice)

                orderList.append({'id': orderID, 'name': name, 'amount': amount, 'price': price,
                                  'top': top, 'yesterday': yesterdayPrice})

            return orderList
        except:
            return []

    def getAll(self):
        buyOrders = self.getActiveBuyOrders()
        sellOrders = self.getActiveSellOrders()
        portfolio = self.getPortfolio()

        allOrders = {
            'buy': buyOrders,
            'sell': sellOrders,
            'portfolio': portfolio
        }
        return allOrders

    def intervalCB(self):
        try:
            activeBuyOrders = self.getActiveBuyOrders()
            activeSellOrders = self.getActiveSellOrders()
            portfolio = self.getPortfolio()
        except:
            return None

        for order in activeBuyOrders:
            yesterdayPrice = order['yesterday']
            top = order['top']
            price = order['price']
            print(price, top, yesterdayPrice)

            if price == top or price == yesterdayPrice:
                print(str(order['name']) + "is on top or equal to yesterday's final price")
            else:
                desiredPrice = min(yesterdayPrice, top + 1)
                print(str(order['name']) + " new price is " + str(desiredPrice))
                try:
                    tick = self.stockTick[order['name']] if order['name'] in self.stockTick else 1
                    self.editBuy(order['id'], order['name'], desiredPrice, tick)
                except:
                    print("Connot Edit Buy Order!")

        for asset in portfolio:
            relatedSellOrder = [order for order in activeSellOrders if order['name'] == asset['name']]
            relatedSellOrder = relatedSellOrder[0] if len(relatedSellOrder) else None

            if relatedSellOrder is None:
                if asset['name'] not in self.stocksToSell:
                    print("Ignore {}. Not in sell list.".format(asset['name']))
                    continue
                desiredPrice = asset['avgBuyPrice'] * (100 + self.defaultSellMargin) / 100
                desiredPrice = int(desiredPrice)

                try:
                    print(asset['name'], "Not Available in Sell Order List. Let's add it.")
                    tick = self.stockTick[asset['name']] if asset['name'] in self.stockTick else 1
                    self.addSell(asset['id'], asset['name'], desiredPrice, tick)
                except:
                    print("Cannot Add Sell Order")

            elif relatedSellOrder['amount'] == asset['amount']:

                price = relatedSellOrder['price']
                avgBuyPrice = asset['avgBuyPrice']
                yesterdayPrice = relatedSellOrder['yesterday']

                tick = self.stockTick[asset['name']] if asset['name'] in self.stockTick else 1

                minSellPrice = roundPrice(int(avgBuyPrice * (100 + self.minSellMargin) / 100), -1, tick)
                todayMinPrice = roundPrice(int(yesterdayPrice * 0.95), -1, tick)
                minPrice = max(minSellPrice, todayMinPrice)

                top = relatedSellOrder['top']

                desiredPrice = max(minPrice, roundPrice(top - 1, -1, tick))

                if price == top or price == minPrice or price == desiredPrice:
                    print("We have the best possible Price")
                else:
                    print(asset['name'], "Update Sell Price.")
                    try:
                        self.editSell(relatedSellOrder['id'], relatedSellOrder['name'], desiredPrice, tick)
                    except:
                        print("Cannot Edit Sell Order")

            elif relatedSellOrder['amount'] < asset['amount']:

                print(asset['name'], "Remove Sell")
                try:
                    self.removeSell(relatedSellOrder['id'])
                except:
                    print("Cannot Remove Sell Order")

        return self.getAll()

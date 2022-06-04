import json

from utils import Broker
import webview


class Api:
    def __init__(self):
        self.broker: Broker

    def intervalCB(self):
        result = self.broker.intervalCB()
        try:
            return {'function': 'intervalCB', 'code': 1, 'message': '', 'result': result}
        except:
            return {'function': 'intervalCB', 'code': -1, 'message': '', 'result': []}

    def openBrowser(self):
        self.broker = Broker()
        return {'function': 'openBrowser', 'code': 1, 'message': 'browser opened'}

    def initSelenium(self):
        self.broker.clearPage()
        return {'function': 'initSelenium', 'code': 1, 'message': 'selenium inited'}

    def getYesterdayFinalPrice(self, stockName):
        price = self.broker.getYesterdayFinalPrice(stockName)
        if price is None:
            return {'function': 'getYesterdayFinalPrice', 'code': 0, 'message': 'Stock name not found', 'price': -1}
        return {'function': 'getYesterdayFinalPrice', 'code': 1, 'message': 'Stock Name Found', 'price': price}

    def getBuyOrderBookLastPrice(self, stockName):
        price = self.broker.getBuyOrderBookLastPrice(stockName)
        if price is None:
            return {'function': 'getBuyOrderBookLastPrice', 'code': 0, 'message': 'Stock name not found', 'price': -1}
        return {'function': 'getBuyOrderBookLastPrice', 'code': 1, 'message': 'Stock Name Found', 'price': price}

    def getSellOrderBookLastPrice(self, stockName):
        price = self.broker.getSellOrderBookLastPrice(stockName)
        if price is None:
            return {'function': 'getSellOrderBookLastPrice', 'code': 0, 'message': 'Stock name not found', 'price': -1}
        return {'function': 'getSellOrderBookLastPrice', 'code': 1, 'message': 'Stock Name Found', 'price': price}

    def addBuy(self, stockName, amount, x, price):
        try:
            values = self.broker.addBuy(stockName, amount, x, price)
            if values is not None:
                return {'function': 'addBuy', 'code': 1, 'message': 'Form Filled', 'values': values}
        except:
            return {'function': 'addBuy', 'code': 0, 'message': 'Form Not Filled', 'values': -1}
        return {'function': 'addBuy', 'code': 0, 'message': 'Form Not Filled', 'values': -1}

    def addBuyConfirm(self):
        result = self.broker.addBuyConfirm()
        if result == 1:
            return {'function': 'addBuyConfirm', 'code': 1, 'message': 'Bought'}
        else:
            return {'function': 'addBuyConfirm', 'code': 0, 'message': result}

    def getActiveBuyOrders(self):
        result = self.broker.getActiveBuyOrders()
        return {'function': 'getActiveBuyOrders', 'code': 1, 'message': '', 'result': result}

    def getActiveSellOrders(self):
        result = self.broker.getActiveSellOrders()
        return {'function': 'getActiveSellOrders', 'code': 1, 'message': '', 'result': result}

    def getPortfolio(self):
        try:
            portfolio = self.broker.getPortfolio()
            return {'function': 'getPortfolio', 'code': 1, 'message': '', 'result': portfolio}
        except:
            return {'function': 'getPortfolio', 'code': -1, 'message': '', 'result': []}

    def getAll(self):
        try:
            allOrders = self.broker.getAll()
            return {'function': 'getAll', 'code': 1, 'message': '', 'result': allOrders}
        except:
            return {'function': 'getAll', 'code': -1, 'message': '', 'result': []}

    def setDefaultParameters(self, defaultSellMargin, minSellMargin):
        defaultSellMargin = float(defaultSellMargin)
        self.broker.defaultSellMargin = defaultSellMargin

        minSellMargin = float(minSellMargin)
        self.broker.minSellMargin = minSellMargin

        return {'function': 'setParameters', 'code': 1, 'message': 'defaultSellMargin:' + str(defaultSellMargin)}

    def stocksToSell(self, stocks):
        # stocks = json.loads(stocks)
        self.broker.stocksToSell = stocks
        return {'function': 'stocksToSell', 'code': 1, 'message': 'stocks to sell set:' + str(stocks)}


def main():
    api = Api()

    window = webview.create_window('FirouzeX', width=1500, height=800, url="web/dashboard.html", js_api=api)
    webview.start(debug=True)


if __name__ == '__main__':
    main()

import requests
import json


def getHamsterCards(authorizationToken):
    try:
        url = "https://api.hamsterkombat.io/clicker/upgrades-for-buy"

        payload = {}
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en,en-US;q=0.9",
            "Authorization": "Bearer " + authorizationToken,
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Origin": "https://hamsterkombat.io",
            "Referer": "https://hamsterkombat.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 2201117TY Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.179 Mobile Safari/537.36",
            "X-Requested-With": "org.telegram.messenger",
            "sec-ch-ua": '"Chromium";v="124", "Android WebView";v="124", "Not-A.Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        cards = json.loads(response.text)["upgradesForBuy"]
        return addPriceDeltaRatio(cards)
    except:
        return []


def addPriceDeltaRatio(cards):
    result = []
    for card in cards:
        try:
            card["priceDeltaRatio"] = card["price"] / card["profitPerHourDelta"]
        except:
            card["priceDeltaRatio"] = 0
        result.append(card)
    return result


def removeZeroPriceDeltaRatio(cards):
    result = []
    for card in cards:
        if card["priceDeltaRatio"] > 0:
            result.append(card)
    return result


def sortPriceDataRatio(cards):
    return sorted(cards, key=lambda x: x["priceDeltaRatio"])


def findCardToBuy(authorizationToken):
    cards = getHamsterCards(authorizationToken)
    cards = removeZeroPriceDeltaRatio(cards)
    cards = sortPriceDataRatio(cards)
    # print(cards)

    for card in cards:
        if card["isAvailable"] and not card["isExpired"]:
            if "cooldownSeconds" in card:
                if card["cooldownSeconds"] == 0:
                    return card
            else:
                return card


def upgradeCard(cardName, authorizationToken):
    url = "https://api.hamsterkombat.io/clicker/buy-upgrade"

    payload = json.dumps({"upgradeId": cardName, "timestamp": 1717797055579})
    headers = {
        "Accept-Language": "en,en-US;q=0.9",
        "Connection": "keep-alive",
        "Origin": "https://hamsterkombat.io",
        "Referer": "https://hamsterkombat.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; 2201117TY Build/TKQ1.221114.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.179 Mobile Safari/537.36",
        "X-Requested-With": "org.telegram.messenger",
        "accept": "application/json",
        "authorization": "Bearer " + authorizationToken,
        "content-type": "application/json",
        "sec-ch-ua": '"Chromium";v="124", "Android WebView";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }

    response = requests.request("POST", url, headers=headers, data=payload)


count = 100
token = ""

n = 0
while n < count:
    card = findCardToBuy(token)
    print(card)
    upgradeCard(card["id"], token)
    n += 1

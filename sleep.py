import requests
import json
import time
from datetime import datetime
import argparse
import threading

sleepDuration = 300


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

    for card in cards:
        if card["isAvailable"] and not card["isExpired"]:
            if "cooldownSeconds" in card:
                if card["cooldownSeconds"] == 0:
                    return card
            else:
                return card


def upgradeCard(cardName, authorizationToken):
    try:
        url = "https://api.hamsterkombat.io/clicker/buy-upgrade"

        payload = json.dumps(
            {"upgradeId": cardName, "timestamp": int(time.time() * 1000)}
        )
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
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        return False


def runUpgrade(token):
    while True:
        try:
            card = findCardToBuy(token)
            res = upgradeCard(card["id"], token)
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            print(formatted_time + ":  " + str(card), "       success: " + str(res))
        except:
            return
        finally:
            time.sleep(sleepDuration)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tokens", type=str, help="tokens(separate with comma)")
    args = parser.parse_args()

    threads = []
    for token in args.tokens.split(","):
        thread = threading.Thread(target=runUpgrade, args=(token,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

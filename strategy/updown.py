import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from coin import *
import time
from datetime import datetime, timezone, timedelta

# param #######################################################################
FEE = 0.003  # 수수료는 0.3%겠지?
UPDOWN = 0.01  # 2% 상하로 걸어놓기..  성공하면 0.7%먹는 게임?
BETTING = 50000  # 한번에 거는 돈의 크기
COOL_TIME = 60 * 10  # 초단위
TIMEOUT_DAYS = 5
###############################################################################

f = open("../upbit_api_key.txt", 'r')
access_key = f.readline().rstrip()
secret_key = f.readline().rstrip()
f.close()
coin = Coin('upbit',access_key,secret_key)

avg_gap = 0
skip_turn = 10
gap_sum = 0
cnt = 0

while True:
    try:
        a = coin.get_price('BTC', 'KRW')
        money = coin.get_asset_info('KRW')
        btc = coin.get_asset_info('BTC')
    except Exception as e:
        print('err', e)
        time.sleep(1)
        continue

    print('KRW..', money)
    print('BTC..', btc)
    print(datetime.now().strftime("%m-%d %H:%M:%S"), 'BTC price..', 'upbit', a)
    #a = round(a, -1) # minimum 10 won

    ask_price = a + a * UPDOWN;ask_price = round(ask_price, -3) # minimum 1000 won
    bid_price = a - a * UPDOWN;bid_price = round(bid_price, -3) # minimum 1000 won
    ask_cnt = float(BETTING) / ask_price 
    bid_cnt = float(BETTING) / bid_price
    if money['free'] > bid_price * bid_cnt :
        pass
    else:
        print('not enough KRW!')
        time.sleep(COOL_TIME)
        continue

    if btc['free'] > ask_cnt:
        oid1 = coin.limit_buy('BTC', bid_price, bid_cnt)
        oid2 = coin.limit_sell('BTC', ask_price, ask_cnt)
        print("oid:", {oid1, oid2})
    else:
        print('not enough BTC!')

    try:
        # 고착화를 막기위해 일정기간 이상의 미체결 주문 청산
        print("cancel pending orders...")
        l = coin.get_live_orders('BTC', 'KRW')
        KST = timezone(timedelta(hours=9))
        for (oid,odt) in l:
            now = datetime.now(KST)
            date_diff = (now-odt).days
            if date_diff >= TIMEOUT_DAYS:
                r = coin.cancel(oid)
                print(r)
    except Exception as e:
        print('err', e)

    time.sleep(COOL_TIME)

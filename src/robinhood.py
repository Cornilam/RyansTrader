import json
import requests
import datetime as dt
import config
import robin_stocks.robinhood as rh


def login():
    # this function will be the start of the robinhood series..
    # first thing we will login and then check our current balance and buying power
    rh.login(config.username, config.password)
    account_details = rh.profiles.load_account_profile()

    buying_power = float(account_details['cash'])

    print('Welcome to Robinhood, you have ' + '$' + str(buying_power) + ' available to spend')


def SPY_converter(spx, strike):
    global new_strike
    if 'SPX' in spx:
        spx = 'SPY'
        Strike = str(float(strike) / 1)
        print(Strike)
        new_strike = Strike[0:3]

    return spx, new_strike


def purchaser(symbol, strike, option_type):
    today = dt.date.today()
    friday = today + dt.timedelta((4 - today.weekday()) % 7)

    if 'SPX' in symbol:
        (symbol, strike) = SPY_converter(symbol, strike)
    try:
        print('trying to fetch options data for {} at strike {} expiring on {}'.format(symbol, strike, friday))
        options_data = rh.options.find_options_by_expiration_and_strike(inputSymbols=symbol,
                                                                        expirationDate=str(friday),
                                                                        strikePrice=strike, optionType=option_type)
    except:
        print('no options data available')
        options_data = 'NONE'
        pass
    latest_price = rh.stocks.get_latest_price(symbol, includeExtendedHours=False)

    print('latest price for {}: {}'.format(symbol, latest_price))

    return options_data

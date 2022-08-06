import requests
import json
from robinhood import purchaser, login

daily_watchlist = []
discord_channel_id = '852526152252784651'
watchlist_id = '749795102100160542'

ticker = ''
option_type = 'call'
strike_price = ''


def write_json_to_file(json_data, file_name_to_write):
    # use this to write most json data to a file. 
    with open(file_name_to_write, 'a', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)
        f.write(',\n')


def retrieve_messages(channel_id):
    # Make an Http GET request to the discord chat to pull the last 50 messages.
    latest_messages_response = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers={
        'authorization': 'NDI1MTIxNDcwMTgwNjIyMzY4.XpEVVQ.PbufYbTadjH2JbAuMPE9xFm6-5c'})

    # write_json_to_file(latest_messages_response, 'latest_messages.json')
    return json.loads(latest_messages_response.text)


def get_tickers_from_watchlist(description):
    tickers_array = []
    description_words = description.split()

    for each_stock in description_words:
        if '$' in each_stock and each_stock[1:].isalpha():
            tickers_array.append(each_stock)

    return tickers_array


def init_watchlist():
    # here we are going to retrieve the last 50 messages that were sent out in watchlist channel
    all_messages = retrieve_messages(watchlist_id)
    # empty list to place our tickers in
    watchlist = []
    # open message and get to embeds in json string
    for each_message in all_messages:
        # getting into the embeds
        embeddedmessage = each_message['embeds']
        for embedded_message in embeddedmessage:
            if '$' in embedded_message['description']:
                tickers = get_tickers_from_watchlist(embedded_message['description'])
                watchlist.extend(tickers)

    watchlist.append('$SPX')
    watchlist.append('$CHWY')
    return watchlist


def ticker_in_watchlist(ticker):
    global daily_watchlist

    for each_ticker in daily_watchlist:
        stock_symbol = each_ticker

        # if out watchlist item contains a $ sign
        if '$' in each_ticker:
            stock_symbol = each_ticker.replace('$', '')

        if str(stock_symbol) in str(ticker):
            return str(stock_symbol)

    return None


def strike_processor(strike):
    print(strike)
    Strike = strike[0:3]
    print(Strike)
    return Strike


def options_data_processor(data):
    global ask_price
    for options_data in data:
        if len(options_data) > 0:
            ask_price = (options_data['ask_price'])

    print('the ask price for a contract is {}'.format(ask_price))


def process_message(last_message):
    global option_type, ticker, strike_price
    # here we are going to start processing the messages that we recieved and search for tickers, strikes, calls/puts and try our best to get a near fill.
    for message in last_message:
        # the description is embedded in the message with just means you have to open it up using the right key.
        embeddedmessage = message['embeds']
        for each_message in embeddedmessage:
            if len(each_message) > 0:
                # the action that we are interested in is found in the title, its going to be either entry, scale, or exit. 
                if 'title' in each_message:
                    # here we are going to process the message if entry is found as the action word
                    if 'ENTRY' in each_message['title']:
                        split_message = each_message['description'].split()
                        # here we split the message to first search for the ticker that hes entrying into.
                        for stock in split_message:
                            if '$' in stock:
                                ticker = ticker_in_watchlist(stock)
                        for strike in split_message:
                            if strike.endswith('p'):
                                option_type = 'put'
                                strike_price = strike_processor(strike)
                            if strike.endswith('c'):
                                option_type = 'call'
                                strike_price = strike_processor(strike)
                        strike_processor(strike_price)
                        options_data = purchaser(ticker, strike_price, option_type)

                        print('options data for {} {} at strike {}'.format(ticker, option_type, strike_price))
                        options_data_processor(options_data)


def discord_checker():
    pass


def main():
    global daily_watchlist
    daily_watchlist = init_watchlist()
    print(daily_watchlist)

    retrieve_messages(discord_channel_id)
    latest_message = retrieve_messages(discord_channel_id)

    process_message(latest_message)

    print('all done')


login()
main()

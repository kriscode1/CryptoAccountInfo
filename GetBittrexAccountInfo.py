# Retrieves balance and open order info from Bittrex.
# Uses the Bittrex API: https://bittrex.com/home/api
# Estimates USD value with a public Bitcoin index.
# 
# Kristofer Christakos
# Modify as desired.

import urllib.request
import time, datetime
import hmac, hashlib
import json

api_key = "your api key"
api_secret = "your api secret"


print(datetime.datetime.now().ctime(), "\tUTC:", datetime.datetime.utcnow().ctime())
print("")

def ParseBittrexResponse(response_text, debug=False):
	'''Parses both public and private Bittrex JSON responses and returns None if failure.'''
	
	result = json.loads(response_text)
	if (result['success'] != True):
		print("Failed response:", response_text)
		debug = True
		result = None
	else:
		result = result['result']
	return result

def GetPrivateRequestForBittrex(request_url, api_key, api_secret, debug=False):
	'''Submits a private request to Bittrex, returns a parsed response or None if failure.'''
	
	def BuildPrivateRequestForBittrex(url_root):
		'''
		Helper function to append Bittrex authentication info to the request URL.
		Parameter "url_root" is a request URL string such as "https://bittrex.com/api/v1.1/account/getbalances"
		Returns a request object from urllib.request.Request() with necessary headers.
		The request is authenticated by adding api_key and nonce to the request URL.
		'''
		
		nonce = str(time.time())
		request_url = url_root
		if ('?' not in request_url): request_url += '?'
		if (request_url[-1] != '?'): request_url += '&'
		request_url += "apikey=" + api_key + "&nonce=" + nonce
		
		hash = hmac.new(bytes(api_secret, 'utf-8'), bytes(request_url, 'utf-8'), hashlib.sha512).hexdigest()
		request_obj = urllib.request.Request(request_url)
		request_obj.add_header('apisign', hash)
		return request_obj
	
	request_obj = BuildPrivateRequestForBittrex(request_url)
	response = urllib.request.urlopen(request_obj)
	response_text = response.read()
	result = ParseBittrexResponse(response_text, debug)
	if result == None: debug = True
	if debug:
		print(response.geturl())
		print(response.info())
		print(response.getcode())
	return result;

def GetPublicRequestFromBittrex(url, debug=False):
	'''Submits a public request to Bittrex, returns the parsed response object.'''
	response_text = urllib.request.urlopen(url).read()
	result = ParseBittrexResponse(response_text, debug)
	if result == None: debug = True
	if debug:
		print(url)
	return result

def GetLastPriceFromBittrex(market, debug=False):
	'''
	Gets the last price traded for the given Bittrex market.
	Parameter "market" is a string, can be found in Bittrex URLs. Ex: "USDT-ETH"
	'''
	
	last_price = None
	try:
		last_price = GetPublicRequestFromBittrex("https://bittrex.com/api/v1.1/public/getticker?market=" + market)['Last']
	except:
		print("Error, market probably not found:", market)
	return last_price

#	Used to use coindesk.com API to fetch a Bitcoin-USD index, but they began authenticating requests.
#	Switched to blockchain.info.
#btc_price = json.loads(urllib.request.urlopen("https://api.coindesk.com/v1/bpi/currentprice.json").read())['bpi']['USD']['rate_float']
btc_price = json.loads(urllib.request.urlopen("https://blockchain.info/ticker").read())['USD']['last']
print("Current BTC Price: $" + str(btc_price))
print("")

print("Balances:")
print("Coin\tPrice (BTC)\t{:8}\tValue (BTC)\tValue (USD)".format("Balance"))
total_btc = 0.0
total_usd = 0.0
balances = GetPrivateRequestForBittrex("https://bittrex.com/api/v1.1/account/getbalances", api_key, api_secret)
for balance in balances:
	if (balance['Balance'] == 0.0): continue
	last_price = 0.0
	btc_value = None
	
	if (balance['Currency'] == "BTC"):
		btc_value = balance['Balance']
	elif (balance['Currency'] == "USDT"):
		market = "USDT-BTC"
		last_price = GetLastPriceFromBittrex(market)
		if (last_price == None): continue
		btc_value = balance['Balance'] / last_price
	else:
		#Get the BTC-priced market for all other coins
		market = "BTC-" + balance['Currency']
		last_price = GetLastPriceFromBittrex(market)
		if (last_price == None): continue
		btc_value = last_price * balance['Balance']
	
	usd_value = btc_value * btc_price
	if usd_value > 1.00:
		print("{}\t{:.8f}\t{:.8f}\t{:.8f} BTC\t${:.2f} USD".format(balance['Currency'], last_price, balance['Balance'], btc_value, usd_value))
		total_btc += btc_value
		total_usd += usd_value

print("Total\t{:10}\t{:.8f} BTC\t\t\t${:.2f} USD".format("", total_btc, total_usd))

print("")
print("Open Orders:")
open_orders = GetPrivateRequestForBittrex("https://bittrex.com/api/v1.1/market/getopenorders", api_key, api_secret)
for order in open_orders:
	print("{:10} {} {} ".format(order['Exchange'], order['OrderType'], order['Quantity']), end="")
	order_price = None
	if order['IsConditional']:
		#Printing stop order
		print("when {} {:.8f} thru to {:.8f}".format(order['Condition'], order['ConditionTarget'], order['Limit']))
		order_price = order['ConditionTarget']
	else:
		#Printing limit order
		print("at limit", order['Limit'])
		order_price = order['Limit']
	last_price = GetLastPriceFromBittrex(order['Exchange'])
	if last_price == None: continue
	net = last_price - order_price
	net_percent = net/last_price * 100
	print("		   Current price is {:.8f}, {:.8f} {:.2f}% away".format(last_price, net, net_percent))

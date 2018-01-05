# CryptoAccountInfo
Retrieves balance and open-order info from Bittrex and estimates portfolio value.

This is a command line Python 3 program that uses the Bittrex API to fetch personal account information and current coin prices. Bittrex portfolio value is estimated using a public Bitcoin index API. I wrote this to quickly check my blanaces (read-only for higher security, and avoids the two factor authentication required of a browser-based read/write sign-in) and see whether my bids/offers/stops have been filled yet. 

To use, sign into Bittrex and create a read-only API key & secret. Then fill those values into "api_key" and "api_secret". 

Example output:

    Thu Jan  4 19:33:41 2018        UTC: Fri Jan  5 00:33:41 2018

    Current BTC Price: $15007.11

    Balances:
    Coin    Price (BTC)     Balance         Value (BTC)     Value (USD)
    ETH     0.06313998      1.11100000      0.07014852 BTC  $1052.73 USD
    XMR     0.02429102      2.22200000      0.05397465 BTC  $810.00 USD
    Total                   3.33300000 BTC                  $1862.73 USD

    Open Orders:

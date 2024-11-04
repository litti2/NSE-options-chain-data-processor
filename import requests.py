import requests
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_nse_option_chain(instrument_name="NIFTY", expiry_date=None, side="CE"):
    """
    Fetches NSE options chain data for a given instrument. Parses JSON to extract highest bid (PE) or ask (CE) prices.
    """
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=" + instrument_name
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logging.error("Error fetching data from NSE API: %s", e)
        return None
    except ValueError:
        logging.error("Error decoding JSON response")
        return None

    # Check if the necessary data structure exists
    if "records" not in data or "data" not in data["records"]:
        logging.error("Unexpected data format in API response")
        return None

    records = []
    for record in data["records"]["data"]:
        strike_price = record.get("strikePrice")
        
        # Check if the 'CE' or 'PE' key exists and get the appropriate bid/ask price
        if side == "PE" and "PE" in record:
            bid_price = record["PE"].get("bidprice", 0)
            records.append([instrument_name, strike_price, side, bid_price])
        elif side == "CE" and "CE" in record:
            ask_price = record["CE"].get("askPrice", 0)
            records.append([instrument_name, strike_price, side, ask_price])

    # Check if records were retrieved successfully
    if not records:
        logging.warning("No option chain data found for %s with side %s", instrument_name, side)
    
    return pd.DataFrame(records, columns=['instrument_name', 'strike_price', 'side', 'bid/ask'])

def calculate_margin_and_premium(data, lot_size=75):
    """
    Adds 'premium_earned' and a placeholder 'margin_required' column to the data.
    """
    if data.empty:
        logging.warning("Data is empty. Skipping calculations.")
        data['premium_earned'] = 0
        data['margin_required'] = 0  # Placeholder for demonstration
    else:
        data['premium_earned'] = data['bid/ask'] * lot_size
        # Placeholder margin value - replace with real API call if available
        data['margin_required'] = 1000  # Example placeholder value
    return data

def main():
    instrument_name = "NIFTY"
    expiry_date = None
    side = "CE"

    # Fetch Option Chain Data
    df_options = get_nse_option_chain(instrument_name, expiry_date, side)
    if df_options is not None and not df_options.empty:
        print("Option Chain Data:")
        print(df_options)

        # Calculate Premium
        df_final = calculate_margin_and_premium(df_options)
        print("\nData with Premium:")
        print(df_final)
    else:
        logging.info("No data to display.")

if __name__ == "__main__":
    main()

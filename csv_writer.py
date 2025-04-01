import csv

def write_to_csv(data, filename='nifftyy_data.csv'):
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["timestamp", "nifty_value", "atm_strike", "ce_price", "pe_price", "ce_vwap", "pe_vwap", "ce_vwma", "pe_vwma", "super_trend_ce", "super_trend_pe"])
        
        file.seek(0, 2) 
        if file.tell() == 0:
            writer.writeheader() 

        writer.writerow(data)
        file.flush() 

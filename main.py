import requests
import time
import csv
import pandas as pd
import json
from tor import get_current_ip,renew_tor_ip
from scrape_data import get_used_car_intermediate_data,extract_data_from_used_car_url

if __name__ == "__main__":
	locs = pd.read_csv("./config/locations.csv")

	"""
		Get all the links of used cars for the given location(s)
	"""
	filename = "./output/data_v3/car_dekho_intermediate_v2.csv"
	for loc in locs.values:
	    with open (filename, 'a') as csvfile:
	        print("fetching: ",loc[0])
	        data = get_used_car_intermediate_data(loc[0])
	        # print(data)
	        headers = list(data.keys())
	        writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)
	        if csvfile.tell() == 0:
	            writer.writeheader()
	        modif_data = []
	        for count in range(len(data[headers[0]])):
	            modif_data.append({
	                headers[0]:data[headers[0]][count],
	                headers[1]:data[headers[1]][count],
	                headers[2]:data[headers[2]][count],
	                headers[3]:data[headers[3]][count],
	                headers[4]:data[headers[4]][count],
	                headers[5]:data[headers[5]][count],
	                headers[6]:data[headers[6]][count],
	                headers[7]:data[headers[7]][count],
	                headers[8]:data[headers[8]][count],
	                headers[9]:data[headers[9]][count],
	                headers[10]:data[headers[10]][count],
	                headers[11]:data[headers[11]][count],
	                headers[12]:data[headers[12]][count],
	            })
	        for x in modif_data:
	            writer.writerow(x)

	"""
		Scrape all the data from the links in the car_dekho_intermediate.csv file and update the DataFrame
	"""
	df = pd.read_csv(filename)
	df_test = df.copy()
	ch = df_test.to_dict('records')
	print(get_current_ip())
	for count,row in enumerate(ch):
	    if count % 300 == 0 and count > 0:            
	        # renew_tor_ip()
	        print(get_current_ip())
	        time.sleep(3)
	    print(count," -- ",row['main_page_link'])
	    res = extract_data_from_used_car_url(row['main_page_link'],json.load(open('./config/required_keys.json')),isAssured=bool(row['isAssured']))
	    # print("*"*50)
	    # print(json.dumps(res,indent=4))
	    # print("*"*50)
	    row.update(res)

	pd.DataFrame(ch).to_csv("./output/data_v3/cardekho_complete_data.csv")
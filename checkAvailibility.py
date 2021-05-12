# make sure you have python installed and requests library
#  run script with commad python checkAvailibility.py
# This script runs continously and checks for availibility of a slot
# For getting district code
# first goto https://cdn-api.co-vin.in/api/v2/admin/location/states
# then select state_id
# replace the state_id with the value you got from previous request https://cdn-api.co-vin.in/api/v2/admin/location/districts/state_id
# find the district and district code from response and add that in districts
import time
import ctypes
from datetime import datetime,timedelta
import requests
import winsound
import sys,os

#buzzer settings
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
#url for search based on district code or pincode
URL_district = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}'
URL_pincode = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}'
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

# append the centerId which you don't want to get notified for
excluded_center = []#[592292,696996,697093,697052,697630,697293,696972]

# add key value pair by district id as given by top description
districts = {
    "702":"Haridwar",
    "725" : "Kolkata"
}
# add key value pair given by pincode
pincodes = {
    '246149': 'Kotdwar'
}

# this method gets the detail based on district code
def job_district(district_id, district_name, date_string):
    print('for district {} with district Id: {}'.format(district_name,district_id))
    getUrl = URL_district.format(district_id, date_string)
    response_data = requests.get(getUrl, headers=browser_header)
    #print(response_data.json())
    parse_response(district_name, response_data)

# this method gets data based on pincode
def job_pincode(pincode, district_name, date_string):
    print('for district {} with pincode: {}'.format(district_name,pincode))
    getUrl = URL_pincode.format(pincode, date_string)
    response_data = requests.get(getUrl, headers=browser_header)
    parse_response(district_name, response_data)

# parses the json response
def parse_response(district_name, response_data):
    vaccineAvailData = []
    print(response_data.status_code)
    if response_data.status_code == 200:
        data = response_data.json()
        #print(data)
        vaccineAvailData = checkForAvailibility(data)
        print(vaccineAvailData)
    showAvailibility(vaccineAvailData,district_name)

# show message on console
def showAvailibility(vaccineAvailData,district_name):
    if vaccineAvailData:
        for info in vaccineAvailData:
            msg = "{} {} {} {} {} {}\n"
            msg = msg.format(district_name, info.get("centerId"), info.get("centerName"), info.get("pincode"), info.get("date"),  info.get("available")) 
            print(msg)

        if sys.platform.startswith('win'):
            winsound.Beep(frequency, duration)
            MessageBox = ctypes.windll.user32.MessageBoxW
            MessageBox(None, "Slot Found in : "+ district_name, 'Slot Found', 0)
        else:
            os.system('echo -e "\a"')

def checkForAvailibility(data):
    vaccineAvailData = []
    center_data = data.get("centers")
    for center in center_data:
        for session in center.get("sessions"):
            if session.get("min_age_limit")<45 and session.get("available_capacity") > 0:
                if center.get("center_id") not in excluded_center:
                    availableCenter = {}
                    availableCenter = {
                        "centerId" : center.get("center_id"),
                        "centerName" : center.get("name"),
                        "blockName" : center.get("block_name"),
                        "date" : session.get("date"),
                        "pincode" : session.get("pincode"),
                        "available" : session.get("available_capacity")
                    }
                    vaccineAvailData.append(availableCenter)
    return vaccineAvailData


if __name__ == '__main__':
    # max 100 requests per 5 min delay will be automatically calculated
    time_delay = (5*60)/(100/len(districts)+ len(pincodes))
    print('Request checking delay: {}'.format(time_delay))
    while True:
        print('checking : {}'.format(datetime.now()))
        now = datetime.now()
        first_time_string = now.strftime("%d-%m-%Y")
        if districts:
            for district_id, district_name in districts.items():
                job_district(district_id, district_name, first_time_string)
        if pincodes:
            for pincode, district_name in pincodes.items():
                job_pincode(pincode, district_name, first_time_string)
        time.sleep(time_delay)
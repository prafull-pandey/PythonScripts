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
url_getstates = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
url_getdistrict = 'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}'
URL_district = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={0}&date={1}'
URL_pincode = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={0}&date={1}'
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

# append the centerId which you don't want to get notified for
excluded_center = [700370,696884,700368]#[592292,696996,697093,697052,697630,697293,696972]

# add key value pair by district id as given by top description
districts = {
    #"702":"Haridwar",
    #"725" : "Kolkata"
}
# add key value pair given by pincode
pincodes = {
    #'246149': 'Kotdwar',
    #'249205': 'HW2'
}

def clear():
    # check and make call for specific operating system
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

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

def select_state():
    response_data = requests.get(url_getstates, headers=browser_header)
    if response_data.status_code == 200:
        data = response_data.json()
        states = data.get('states')
        for state in states:
            print("{} : {}".format(state.get('state_id'), state.get('state_name')))

    selected_state = input('select state code : ')
    clear()
    select_district(selected_state)

def select_district(state_code):
    response_data = requests.get(url_getdistrict.format(state_code), headers=browser_header)
    if response_data.status_code == 200:
        data = response_data.json()
        districts_data = data.get('districts')
        for district in districts_data:
            print("{} : {}".format(district.get('district_id') ,district.get('district_name')))

        selected_district = input('select district code : ')
        clear()
        selectedDisct = None
        for sub in districts_data:
            if str(sub['district_id']) == selected_district:
                selectedDisct = sub
                break
        districts[selected_district]=selectedDisct.get('district_name')
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
    clear()
    while True:
        print('1 : By district')
        print('2 : By Pincode')
        preference = input('Please select your preference : ')

        if preference == '1':
            select_state()
            break

        elif preference == '2':
            city_name = input('Please input city name : ')
            pincode = input('Please input pincode : ')
            pincodes[pincode]=city_name
            print(pincodes)
            clear()
            break
        else :
            print("Please select correct input")

    # max 100 requests per 5 min delay will be automatically calculated
    lengthdic = len(districts)+ len(pincodes)
    time_delay = (5*60)/(100/lengthdic)
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

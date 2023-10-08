import earthaccess
import os
import math
import h5py
import matplotlib.pyplot as plt
import numpy as np
from opencage.geocoder import OpenCageGeocode
import requests
from pyhdf.SD import SD, SDC
from mpl_toolkits.basemap import Basemap
import pandas as pd
import json
import os
import numpy as np
from pyhdf.SD import SD
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import xarray as xr
import datetime

def getArea(area_bounds, latitude, longitude):
    lon1, lon2, lat1, lat2 = area_bounds

    # Adjust bounds to handle both positive and negative latitude/longitude
    if lat1 < 0 and lat2 < 0:
        lat1, lat2 = lat2, lat1  # Swap lat1 and lat2 for negative latitudes
    if lon1 < 0 and lon2 < 0:
        lon1, lon2 = lon2, lon1  # Swap lon1 and lon2 for negative longitudes

    # Find the indices within the specified area
    lon_indices = np.where((longitude >= lon1) & (longitude <= lon2))
    lat_indices = np.where((latitude >= lat1) & (latitude <= lat2))

    return lon_indices, lat_indices

def pointofMaxVeg(lon_indices,lat_indices,data):


    array1 = lat_indices
    array2 = lon_indices

    # Determine the size difference
    size_diff = len(array1) - len(array2)

    # Fill missing elements with values starting from the last value of the larger array + 1
    if size_diff > 0:
        last_value = array2[-1]
        fill_values = np.arange(last_value + 1, last_value + 1 + size_diff)
        array2 = np.concatenate((array2, fill_values))
    elif size_diff < 0:
        last_value = array1[-1]
        fill_values = np.arange(last_value + 1, last_value + 1 - size_diff)
        array1 = np.concatenate((array1, fill_values))


    dataValues=data[array1[0],array2[0]]
    mazVali=np.argmax(dataValues)
    y=array1[0][mazVali]
    x=array2[0][mazVali]
    return x,y,dataValues[mazVali]
    

def  plotMapWithZoomedRectangle(lon1, lon2, lat1, lat2, data):

 
    # Load your data and create a Basemap object
   
    latitude = np.array(data["HDFEOS"]["GRIDS"]["VIIRS_Grid_16Day_VI_CMG"]['Data Fields']["lat"])
    longitude = np.array(data["HDFEOS"]["GRIDS"]["VIIRS_Grid_16Day_VI_CMG"]['Data Fields']["lon"])
    evi_data = np.array(data["HDFEOS"]["GRIDS"]["VIIRS_Grid_16Day_VI_CMG"]['Data Fields']["CMG 0.05 Deg 16 days EVI"])
    # Create a Basemap object
    m = Basemap(
        projection='cyl',
        resolution='l',
        llcrnrlat=-90,
        urcrnrlat=90,
        llcrnrlon=-180,
        urcrnrlon=180
    )

    # Plot your data using pcolormesh
    x, y = m(longitude, latitude)
    m.pcolormesh(x, y, evi_data)



    # Draw a rectangle on the map

    x_rect, y_rect = m([lon1, lon2, lon2, lon1, lon1], [lat1, lat1, lat2, lat2, lat1])
    plt.plot(x_rect, y_rect, color='red', lw=2)

    # Draw coastlines, parallels, and meridians
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(-90., 120., 30.), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(-180., 181., 45.), labels=[0, 0, 0, 1])

    #draw a point of the higest data value in the area given by the rectangle
    lonx,laty=getArea([lon1,lon2,lat1,lat2],latitude,longitude)

   
    p1lon,p2lat,val=pointofMaxVeg(lonx,laty,evi_data)

    

    x_point, y_point = m(longitude[p1lon], latitude[p2lat])
    plt.plot(x_point, y_point, marker='o', markersize=5, color='blue', label='Max Value')



    

    # Set the zoomed extent
    ax = plt.gca()
    ax.set_xlim(lon1 - 5, lon2 + 5)  # Adjust the range as needed
    ax.set_ylim(lat1 - 5, lat2 + 5)  # Adjust the range as needed

    # Show the map
    plt.show()
    return  longitude[p1lon], latitude[p2lat]



# Get the current date
current_date = datetime.date.today() 
delta_date=datetime.date.today() - datetime.timedelta(days=16)
# Format it as yyyy-mm-dd
current_date = current_date.strftime('%Y-%m-%d')
delta_date = delta_date.strftime('%Y-%m-%d')


key="eb2db0e9b2d74a0ab2848d3b6eba401e"
distance_km=30
import art


os.environ["EARTHDATA_USERNAME"]="alberto432423423"
os.environ["EARTHDATA_PASSWORD"]="wqedaase2q242134fdsfwqeqA!"


auth = earthaccess.login()

lat=0
lon=0

def returnArea(central_lat,central_lon):

    # Earth's radius in kilometers
    earth_radius_km = 6371

    # Approximate degrees per kilometer (latitude and longitude)
    degrees_per_km = 1 / (earth_radius_km * 2 * math.pi / 360)

    # Calculate the offset in degrees for 20 km in both latitude and longitude
    lat_offset = distance_km * degrees_per_km
    lon_offset = distance_km * degrees_per_km / math.cos(math.radians(central_lat))

    # Calculate the coordinates of the corners of the rectangle
    north_lat = central_lat + lat_offset
    south_lat = central_lat - lat_offset
    east_lon = central_lon + lon_offset
    west_lon = central_lon - lon_offset
    return [north_lat,south_lat,east_lon,west_lon]


def defaultLocation():
    url = 'https://ipinfo.io'

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the response content, which contains information about the IP address
        data=json.loads(response.text)
        lon=float(data["loc"].split(",")[0])
        lat=float(data["loc"].split(",")[1])

        return (data["country"]+" " +data["region"] +" "+ data["city"],lon,lat)
def gecoderLocation(x,y):
    geocoder = OpenCageGeocode(key)
    data=geocoder.reverse_geocode(x,y)
    return data[0]["formatted"]




print(art.text2art("Welcome to Buble!", ""))
location=defaultLocation()
lat=location[2]
lon=location[1]
print("Your current location is: '{}' \nUsing default range of {}km \n".format(location[0],distance_km))

# ANSI escape codes for text colors
feelings = {
        '1': "sad",
        '2': "happy",
        '3': "angry",
        '4': "disgusted",
        '5': "fearful"
    }
activities = {
    "Meditate": "Dedicate a few minutes each day to meditate and practice mindfulness. This can help reduce stress and improve your emotional well-being.",
    "Exercise": "Whether it's running, swimming, dancing, or any other activity you enjoy, exercise releases endorphins and makes you feel good.",
    "Go Outside": "Leave your house and take a walk around your city.",
    "Hang Out": "Meet up with friends or family members.",
}

activities2 = {
    "GoTo":"Visit the following location and wear somenthing yellow"
}

feelingsOptions={
        '1': ["Meditate","Exercise","Go Outside","Hang Out"],
        '2': ["Go Outside","Hang Out"],
        '3': ["Meditate","Exercise"],
        '4': ["Go Outside","Hang Out"],
        '5': ["Exercise","Outside","Hang Out"]
}

class TextColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'  # End color

# Function to display the main menu and ask for the user's feeling
def main_menu():
    print(f"{TextColors.HEADER}How are you feeling today?{TextColors.ENDC}")
    print(f"{TextColors.BLUE}1. Sad{TextColors.ENDC}")
    print(f"{TextColors.GREEN}2. Happy{TextColors.ENDC}")
    print(f"{TextColors.YELLOW}3. Angry{TextColors.ENDC}")
    print(f"{TextColors.RED}4. Disgusted{TextColors.ENDC}")
    print(f"{TextColors.BLUE}5. Fearful{TextColors.ENDC}")
    while True:
    
        choice = input(f"Enter the number corresponding to your feeling (or 'exit' to quit): ")
        
        if choice == 'exit':
            exit()
        
        if choice not in ['1', '2', '3', '4', '5']:
            print(f"{TextColors.RED}Invalid choice. Please choose a number from 1 to 5.{TextColors.ENDC}")
        else:       

            return choice

def meet_someone():
    while True:
        response = input("Would you like to meet someone? (y/n): ")
        if response.lower() == 'y':
            print("That sounds like a great idea!")
            return False
        elif response.lower() == 'n':
            print("That's okay. Sometimes we all need some alone time.")
            return True
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# Main program
if __name__ == "__main__":

    choice = main_menu()
    alone = meet_someone()
       

txt=("{} and you want to be {}").format(feelings[choice],"alone" if alone else "in company" )
print(f"{TextColors.GREEN} You are {txt}  {TextColors.ENDC}")

print("Loading...\nOptions to be more {}".format(feelings[choice]))

for action in feelingsOptions[choice]:
    print("\t {}".format(activities[action]))

print("visit the following location:")

#search a sunny location, a warm one, a calm one and one with a lot of vegation withing 20km

area=returnArea(lat,lon)



results = earthaccess.search_data(
    short_name='VNP13C1',
    cloud_hosted=True,
    temporal=(delta_date, current_date),
    count=1
)

results = earthaccess.download(results, "./data")
#open file
x=0
y=0
print("Area of search: {} {} {} {} ".format(area[0], area[1], area[2], area[3]) )
for res in results:
    data=h5py.File("./data/"+res,"r")
    x,y=plotMapWithZoomedRectangle(area[0], area[1], area[3], area[2],data)

data=gecoderLocation(y,x)
print("Your nearest Natural Environment is at: {}".format(data))


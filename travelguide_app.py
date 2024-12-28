import streamlit as st  # Streamlit for creating a web app
from travelplanner import TravelPlanner
import MapDisplay
from streamlit_folium import st_folium
import pandas as pd
import os
import folium

st.title("Hi ! I'm your travel companion")

# Input city
city = st.text_input("City", "Bangkok, Thailand")

# Input number of days of the trip (K)
# The result will be grouped into K groups/clusters)
K = st.text_input("Number of Days of your trip","3")
K = int(K)

# Input hotel/accomodation
hotel = st.text_input("Hotel", "Enter hotel name or address")

# Input airport
airport = st.text_input("Airport", "Donmuang International Airport")


# Multi-select field for activities the user is interested in
activities = st.multiselect(
    "What would you like to do?",  
    ["Tourist attractions", 
     "Shopping destinations", 
     "Local restaurants", 
     "Local dessert place to try", 
     "Family Attractions", 
     "Coffee"],  # Options available for selection
    default=["Tourist attractions"]  # Default selection
)

# Creating a dictionary with all user inputs to be passed to the TravelPlanner
args_dict = {
    "city": city,  # User-inputted city
    "hotel": hotel,  # User-inputted hotel
    "airport": airport,  # User-inputted airport
    "activities": activities,  # User-selected activities
}

st.write(args_dict)
st.write(f"List top ten best {args_dict['activities']} in {args_dict['city']} with their names and brief descriptions.")


# Plan trip when the button is clicked
# otherwise just display the previous result from df_place_cluster.csv (if the file exists)
if st.button('Plan your trip !'):
    # Initializing the TravelPlanner with the user inputs
    tp = TravelPlanner(args_dict)

    # Option 1 : Ask LLM for a list of interesting places
    place_list = tp.Ask_LLM_find_place()
    print(f"output list from LLM {place_list}")

    # call Google Places API to get information about the places on the list
    output = tp.get_Info_for_list(place_list, 'df_place_info.csv')

    
    
    # Option 2 : Use Google Places API text search to find interesting places 
    # output = tp.find_place()


    # Displaying places of interest
    #for index,row in output.iterrows():
    #    st.write(f"## {index + 1}. {row['displayName.text']}")
    #    st.write(f"Place ID: {row['id']}")
    #    st.write(f"Address: {row['formattedAddress']}")
    #    st.write(f"Latitude: {row['location.latitude']}")
    #    st.write(f"Longitude: {row['location.longitude']}")
    #    st.write(f"Average user rating: {row['rating']}")
    #    st.write(f"Rating count: {row['userRatingCount']}")
    #    st.write(f"Website: {row['websiteUri']}")
    
    

    #compute cluster for each place
    place_withcluster = tp.compute_cluster(output, K=K)

    # Add description to each place
    description = []
    for i in range(len(place_withcluster)):
        print(place_withcluster['displayName.text'][i])
        responseLLM = tp.Ask_LLM_find_info(place_withcluster['displayName.text'][i])
        description.append(responseLLM.content)

    # Convert to DataFrame
    df_description = pd.DataFrame(description, columns=['description'])
    places_w_description = pd.concat([place_withcluster, df_description], axis=1, ignore_index = False)    

    # Save to .csv file
    places_w_description.to_csv('df_place_cluster_description.csv', index=False)


    # get info for the user input hotel and airport
    hotel_airport_list = [tp.hotel, tp.airport]
    print('Getting hotel and airport info after perform clustering ------')
    for i in range(len(hotel_airport_list)):
        print(hotel_airport_list[i])
    
    output_hotel = tp.get_Info_for_list(hotel_airport_list, 'hotel_airport_info.csv')

    # Displaying hotel and airport information
    #for index,row in output_hotel.iterrows():
    #    col3.write(f"## {index + 1}. {row['displayName.text']}")
    #    col3.write(f"  {row}")
    


    # Compute route -> ordering stops to visit along the route
    orderred_stops = tp.compute_route(place_withcluster)

    # Displaying places by clusters
    places_output = pd.read_csv("df_place_cluster_description.csv")


    for i in range(K):
        place_cluster_i = pd.read_csv("df_route_"+str(i)+".csv")
        st.write(f"# DAY {i+1}")


        for index,row in place_cluster_i.iterrows():
            placeIndex = row['placeIndex']
            st.write(f"## {index + 1}. {row['placeName']}")
            #st.write(places_output['description'][places_output['placeIndex'] == placeIndex].to_string(index=False))
            st.table(places_output['description'][places_output['placeIndex'] == placeIndex])
            st.write(f"Place Index: {placeIndex}")
            st.write(f"Place ID: {row['placeID']}")
            st.write(f"Address: {places_output['formattedAddress'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
            st.write(f"Average user rating: {places_output['rating'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
            st.write(f"Rating count: {places_output['userRatingCount'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
            st.write(f"Website: {places_output['websiteUri'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
            
    
    # Display stops with numbers on a map
    #center the map at the mean latitude, longtitude from the place_data
    map2 = folium.Map(location=[place_withcluster['location.latitude'].mean(),place_withcluster['location.longitude'].mean()], zoom_start=11, tiles="openstreetmap")
    map2 = MapDisplay.mapDisplay_withnumber(K,map2)
    st_data = st_folium(map2)

else:
    if os.path.exists("df_place_cluster_description.csv") and os.path.exists("df_route_0.csv"):
        print(f"The file df_place_cluster_description.csv and df_route_0.csv exist.")

        places_output = pd.read_csv("df_place_cluster_description.csv")

        # Displaying places by clusters
        for i in range(K):
            place_cluster_i = pd.read_csv("df_route_"+str(i)+".csv")
            st.write(f"# DAY {i+1}")


            for index,row in place_cluster_i.iterrows():
                placeIndex = row['placeIndex']
                st.write(f"## {index + 1}. {row['placeName']}")
                st.table(places_output['description'][places_output['placeIndex'] == placeIndex])
                st.write(f"Place Index: {placeIndex}")
                st.write(f"Place ID: {row['placeID']}")
                st.write(f"Address: {places_output['formattedAddress'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
                st.write(f"Average user rating: {places_output['rating'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
                st.write(f"Rating count: {places_output['userRatingCount'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
                st.write(f"Website: {places_output['websiteUri'][places_output['placeIndex'] == placeIndex].to_string(index=False)}")
            

        # Displaying places from all clusters
        #for index,row in places_output.iterrows():
        #    st.write(f"## {index + 1}. {row['displayName.text']}")
        #    st.write(f"Place ID: {row['id']}")
        #    st.write(f"Address: {row['formattedAddress']}")
        #    st.write(f"Latitude: {row['location.latitude']}")
        #    st.write(f"Longitude: {row['location.longitude']}")
        #    st.write(f"Average user rating: {row['rating']}")
        #    st.write(f"Rating count: {row['userRatingCount']}")
        #    st.write(f"Website: {row['websiteUri']}")
        #    st.write(f"Cluster: {row['cluster']}")
        

        # Display stops with numbers on a map
        #center the map at the mean latitude, longtitude from the place_data
        map2 = folium.Map(location=[places_output['location.latitude'].mean(),places_output['location.longitude'].mean()], zoom_start=11, tiles="openstreetmap")
        map2 = MapDisplay.mapDisplay_withnumber(K,map2)
        st_data = st_folium(map2)
    else:
        print(f"The file df_place_cluster_description.csv or df_route_0.csv does not exist.") 

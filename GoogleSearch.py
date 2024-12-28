import urllib.parse
import urllib.request
import json, re, os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Retrieve the API key from the environment variable
api_key = os.getenv('GOOGLE_API_KEY')
route_api_key = os.getenv('GOOGLE_ROUTE_API_KEY')

def find_place(city, activities):
    # Define the API endpoint
    url = 'https://places.googleapis.com/v1/places:searchText'
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,  # Replace 'API_KEY' with your actual Google Places API key
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.websiteUri,places.location'
    }

    # Define the data payload for the POST request
    data = {
        'textQuery': " ".join(activities) + " in " + city ,
        'pageSize' : 8
        }
    print(f'data to feed find_place = {data}')

    # Convert data to JSON format
    json_data = json.dumps(data)

    # Make the POST request
    response = requests.post(url, headers=headers, data=json_data)

    # try print response
    result_place = response.json()
    print(".........................Hey .....................")
    print(result_place)
    #print(result_place['places'][0])
    #print(result_place['places'][1])

    # Convert JSON data to DataFrame
    df_place = pd.json_normalize(result_place['places'])
    
    # Add 'placeIndex' at the beginning of the dataFrame as the key for future data retrieval
    df_place.insert(loc = 0, column = 'placeIndex', value = range(len(df_place)))

    # Add 'type'
    df_place['type'] = 'Place'

    #save DataFrame to csv file
    df_place.to_csv('df_place.csv', index=False)

    return df_place

def get_placeInfo(place):
    # Define the API endpoint
    url = 'https://places.googleapis.com/v1/places:searchText'
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,  # Replace 'API_KEY' with your actual Google Places API key
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.websiteUri,places.location'
    }

    # Define the data payload for the POST request
    data = {
        'textQuery': place ,
        'pageSize' : 1
        }
    print(f'data to feed places API to get place info = {data}')

    # Convert data to JSON format
    json_data = json.dumps(data)

    # Make the POST request
    response = requests.post(url, headers=headers, data=json_data)

    # try print response
    result_place = response.json()
    print(".........................Hey here is the place info.....................")
    print(result_place)
    
    # Convert JSON data to DataFrame
    df_place = pd.json_normalize(result_place['places'])
    
    # Add 'placeIndex' at the beginning of the dataFrame as the key for future data retrieval
    df_place.insert(loc = 0, column = 'placeIndex', value = range(len(df_place)))

    # Add 'type'
    df_place['type'] = 'Place'

    #save DataFrame to csv file
    df_place.to_csv('one_place_info.csv', index=False)

    return df_place

def get_placeInfo_for_list(place_list, city, file_name):
    # Define the API endpoint
    url = 'https://places.googleapis.com/v1/places:searchText'
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': api_key,  # Replace 'API_KEY' with your actual Google Places API key
        'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.websiteUri,places.location'
    }

    # track number of places that have place info response from Google
    n = 0

    # Define the data payload for the POST request
    for i in range(len(place_list)):
        data = {
            'textQuery': place_list[i]+', '+city,
            'pageSize' : 1
            }
        print(f'from gs.get_placeInfo_for_list data to feed places API to get place info = {data}')

        # Convert data to JSON format
        json_data = json.dumps(data)

        # Make the POST request
        response = requests.post(url, headers=headers, data=json_data)

        # try print response
        result_place = response.json()
        print(".........................Hey here is the place info.....................")
        print(result_place)
        #print(result_place['places'][0])
        #print(result_place['places'][1])

        # Convert JSON data to DataFrame
        if len(result_place) > 0:
            n += 1
            if n == 1:
                df_place = pd.json_normalize(result_place['places'])
                print(f"initialize df_place (n = {n}")
            else:
                df_new = pd.json_normalize(result_place['places'])
                df_place = pd.concat([df_place, df_new], ignore_index = True)
                print(f"append df_place (n = {n}")
        
    # Add 'placeIndex' at the beginning of the dataFrame as the key for future data retrieval
    df_place.insert(loc = 0, column = 'placeIndex', value = range(len(df_place)))

    # Add 'type'
    df_place['type'] = 'Place'

    #save DataFrame to csv file
    df_place.to_csv(file_name, index=False)

    return df_place

def compute_route(df_place,num_cluster,hotelID,hotelName,airportID,airportName):
    
    # Define the API endpoint
    url = 'https://routes.googleapis.com/directions/v2:computeRoutes'
    
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': route_api_key,  # Replace 'API_KEY' with your actual Google Route API key
        #'X-Goog-FieldMask': 'routes,geocodingResults.intermediates.intermediateWaypointRequestIndex'
        'X-Goog-FieldMask':'routes.optimizedIntermediateWaypointIndex'
        #ComputeRoutesResponse.Routes.optimized_intermediate_waypoint_index

    }

    #set start and end points
    startID = hotelID
    startName = hotelName
    endID = hotelID
    endName = hotelName


    # Define the data payload for the POST request
    stops = []
    stops_Index = list(df_place["placeIndex"]) #create a list storing placeIndex of the places of interest
    stops_ID = list(df_place["id"]) #create a list storing placeID of the places of interest
    stops_name = list(df_place["displayName.text"]) #create a list storing names of the places of interest
    stops_lat = list(df_place["location.latitude"]) #create a list storing latitudes of the places of interest
    stops_long = list(df_place["location.longitude"]) #create a list storing longitudes of the places of interest


    for i in range(len(df_place)):
        stops.append(dict(placeId = stops_ID[i]))
        print(f"ID : {stops_ID[i]}  Name : {stops_name[i]}")
    
    data = {
                "origin": {
                    "placeId": startID   #stops_ID[0]
                },
                "destination": {
                    "placeId": endID   #stops_ID[0]
                },
                "intermediates": stops,

                "travelMode": "DRIVE",
                "optimizeWaypointOrder": "true"
            }
    print(f'data to feed compute_route = {data}')
    
    # Convert data to JSON format
    json_data = json.dumps(data)
    print(json_data)

    orderred_stops = []
    # Make the POST request
    response = requests.post(url, headers=headers, data=json_data)
    print(f"response from the POST request ----- {response}")

    # try print response
    orderred_stops = response.json()
    print(".........................Hey orderred stops are below.....................")
    print(orderred_stops)
    print(type(orderred_stops))
    
    #route = a list of stops in recommended order
    
    route = orderred_stops['routes'][0]['optimizedIntermediateWaypointIndex']

    #print result
    print(f"--START PlaceID: {startID}  Name: {startName}")
    
    #save the route in dataFrame
    df_route = pd.DataFrame(columns=['visitOrder', 'placeIndex', 'placeID', 'placeName', 'location.latitude', 'location.longitude'])
    for i in range(len(route)):
        id = route[i]
        print(f"#{i} {id} PlaceID: {stops_ID[id]}  Name: {stops_name[id]}")
        df_route.loc[i, "visitOrder"] = i
        df_route.loc[i, "placeIndex"] = stops_Index[id]
        df_route.loc[i, "placeID"] = stops_ID[id]
        df_route.loc[i, "placeName"] = stops_name[id]
        df_route.loc[i, "location.latitude"] = stops_lat[id]
        df_route.loc[i, "location.longitude"] = stops_long[id]
    
    print("-----------------here is df_route-------")
    print(df_route)
    print("----------------------------------------")
    
    
    print(f"--END PlaceID: {endID}  Name: {endName}")
    
    #save DataFrame to csv file
    df_route.to_csv('df_route_'+num_cluster+'.csv', index=False)

    return df_route

def compute_cluster(place_data, K):
    
    # Read the CSV file
    #place_data = pd.read_csv("df_place.csv")

    X = pd.DataFrame(columns=['placeIndex', 'location.latitude', 'location.longitude'])
    X['placeIndex'] = range(len(place_data))
    X['location.latitude'] = place_data['location.latitude']
    X['location.longitude'] = place_data['location.longitude']

    #K = 3
    kmeans = KMeans(n_clusters = K)

    X['cluster'] = kmeans.fit_predict(X[X.columns[1:3]])
    place_data['cluster'] = X['cluster']
    place_data
    plt.scatter(place_data['location.longitude'], place_data['location.latitude'], c=place_data['cluster'])

    #save DataFrame with cluster numbers to csv file
    place_data.to_csv('df_place_cluster.csv', index=False)

    return place_data

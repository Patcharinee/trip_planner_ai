import folium
import pandas as pd

def mapDisplay(place_data):

    # counting number of clusters from place_data
    K = len(pd.unique(place_data['cluster']))
    
    print("No.of.unique values :", K)
    
    #create cluster dict containing lists of latitude, longitude for each cluster
    cluster={}
    for i in range(K):
        cluster[str(i)] = place_data[['location.latitude','location.longitude','displayName.text','websiteUri']][place_data['cluster'] == i].values.tolist()
    #print(cluster)

    #colors for different clusters
    color = ['blue','green','purple','pink','orange']

    #center the map at the mean latitude, longtitude from the place_data
    map = folium.Map(location=[place_data['location.latitude'].mean(),place_data['location.longitude'].mean()], zoom_start=11, tiles="openstreetmap")
        
    #create points on the map
    for i in range(len(cluster)):
        for j in cluster[str(i)]:
            icone1 = folium.Icon(icon="heart", icon_color="white", color=color[i])
            marker = folium.Marker(location=[j[0],j[1]], popup=folium.Popup(j[2]), icon=icone1)
            marker.add_to(map)
    return  map


def mapDisplay_withnumber(K,map2):
    #colors for different clusters
    color = ['blue','green','purple','pink','orange']

    #display hotel and airport on map
    hotel_airport_output = pd.read_csv("hotel_airport_info.csv")

    #display hotel on map
    icon_hotel = folium.Icon(icon="bed", icon_color="white", color='red', prefix="fa")
    marker = folium.Marker(location=[hotel_airport_output['location.latitude'][0],hotel_airport_output['location.longitude'][0]], popup=folium.Popup(hotel_airport_output['displayName.text'][0]), icon=icon_hotel)
    marker.add_to(map2)

    #display airport on map
    icon_airport = folium.Icon(icon="plane", icon_color="white", color='red', prefix="fa")
    marker = folium.Marker(location=[hotel_airport_output['location.latitude'][1],hotel_airport_output['location.longitude'][1]], popup=folium.Popup(hotel_airport_output['displayName.text'][1]), icon=icon_airport)  
    marker.add_to(map2)


    for i in range(K):
        place_cluster_i = pd.read_csv("df_route_"+str(i)+".csv")
        #create points on the map
        for index,row in place_cluster_i.iterrows():
            #print(row['visitOrder'])
            #print(row['placeName'])
            #print(row['location.latitude'])
            #print(row['location.longitude'])
            icone1 = folium.Icon(icon=str(row['visitOrder']+1), icon_color="white", color=color[i], prefix="fa")
            marker = folium.Marker(location=[row['location.latitude'],row['location.longitude']], popup=folium.Popup(row['placeName']), icon=icone1)
            marker.add_to(map2)
    return  map2
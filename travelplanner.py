from dotenv import load_dotenv
import os, json
import requests
import GoogleSearch as gs
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class TravelPlanner():
    """
    TravelPlanner is a class designed to create a travel plan based on user inputs such as city,
    activities. It helps group the interesting places to visit based on the number of days of the trip and
    provide suggested order to visit the places.

    """
    def __init__(self, args_dict):
        """
        Initializes the TravelPlanner with the given arguments.

        Args:
            args_dict (dict): A dictionary containing travel details 
        """
        
        load_dotenv()
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o'

        self.city = args_dict.get("city")
        self.hotel = args_dict.get("hotel")
        self.airport = args_dict.get("airport")
        self.activities = args_dict.get("activities")
        
    def find_place(self):
        df_place = gs.find_place(self.city, self.activities)
        return df_place
    
    def Ask_LLM_find_place(self):
        # Define the output structure
        class Attraction(BaseModel):
            name: str = Field(description="Name of the attraction")
            description: str = Field(description="Brief description of the attraction")

        class AttractionList(BaseModel):
            attractions: List[Attraction] = Field(description="List of top attractions in Osaka")

        # Set up the output parser
        parser = PydanticOutputParser(pydantic_object=AttractionList)

        # Create a prompt template
        prompt = PromptTemplate(
            template="List top ten best {subject} in {city} with their names and brief descriptions.\n{format_instructions}\n",
            input_variables=["subject","city"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        # Initialize the OpenAI LLM
        model = ChatOpenAI(temperature=0)

        # Generate the response

        chain = prompt | model | parser
        response = chain.invoke({"subject": self.activities,"city": self.city})

        # Convert to list
        attractions_list = []
        attractions_description = []
        for attraction in response.attractions:
            attractions_list.append(attraction.name)
            attractions_description.append(attraction.description)

        # print the lists
        print(len)
        for i in range(len(response.attractions)):
            print(attractions_list[i])
            print(f"    {attractions_description[i]}")

        place_list = attractions_list
        
        return place_list
    
    def Ask_LLM_find_info(self,place_name):
        
        # Create a prompt template
        prompt = PromptTemplate(
            template="provide brief description of {place_name} in {city} for first-time visitor including why it is popular and fun fact (if any).",
            input_variables=["place_name","city"],)

        # Initialize the OpenAI LLM
        model = ChatOpenAI(temperature=0)

        # Generate the response

        chain = prompt | model
        response = chain.invoke({"place_name": place_name,"city": self.city})
        
        return response
    

    def get_placeInfo(self):
        df_place = gs.get_placeInfo(self.city)
        return df_place
    
    def get_Info_for_list(self, place_list, file_name):
        df_place = gs.get_placeInfo_for_list(place_list, self.city, file_name)
        return df_place
    
    def compute_route(self, place_data):
        
        hotel_airport_output = pd.read_csv("hotel_airport_info.csv")
        hotelID = hotel_airport_output['id'][0]
        hotelName = hotel_airport_output['displayName.text'][0]
        airportID = hotel_airport_output['id'][1]
        airportName = hotel_airport_output['displayName.text'][1]
        #for index,row in hotel_airport_output.iterrows():
        #    col3.write(f"## {index + 1}. {row['displayName.text']}")
        #    col3.write(f"  {row}")
        
        # counting number of clusters from place_data
        K = len(pd.unique(place_data['cluster']))
        print(f"number of clusters = {K}")

        for i in range(K):
            print(f"Cluster {i}:")
            place_cluster = place_data[place_data['cluster'] == i]
            print(place_cluster['displayName.text'])
            if len(place_cluster) > 1:
                print(f"len = {len(place_cluster)} -> plan route")
                orderred_stops = gs.compute_route(place_cluster,str(i),hotelID,hotelName,airportID,airportName)
            else:
                print(f"len = {len(place_cluster)} no need to plan route (length <= 1)")
                df = place_cluster[['placeIndex','id','displayName.text','location.latitude','location.longitude']]
                df.rename(columns = {'id':'placeID'}, inplace = True)
                df.rename(columns = {'displayName.text':'placeName'}, inplace = True)
                df.insert(loc = 0, column = 'visitOrder', value = 0)
                df.to_csv('df_route_'+str(i)+'.csv', index=False)

        return orderred_stops
    
    def compute_cluster(self, place_data, K):
        place_withcluster = gs.compute_cluster(place_data, K)
        return place_withcluster

## This AI Trip Planner helps users create customized travel itineraries based on three main inputs:
- Destination city
- Activities/attractions of interest
- Number of days for the trip

## It works by:
- Gather points of interest based on user preferences by using LLM.
- Organizing nearby points of interest into groups (clusters) - one group per day of travel by using K-means clustering algorithm.
- Creating an optimized route for visiting locations within each daily group by using Google Route API.
- Plotting the results on Folium map.

This helps travelers easily and efficiently plan their daily activities while maximizing their time at each destination.

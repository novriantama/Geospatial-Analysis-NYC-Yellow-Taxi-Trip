# Geospatial Analysis NYC Yellow Taxi Trip

## Project Background
This project analyzes the NYC Yellow Cab trip data, a publicly available dataset provided by the New York City Taxi and Limousine Commission (TLC). This dataset contains detailed information about millions of individual taxi trips within New York City, including:   

Trip timestamps: Pickup and dropoff dates and times.   
Location data: Pickup and dropoff locations, often specified by taxi zones.   
Trip distance: The distance covered during the trip.   
Fare information: Fare amount, payment type, and any additional charges.   
Passenger count: The number of passengers on the trip.

This rich dataset offers valuable insights into urban mobility patterns, traffic dynamics, and passenger behavior within a major metropolitan area.  By applying data analysis and visualization techniques, we can extract meaningful information from this raw data to address specific questions and challenges faced by taxi services and city planners.   

## Problem Statement
Taxi services need to optimize their operations and improve customer satisfaction by understanding  passenger demand and accessibility patterns. This requires the ability to:
- Identify high-demand areas: Where are the most frequent pickup and dropoff locations? Are there any spatial patterns or hotspots that emerge?
- Assess location accessibility: How easy is it to reach various locations by taxi, considering travel time and distance?

By addressing these questions, taxi services can make data-driven decisions regarding fleet management, route optimization, and service area expansion.

## Tools and Technologies
- **Docker**: For container management
- **Python**: Main programming language
- **Apache Spark**: For ETL Processing
- **Apache Airflow**: For scheduling and orchestration
- **BigQuery**: For data storage and querying
- **Looker**: For data visualization

## How to install
1. Clone this repo.
2. Run `make download-data`
3. Unzip nyc yellow cab data and place it to data folder
4. Run `make docker-build`
5. Run `make docker-compose`
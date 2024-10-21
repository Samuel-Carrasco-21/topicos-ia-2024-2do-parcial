from random import randint
from datetime import date, datetime
from llama_index.core.tools import QueryEngineTool, FunctionTool, ToolMetadata
from ai_assistant.rags import TravelGuideRAG
from ai_assistant.prompts import travel_guide_qa_tpl, travel_guide_description
from ai_assistant.config import get_agent_settings
from ai_assistant.models import (
    TripReservation,
    TripType,
    HotelReservation,
    RestaurantReservation,
    ReservationType,
)
from ai_assistant.utils import save_reservation
import json

SETTINGS = get_agent_settings()

travel_guide_tool = QueryEngineTool(
    query_engine=TravelGuideRAG(
        store_path=SETTINGS.travel_guide_store_path,
        data_dir=SETTINGS.travel_guide_data_path,
        qa_prompt_tpl=travel_guide_qa_tpl,
    ).get_query_engine(),
    metadata=ToolMetadata(
        name="travel_guide", description=travel_guide_description, return_direct=False
    ),
)

def reserve_flight(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    A flight ticket needs to be reserved, taking into account the following input parameters:

    - date_str: Travel date (string, in ISO format)
    - departure: Departure point
    - destination: Destination point

    The result must be an object of type TripReservation:
    - TripReservation: An object containing the details of the reservation.
    """

    min_price = 300
    max_price = 2000
    print(f"Making flight reservation from {departure} to {destination} on date: {date_str}")
    reservation = TripReservation(
        trip_type=TripType.flight,
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(min_price, max_price),
        reservation_type=ReservationType.TripReservation,
    )

    save_reservation(reservation)
    return reservation

def reserve_bus(date_str: str, departure: str, destination: str) -> TripReservation:
    """
    A bus ticket needs to be reserved, taking into account the following input parameters:

    - date_str: Travel date (string, in ISO format)
    - departure: Departure city
    - destination: Destination city

    The result must be an object of type TripReservation:
    - TripReservation: An object containing the details of the reservation.
    """

    min_price = 200
    max_price = 600
    print(f"Making bus reservation from {departure} to {destination} on date: {date_str}")
    reservation = TripReservation(
        trip_type=TripType.bus,  # Fixed from flight to bus
        departure=departure,
        destination=destination,
        date=date.fromisoformat(date_str),
        cost=randint(min_price, max_price),
        reservation_type=ReservationType.TripReservation,
    )

    save_reservation(reservation)
    return reservation

def reserve_restaurant(reservation_time_str: str, restaurant: str, city: str, dish: str = None) -> RestaurantReservation:
    """
    A restaurant table reservation is required, taking into account the following input parameters:

    - reservation_time_str: Reservation time (string, in ISO format)
    - restaurant: Restaurant name
    - city: City where the restaurant is located
    - dish: Name of the dish (optional or None)

    The result must be an object of type RestaurantReservation:
    - RestaurantReservation: An object containing the details of the restaurant reservation.
    """

    min_price = 20
    max_price = 300
    print(f"Making restaurant reservation at {restaurant} in {city} at {reservation_time_str}")
    reservation = RestaurantReservation(
        reservation_time=datetime.fromisoformat(reservation_time_str),
        restaurant=restaurant,
        city=city,
        dish=dish,
        cost=randint(min_price, max_price),
        reservation_type=ReservationType.RestaurantReservation,
    )

    save_reservation(reservation)
    return reservation

def reserve_hotel(checkin_date_str: str, checkout_date_str: str, hotel_name: str, city: str) -> HotelReservation:
    """
    A hotel room reservation is required, taking into account the following input parameters:

    - checkin_date_str: Check-in date (string, in ISO format)
    - checkout_date_str: Check-out date (string, in ISO format)
    - hotel_name: Hotel name
    - city: City where the hotel is located

    The result must be an object of type HotelReservation:
    - HotelReservation: An object containing the details of the reservation.
    """

    min_price = 100
    max_price = 1000
    print(f"Making hotel reservation at {hotel_name} in {city} from {checkin_date_str} to {checkout_date_str}")
    reservation = HotelReservation(
        checkin_date=date.fromisoformat(checkin_date_str),
        checkout_date=date.fromisoformat(checkout_date_str),
        hotel_name=hotel_name,
        city=city,
        cost=randint(min_price, max_price),
        reservation_type=ReservationType.HotelReservation,
    )

    save_reservation(reservation)
    return reservation

def process_reservations(reservations):
    """
    This function, process reservations, organizing by city and date, calculating the total cost.
    """
    extract_city = lambda r: r.get('city', r.get('destination'))
    extract_date = lambda r: r.get('date') or r.get('checkin_date') or r.get('reservation_time')

    activities_by_city = {}
    for reservation in reservations:
        city = extract_city(reservation)
        date = extract_date(reservation)
        if city not in activities_by_city:
            activities_by_city[city] = []
        activities_by_city[city].append({
            'type': reservation.get('reservation_type'),
            'date': date,
            'details': reservation
        })
    
    return activities_by_city

def give_activity(activity) -> tuple[str, int]:
    activity_type = activity['type']
    details = activity['details']
    cost = details.get('cost', 0)
    
    gotten_activity = ""

    if activity_type == ReservationType.TripReservation.value:
        trip_type = details.get('trip_type', 'Unknown')
        gotten_activity = f"- Trip by {trip_type} from {details['departure']} to {details['destination']}, Cost: ${cost}\n;"
    elif activity_type == ReservationType.HotelReservation.value:
        gotten_activity = f"- Hotel reservation, {details['hotel_name']} from {details['checkin_date']} to {details['checkout_date']}, Cost: ${cost}\n;"
    elif activity_type == ReservationType.RestaurantReservation.value:
        gotten_activity = f"- Restaurant reservation, {details['restaurant']} at {details['reservation_time']}, Cost: ${cost}\n;"
    
    return (gotten_activity, cost)

def format_summary(activities_by_city) -> str:
    """
    This function, format the summary based on organized reservations.
    """
    summary_lines = []
    total_cost = 0

    for city, activities in activities_by_city.items():
        summary_lines.append(f"**City: {city}**\n")
        
        given_activities = map(give_activity, sorted(activities, key=lambda x: x['date']))
        
        for activity_summary, cost in given_activities:
            summary_lines.append(activity_summary)
            total_cost += cost

    summary_lines.append(f"**Total Trip Cost: ${total_cost}**\n")
    return ''.join(summary_lines)

def update_trip_data(reservations):
    """
    This function replaces the data in the trip.json file with the provided reservations.
    """
    try:
        with open(SETTINGS.log_file, 'w') as file:
            json.dump(reservations, file, indent=4)
    except Exception as e:
        print(f"Error updating trip data: {e}")

def get_trip_summary() -> str:
    """
    A detailed summary of the trip must be generated based on the reservations,
    producing a string that summarizes the entire trip. The summary should include
    all reserved activities along with their costs. It should provide information
    such as the destination and departure cities, the dates of arrival and return,
    a breakdown of costs, and more.
    """
    try:
        with open(SETTINGS.log_file, 'r') as file:
            reservations = json.load(file)
        
        if not reservations:
            return "No reservations found for the trip."
        
        activities_by_city = process_reservations(reservations)
        summary = format_summary(activities_by_city)
        
        update_trip_data(reservations)
        
        return summary
    
    except FileNotFoundError:
        return "The trip log file (trip.json) wasn't found."
    except json.JSONDecodeError:
        return "Error while reading the trip log file."

travel_guide_tool = FunctionTool.from_defaults(fn=get_trip_summary, return_direct=False)
flight_tool = FunctionTool.from_defaults(fn=reserve_flight, return_direct=False)
bus_tool = FunctionTool.from_defaults(fn=reserve_bus, return_direct=False)
restaurant_tool = FunctionTool.from_defaults(fn=reserve_restaurant, return_direct=False)
hotel_tool = FunctionTool.from_defaults(fn=reserve_hotel, return_direct=False)

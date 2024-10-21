from fastapi import FastAPI, Depends, Query
from llama_index.core.agent import ReActAgent
from ai_assistant.agent import TravelAgent
from ai_assistant.models import AgentAPIResponse, TripReservation, HotelReservation, RestaurantReservation
from ai_assistant.tools import (
    reserve_bus,
    reserve_flight,
    reserve_hotel,
    reserve_restaurant,
    get_trip_summary,
)

def get_agent() -> ReActAgent:
    return TravelAgent().get_agent()


app = FastAPI(title="AI Agent")


@app.get("/recommendations/places")
def recommend_places(
    city: str,
    notes: list[str] = Query(None),
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend places to visit in {city} based on these notes: {notes}" if notes else f"Recommend places to visit in {city}"
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))


@app.get("/recommendations/hotels")
def recommend_hotels(
    city: str,
    notes: list[str] = Query(None),
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend hotels in {city} based on these notes: {notes}" if notes else f"Recommend hotels in {city}"
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))


@app.get("/recommendations/activities")
def recommend_activities(
    city: str,
    notes: list[str] = Query(None),
    agent: ReActAgent = Depends(get_agent)
):
    prompt = f"Recommend activities to do in {city} based on these notes: {notes}" if notes else f"Recommend activities in {city}"
    response = agent.chat(prompt)
    return AgentAPIResponse(status="OK", agent_response=str(response))


@app.post("/reservations/flight")
def reserve_flight_api(
    date: str,
    departure: str,
    destination: str
):
    reservation = reserve_flight(date, departure, destination)
    return reservation


@app.post("/reservations/bus")
def reserve_bus_api(
    date: str,
    departure: str,
    destination: str
):
    reservation = reserve_bus(date, departure, destination)
    return reservation


@app.post("/reservations/hotel")
def reserve_hotel_api(
    checkin_date: str,
    checkout_date: str,
    hotel: str,
    city: str
):
    reservation = reserve_hotel(checkin_date, checkout_date, hotel, city)
    return reservation


@app.post("/reservations/restaurant")
def reserve_restaurant_api(
    reservation_time: str,
    restaurant: str,
    city: str,
    dish: str = None
):
    reservation = reserve_restaurant(reservation_time, restaurant, city, dish)
    return reservation


@app.get("/trip/report")
def trip_report(agent: ReActAgent = Depends(get_agent)):
    response = get_trip_summary()
    return AgentAPIResponse(status="OK", agent_response=str(response))

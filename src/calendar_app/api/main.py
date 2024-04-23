from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import icalendar

from typing import List
from collections import defaultdict
from datetime import datetime
import bisect


class CalEvent(BaseModel):
    summary: str
    dtstart: datetime
    dtend: datetime


class TimeRange(BaseModel):
    dtstart: datetime
    dtend: datetime


class ClientAgentPair(BaseModel):
    client_id: str
    agent_id: str


event_data = defaultdict(lambda: defaultdict(list))


# Load test data before the app starts.
for i, cal_filepath in enumerate(["./data/test_calendar0.ics", "./data/test_calendar1.ics"]):
    with open(cal_filepath, 'r') as cal_file:
        cal = icalendar.Calendar.from_ical(cal_file.read())

        print(f'Number of events ({i}): {len(cal.walk('VEVENT'))}\n', flush=True)

        # Make up a client and an agent.
        client_id, agent_id = str(i), str(i)

        for raw_event in cal.walk('VEVENT'):
            event = CalEvent(
                summary=raw_event.get("SUMMARY"),
                dtstart=raw_event.get("DTSTART").dt,
                dtend=raw_event.get("DTEND").dt,
            )
            event_data[client_id][agent_id].append(event)

        print(event_data, flush=True)


# Start the app.
app = FastAPI(title="Calendar App")


# Note: The datetimes are sent as strings in this format: '2024-04-23T15:00:00+00:00'
@app.get("/check/")
async def check(client_id: str, agent_id: str, time_range: TimeRange) -> bool:
    agent_events = event_data[client_id][agent_id]
    for event in agent_events:
        if \
                (time_range.dtstart >= event.dtstart and time_range.dtstart <= event.dtend) or \
                (time_range.dtend >= event.dtstart and time_range.dtend <= event.dtend):
            return False
    return True


@app.post("/query/")
async def query(client_id: str, agent_id: str, time_ranges: List[TimeRange]) -> List[CalEvent]:
    ret = []
    agent_events = event_data[client_id][agent_id]
    for event in agent_events:
        for query_range in time_ranges:
            if event.dtstart >= query_range.dtstart and event.dtend <= query_range.dtend:
                ret.append(event)
    return ret


@app.post("/schedule/")
async def schedule(client_id: str, agent_id: str, event: CalEvent) -> CalEvent:
    if not await check(client_id, agent_id, TimeRange(dtstart=event.dtstart, dtend=event.dtend)):
        raise HTTPException(500, "Tried to schedule an appointment at an unavailable time.")
    agent_events = event_data[client_id][agent_id]
    agent_events.append(event)
    return event


@app.post("/coordinate/")
async def coordinate(agents: List[ClientAgentPair], limit_range: TimeRange) -> List[TimeRange]:
    cutpoints = [(limit_range.dtstart, True), (limit_range.dtend, False)]

    agent_events_list = [event_data[agent.client_id][agent.agent_id] for agent in agents]

    for agent_events in agent_events_list:
        for event in agent_events:
            bisect.insort(cutpoints, (event.dtstart, False))
            bisect.insort(cutpoints, (event.dtend, True))

    num_current_appts = 0
    prev_dtstart = limit_range.dtstart
    ret = []
    for point in cutpoints[1:]:
        if point[1] is False:
            if num_current_appts == 0:
                ret.append(TimeRange(dtstart=prev_dtstart, dtend=point[0]))
            num_current_appts += 1
        else:
            num_current_appts -= 1
            if num_current_appts == 0:
                prev_dtstart = point[0]
    return ret


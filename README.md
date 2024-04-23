
# Homework

To run this app, simply execute `docker-compose up`! It'll then be running at http://localhost:8000

Navigate to http://localhost:8000/docs to manually send API requests.


## The Schedule Endpoint

When the `/schedule/` endpoint is called, it should attempt to add the requested event to the data store. The question is what to do if the requested timeslot is not available.

Some options:

1. Simply add an overlapping event
2. Return False, None, empty Event, etc...
3. Throw an HTTPException

The first option might be reasonable (after all, the user is requesting it; maybe it's okay for events to overlap). However, given the overarching focus on checking for event compatibility in the app so far, I think it makes most sense to go with option three.
Given a little more time, it could make sense to add a flag to allow or disallow overlapping events (it wouldn't take long, but I'm running out of dev time :) )
Finally, of course, in real life it is best to ask the client what they think.


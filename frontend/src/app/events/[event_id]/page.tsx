// TODO: Implement events list page
// [Extension: Events]
// GET /events/{event_id} - get list of events
// PATCH /events/{event_id} - update event
// POST /events/{event_id}/subscribe - subscribe to an event
// POST /events/{event_id}/unsubscribe - unsubscribe from an event
// GET /events/{event_id}/members - get list of members of an event

interface EventPageProps {
    params: {
        event_id: string;
    };
}

export default function EventPage({params}: EventPageProps) {
    // TODO: Fetch event using params.event_id
    return <div>Event {params.event_id}</div>;
}
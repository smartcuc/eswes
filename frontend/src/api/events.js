//##
//
//##

export async function fetchEvents() {
    const res = await fetch("http://127.0.0.1:8000/api/v1/events/");
    if (!res.ok) throw new Error("Failed to fetch events");
    return res.json();
}
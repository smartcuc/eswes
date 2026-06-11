//##
//
//##

export async function fetchEvents() {
    const res = await fetch("/api/v1/events/");
    if (!res.ok) throw new Error("Failed to fetch events");
    return res.json();
}
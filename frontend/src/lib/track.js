export async function trackEvent(event, metadata = {}) {
    try {
        await fetch("/api/track/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
                event,
                metadata,
            }),
        });
    } catch (err) {
        console.error("Tracking failed", err);
    }
}
export async function apiFetch(url: string) {
    const res = await fetch(`/api/tracking${url}`, {
        credentials: "include",
    })

    if (!res.ok) {
        throw new Error("API Error")
    }

    return res.json()
}

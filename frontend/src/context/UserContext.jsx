// src/context/UserContext.jsx

import { createContext, useContext, useState, useEffect } from "react";

const UserContext = createContext();

export function UserProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    async function loadUser() {
        try {
            const res = await fetch("/api/auth/me/", {
                credentials: "include",
            });

            if (!res.ok) throw new Error();

            const data = await res.json();
            setUser(data);
        } catch (err) {
            setUser(null);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadUser();
    }, []);

    return (
        <UserContext.Provider value={{ user, loading, refreshUser: loadUser }}>
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    return useContext(UserContext);
}
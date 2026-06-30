/*
# src/hooks/useUserPreference.js
*/

import { useEffect, useRef, useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "../api/client";

export default function useUserPreference(key) {

    const readyRef = useRef(false);

    const query = useQuery({
        queryKey: ["user-preference", key],
        queryFn: () => apiFetch(`/api/user-settings/${key}/`),
    });

    const [value, setLocalValue] = useState({});

    useEffect(() => {

        if (!query.isSuccess) {
            return;
        }

        setLocalValue(query.data?.value ?? {});

        readyRef.current = true;

    }, [
        query.isSuccess,
        query.data,
    ]);

    const setValue = useCallback(
        async (nextValue) => {

            setLocalValue(nextValue);

            if (!readyRef.current) {
                return;
            }

            await apiFetch(`/api/user-settings/${key}/`, {
                method: "PATCH",
                body: JSON.stringify({
                    value: nextValue,
                }),
            });
        },
        [key]
    );

    return {
        ...query,
        value,
        isReady: query.isSuccess,
        setValue,
    };
}

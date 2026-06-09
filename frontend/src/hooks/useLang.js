/*
# src/hooks/useLang.js
*/

import { useState } from "react";

export function useLang() {
    const [lang, setLang] = useState("de");

    return { lang, setLang };
}


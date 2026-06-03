✅ ✅ 1. Grundprinzip
Du hast jetzt 3 Typen von SQL:


DateiTypVerhalten
001_timescale.sqlMigration⚠️ nur 1x ausführen
002_dirty_pipeline.sqlStruktur + Trigger✅ idempotent
003_indexes.sqlOptimierung✅ idempotent

🚨 ❗ 2. Wichtig: NICHT alles jedes Mal laufen lassen
❌ FALSCH
Shellpsql -f 001_timescale.sqlpsql -f 002_dirty_pipeline.sqlpsql -f 003_indexes.sqlWeitere Zeilen anzeigen
→ jedes Mal ❌

✅ ✅ Richtig
🟢 1. 001_timescale.sql
👉 nur einmal ausführen
Das ist eine Migration:
SQLSELECT create_hypertable(...)Weitere Zeilen anzeigen
❗ Wenn du das nochmal ausführst → ERROR

🟢 2. 002_dirty_pipeline.sql
👉 kannst du immer ausführen ✅
weil:
SQLCREATE TABLE IF NOT EXISTSCREATE OR REPLACE FUNCTIONDROP TRIGGER IF EXISTSWeitere Zeilen anzeigen
👉 idempotent ✔

🟢 3. 003_indexes.sql
👉 kannst du auch immer ausführen ✅
weil:
SQLCREATE INDEX IF NOT EXISTSWeitere Zeilen anzeigen

✅ ✅ 3. Wie du es richtig im Projekt benutzt

🧱 Initial Setup (einmalig)
Shellpsql -f sql/001_timescale.sqlpsql -f sql/002_dirty_pipeline.sqlpsql -f sql/003_indexes.sqlWeitere Zeilen anzeigen

🔄 Danach (bei Deploy / Updates)
Shellpsql -f sql/002_dirty_pipeline.sqlpsql -f sql/003_indexes.sqlWeitere Zeilen anzeigen
👉 KEIN 001 mehr

# Refaktoryzacja WUP — podsumowanie i plan kontynuacji (2026-08-29)

Status: **watch-path ulepszony i wdrożony na c2004**; poniżej rejestr zmian,
ujętych w commitach `a5c4faf` i `d92d9be`, plus niezacommitowane poprawki
higieny testów i bugfix `default_event_store`.

## Co zostało zrobione

### 1. Watch path (commit a5c4faf)
- **Event-level debounce** w `WupWatcher.on_file_change`: kaskada zdarzeń
  watchdog z jednego zapisu edytora agreguje się per serwis w oknie debounce
  (5 szybkich zapisów → 1 quick test zamiast 5). Flush przez
  `_flush_pending_events()` w pętli watch.
- **`wup/realtime_anomalies.py`** (nowy moduł):
  - `LatencyTracker` — rolling p95/median baseline per endpoint; flaguje
    spadki ≥3x mediany przy progach min_samples=8, absolute_floor=50 ms.
  - `ChangeBurstDetector` — wykrywa patologiczne burze zdarzeń
    (≥120 eventów/10 s per serwis) → komunikat „runaway generator / sync loop".
- **Concurrent HTTP probes** — `ThreadPoolExecutor` (8 workerów) w
  `run_quick_test`; latencja zapisywana do `LatencyTracker`; anomalia
  raportowana przez `planfile_reporter` ze statusem degraded (stage
  `probe-latency`).
- **Offline drift w watch path** — `AnomalyDetector` (hash/AST/YAML) podpięty
  lazy w `_scan_drift()`; high/critical findings otwierają ticket planfile
  (service=drift, stage=anomaly). Wcześniej martwy kod — istniał, ale nie był
  importowany nigdzie w watch flow.
- Testy dostosowane do nowej semantyki debounce (jawny flush w 2 testach).

### 2. Runtime hygiene (commit d92d9be)
- **`wup health`** — komenda CLI zwracająca JSON-snapshot stanu watchera;
  `--since` (transitions inkrementalne), `--failed-only`, exit code 0/1/2/3
  wg severity. Jeden komendowy interfejs dla agenta po jego zmianie.
- **EventStore rotation** — 5 MB live + 5 MB archive (wcześniej bez limitu;
  log c2004 urósł do 28 MB od kwietnia).
- Watcher c2004 działa jako persistent user unit `c2004-wup-watch.service`.

### 3. Niezacommitowane (do szybkiego commita)
- **Bugfix `default_event_store`** (`packages/dsl2wup/src/dsl2wup/events.py`):
  store dziedziczył ścieżkę manifestu w CWD, ignorując katalog manifestu →
  każdy test wołający `dispatch()` appendował do `app.doql.events.pb`
  w katalogu repo (349 KB, rosnąca, śledzona w gicie). Fix: ścieżka = katalog
  manifestu + stem. Wymusiło to podpięcie `default_file` w 5 plikach testów.
- **Nowe testy** `tests/test_realtime_anomalies.py` — 12 testów pokrywających
  LatencyTracker / ChangeBurstDetector / integrację debounce z watcherem.
- **Cleanup importów** w `realtime_anomalies.py` (ruff F401).

### 4. Wdrożenie na c2004
- Wheel zreinstalowany do `/home/tom/github/maskservice/c2004/.venv`
  (instalacja kopiowa, nie editable — wymaga reinstalacji po każdej zmianie).
- Watcher zrestartowany; live test: zmiana pliku → `📝 1 change(s) debounced →
  Service: backend` → Quick TestQL passed. Logi czyste, brak Drift/Latency
  false-positive na komentarzu.

## Plan kontynuacji refaktoryzacji

### Krok 1 — hygiena repo (natychmiast, 15 min)
1. Zacommitować niezacommitowane zmiany:
   `fix(events): event store follows manifest dir; isolate test event logs`
2. Dodać `app.doql.events.pb` do `.gitignore` (artefakt runtimeowy) —
   albo usunąć z gita (`git rm --cached`), jeśli nie jest snapshotem bazy.
   Sprawdzić pochodzenie w git log zanim zostanie usunięty.
3. Zabić ręczny watch z IDE (PID z JetBrains scope) dublujący unit systemd.

### Krok 2 — pokrycie testami nowego kodu (1 h)
- Test `run_quick_test` z ThreadPoolExecutor: mock endpointów o znanych
  latencjach → asercja na `LatencyTracker.record` i degraded status.
- Test `_scan_drift`: plik z AST zmianą → asercja planfile ticket (service=drift).
- Property-based test LatencyTracker: sekwencje monotoniczne nigdy nie flagują.

### Krok 3 — refaktoryzacja core.py (2–4 h)
`wup/core.py` ma ~1100 linii i miesza warstwy. Podział:
- `watch_loop.py` — pętla, debounce, flush, cooldown
- `probes.py` — HTTP probes, ThreadPoolExecutor, latencja
- `drift.py` — integracja AnomalyDetector z planfile
- `core.py` — WupWatcher jako fasada komponująca powyższe
Wzorem podziału todocs: `article.py` 560L → `article_sections.py`.

### Kroki 4+ — dalsze kierunki (szkic)
- **Metryki watchera** — licznik eventów/s, rozmiar kolejki, czas quick testu;
  eksponowane w `wup health` JSON.
- **LatencyTracker per-scenario** — baseline dla endpointów TestQL osobno od
  probes; obecnie wspólny.
- **Adaptive debounce** — debounce_seconds skalowany burst_detector state
  (burst → wydłuż okno zamiast jednorazowego alertu).
- **TestQL scenariusze w CI** — smoke scenario per serwis w GitHub Actions;
  obecnie tylko lokalnie.
- **todocs** (osobny podprojekt) — kandydat na kolejną sesję: spójność
  badge'ów wersji w README, przeterminowane metryki w „Project Status".

## Stan testów
- 372/372 pass (353 wup + 19 dsl2wup), ruff clean.
- `app.doql.events.pb` nietknięta przez suite (weryfikowane md5 przed/po).

## Environment
- Watcher: `systemctl --user status c2004-wup-watch.service`
- Live test: `printf '\n# x\n' >> backend/firmware/config.py` w c2004 →
  journalctl pokazuje debounce + Quick TestQL.
- Instalacja c2004: kopiowa (pip install z path), wymaga reinstalacji po
  zmianach źródłowych.

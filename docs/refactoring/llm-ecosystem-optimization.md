---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "llm-ecosystem-optimization",
  "kind": "refactoring-plan",
  "version": 1,
  "title": "Optymalizacja rozwoju wspomaganego LLM",
  "status": "proposed",
  "owner": "semcod/wup maintainers",
  "created": "2026-09-15",
  "updated": "2026-09-15",
  "review_after": "2026-10-15",
  "source_revision": "e3ac729038a1f6c0c0425e40700f8fc3aaf12919",
  "affected_repositories": [
    "semcod/wup"
  ],
  "evidence": [
    "repo://semcod/wup@e3ac729038a1f6c0c0425e40700f8fc3aaf12919#koru.yaml",
    "repo://semcod/wup@e3ac729038a1f6c0c0425e40700f8fc3aaf12919#wup.yaml",
    "repo://semcod/wup@e3ac729038a1f6c0c0425e40700f8fc3aaf12919#wup/planfile_reporter.py",
    "github://semcod/wup/issues/10"
  ]
}
---

# Plan refaktoryzacji: Optymalizacja rozwoju wspomaganego LLM

<!-- docs:section goal -->
## Goal

Skrócić czas od wykrycia problemu do zweryfikowanej decyzji bez osłabiania
testów, bezpieczeństwa sterowania ani niezależności publikacji. Rezultatem ma
być jeden wiarygodny incident dla jednego sygnału, szybka ścieżka walidacji i
odtwarzalny kontekst dla kolejnej sesji agenta.

<!-- docs:section current_state -->
## Current state

WUP ma automatyczne zgłaszanie awarii do Planfile, Koru prowadzi skanowanie
backlogu, a dokumentacja zawiera częściową adopcję polityki lokalnego CI.
Podczas sesji jeden timeout TestQL utworzył dwa otwarte tickety, PLF-091 i
PLF-092. Konfiguracja Koru deklaruje wymaganie sukcesu CI, lecz uniwersalny
skrypt jakości wypisuje ostrzeżenie po błędzie testu, więc nie jest bramą
fail-closed. Profil OneDev dla WUP pozostaje częściowy, co opisuje PLF-088.

<!-- docs:section scope -->
## Scope

Plan obejmuje WUP, jego konfigurację TestQL i Planfile oraz kontrakty
integracyjne używane przez Koru i Goal. Wprowadza dokumentację kanoniczną,
deduplikację incydentów, klasyfikację wyników i propozycję rozdzielenia
sterowania StackNet od telemetryki. Zależne systemy sprzętowe pozostają
własnością swoich repozytoriów; WUP dokumentuje tylko wymagane kontrakty.

<!-- docs:section non_goals -->
## Non goals

Plan nie zatwierdza merge'a, wdrożenia, zmian sprzętowych ani skanowania całej
sieci. Nie zastępuje lokalnego Validatora ani reguł OneDev. Nie przenosi
Wellmanifest do zależności runtime WUP i nie traktuje dokumentacji jako dowodu
działającego CI.

<!-- docs:section evidence -->
## Evidence

Podstawą są konfiguracje Koru i WUP oraz implementacja PlanfileReporter w
rewizji wskazanej w metadanych. Otwarty ticket PLF-089, opublikowany jako
GitHub issue 10, rejestruje konieczność uregulowania Wellmanifest, lifecycle
ticketów i dowodów lokalnego CI. Track timeoutu TestQL wskazuje ten sam plik
śladu dla PLF-091 oraz PLF-092. Te obserwacje pokazują problem procesu; nie
dowodzą jeszcze pojedynczej przyczyny błędu deduplikacji.

<!-- docs:section target_design -->
## Target design

Sterowanie, telemetryka i diagnostyka są rozdzielone. Kontroler StackNet
otrzymuje zweryfikowany program ruchu oraz komendy start/stop i jest zegarem
cyklu. GUI oraz LLM nie znajdują się na ścieżce czasowej ruchu; odbierają
asynchroniczne potwierdzenia i telemetrię.

WUP nadaje każdemu sygnałowi stabilny fingerprint: repozytorium, usługa, etap,
typ wyniku, hash scenariusza i znormalizowany podpis błędu. Zapis rejestru jest
atomowy. Automatyczny ticket zaczyna w stanie triage; do GitHub trafia dopiero
po klasyfikacji i oznaczeniu approved_for_sync. Ticket wskazuje ten dokument,
a nie kopiuje pełnego planu.

<!-- docs:section migration -->
## Migration

1. Naprawić bramę Koru tak, aby wymagany błąd testu dawał niezerowy kod
   wyjścia; niewykonalny krok klasyfikować jako blocked_environment.
2. Dodać atomowy rejestr fingerprintów i testy konkurencyjnych zgłoszeń,
   restartu, recovery oraz błędu synchronizacji.
3. Zredukować PLF-091 i PLF-092 do jednego incidentu po odtworzeniu
   fingerprintu; zachować bezpieczną referencję do receiptu.
4. Dodać lifecycle triage i approved_for_sync do Planfile/WUP, a synchronizację
   GitHub ograniczyć do dopuszczonych ticketów.
5. Zdefiniować w repozytorium właściciela StackNet kontrakt programu ruchu,
   zdarzeń potwierdzenia i budżetu opóźnienia.
6. Rozszerzyć lokalny profil Validator/OneDev zgodnie z PLF-088, z testem
   dokładnego head, base i merge result.
7. Aktualizować ten dokument przy każdej zmianie znaczenia planu i zwiększać
   jego wersję.

<!-- docs:section acceptance -->
## Acceptance

- Ten sam otwarty sygnał nie tworzy więcej niż jednego ticketu.
- Każdy wymagany krok jakości kończy się błędem procesu, gdy test nie przeszedł.
- Ticket publikowany do GitHub ma fingerprint, kryteria akceptacji, dedupe-key
  i adres dokumentu kanonicznego.
- Start, stop oraz przejście kierunku ruchu nie czekają na polling diagnostyczny.
- Receipt walidacji zawiera head, base, merge result, macierz i digest
  środowiska.
- Plan pozostaje odnajdywalny przez indeks dokumentacji i Planfile.

<!-- docs:section validation -->
## Validation

Walidacja dokumentacji uruchamia przypięty checker wellmanifest/docs z
dostarczonym standard_revision i deliverables. Zmiany WUP wymagają task
test:root, task lint oraz odpowiedniej ścieżki workspace lub TestQL. Kontrakt
deduplikacji wymaga testów jednostkowych i testu równoległych zgłoszeń.
Kontrakt sprzętowy wymaga testów integracyjnych na symulatorze oraz osobnego
pomiaru na zatwierdzonym urządzeniu.

<!-- docs:section rollback -->
## Rollback

Zmiany procesu są odwracalne przez wyłączenie automatycznej publikacji GitHub i
pozostawienie ticketów w triage. Zmiana fingerprintu obsługuje poprzedni
format rejestru przez migrację odczytu; w razie problemu nowy zapis można
wyłączyć bez utraty istniejących ticketów. Sterowanie sprzętem ma lokalny,
bezpieczny stop niezależny od GUI i automatyzacji.

<!-- docs:section risks -->
## Risks

Nadmiernie szeroki fingerprint ukryje różne awarie, a zbyt wąski nadal będzie
tworzył szum. Zmiana fail-closed może ujawnić wcześniej maskowane awarie
środowiska i czasowo wydłużyć kolejkę. Automatyczne wykrywanie urządzeń bez
listy zaufania zwiększa ryzyko niewłaściwego celu. Te ryzyka ograniczają testy
kontraktowe, triage i stopniowe canary.

<!-- docs:section ownership -->
## Ownership

Utrzymanie dokumentu i integracji WUP/Planfile należy do semcod/wup
maintainers. Planfile odpowiada za kontrakt synchronizacji issue, Koru i Goal
za przygotowanie kontekstu oraz receipts, a właściciel StackNet za wykonanie
programu ruchu i bezpieczeństwo kontrolera. Publikacja i merge pozostają w
procesie chronionego lokalnego CI.

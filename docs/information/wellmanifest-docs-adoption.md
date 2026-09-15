---
{
  "schema": "wellmanifest.docs/document/v1",
  "id": "wellmanifest-docs-adoption",
  "kind": "information",
  "version": 1,
  "title": "Adopcja wellmanifest/docs w WUP",
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
    "https://github.com/wellmanifest/docs/blob/ebe7501063ef4f3e63ded610c2d3183010ca636e/docs/standard/POLICY.md",
    "github://semcod/wup/issues/10",
    "repo://semcod/wup@e3ac729038a1f6c0c0425e40700f8fc3aaf12919#AGENTS.md"
  ]
}
---

# Informacja: Adopcja wellmanifest/docs w WUP

<!-- docs:section purpose -->
## Purpose

Ustalić trwałe miejsce dla analiz, planów refaktoryzacji i decyzji, aby nowa
sesja agenta mogła odnaleźć wynik poza czatem, katalogiem roboczym lub
pojedynczym ticketem.

<!-- docs:section scope -->
## Scope

WUP przyjmuje układ, metadane oraz lokalną walidację standardu wellmanifest/docs
0.1.1. Dotyczy to nowych i modyfikowanych rezultatów dostarczanych od tej
adopcji. Dokumenty historyczne są migrowane przy kolejnej zmianie merytorycznej.

<!-- docs:section evidence -->
## Evidence

Przypięcie znajduje się w .governance/docs.json i wskazuje immutable revision
ebe7501063ef4f3e63ded610c2d3183010ca636e oraz hash polityki. PLF-089 określa
potrzebę lifecycle ticketów i trwałego dowodu walidacji. Lokalnie odczytano
policy, template refactoring-plan i checker z dokładnie tej rewizji.

<!-- docs:section content -->
## Content

Dokumenty trwałe należą do docs/information, analizy do docs/analysis, plany
refaktoryzacji do docs/refactoring, a decyzje do docs/decisions. Każdy dokument
ma stabilny id, JSON metadata, oznaczone sekcje oraz wpis w docs/README.md.
Ticket Planfile przechowuje ograniczoną intencję i link do dokumentu
kanonicznego. Katalog project/ticket-id, chat, cache i katalog tymczasowy nie
są jedynym miejscem wyniku.

<!-- docs:section limitations -->
## Limitations

Profil standardu domyślnie jest przeznaczony dla subactor/*, a WUP jest
repozytorium semcod/*. Ta adopcja jest świadomym, kompatybilnym użyciem
struktury i checkera, lecz nie oznacza wdrożonej chronionej bramy OneDev.
Checker potwierdza format, miejsce i tracking Git, ale nie prawdziwość treści
ani sukces wdrożenia. Stan deployed i verified pozostaje osobną pracą PLF-088
oraz PLF-089.

<!-- docs:section next_actions -->
## Next actions

Dodać checker do istniejącego lokalnego profilu Validator/OneDev po canary,
bez tworzenia osobnego GitHub workflow. Powiązać nowe tickety refaktoryzacyjne
z dokumentami kanonicznymi i aktualizować indeks oraz version podczas zmiany
ustaleń.

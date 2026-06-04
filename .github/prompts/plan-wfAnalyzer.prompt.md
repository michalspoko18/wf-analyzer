## Plan: wf-analyzer

Aplikacja składa się z 3 serwisów Docker Compose: **collector** (Python, scraper + agregacja), **api** (FastAPI) i **frontend** (SvelteKit). Zewnętrzna baza PostgreSQL — bez serwisu `db` w compose.

---

### Faza 1: Fundament

1. Struktura katalogów projektu + `docker-compose.yml` (3 serwisy, wspólny `.env`)
2. `db/init.sql` — tworzenie schematu + seed 3 siłowni
3. Rozbudowanie `example.env` o `DB_URL`, `WF_LOGIN`, `WF_PASSWORD`

### Faza 2: Collector (Python)

4. `collector/auth.py` — logowanie do WellFitness (POST `/Auth/Login`), zarządzanie sesją (cookies + JWT), automatyczny re-auth przy 401
5. `collector/fetcher.py` — GET `/GetMembersInClubs`, filtrowanie do 3 siłowni po `ClubName`
6. `collector/aggregator.py` — przeliczanie `gym_occupancy_hourly` i `gym_occupancy_daily` z raw samples (UPSERT per `dow` + `hour`)
7. `collector/main.py` — pętla co 5 min (APScheduler), osobny job agregacji co godzinę
8. `Dockerfile` + `requirements.txt` dla collectora

### Faza 3: API (FastAPI)

9. `api/database.py` — połączenie asyncpg, pool
10. `api/routers/gyms.py` — `GET /api/gyms`, `GET /api/gyms/{id}/current`
11. `api/routers/occupancy.py` — `GET /api/gyms/{id}/history?from=&to=`, `/hourly`, `/daily`
12. `api/routers/analytics.py` — `GET /api/analytics/best-times` (ranking najcichszych godzin per siłownia)
13. `Dockerfile` + `requirements.txt` dla API

### Faza 4: Frontend (SvelteKit)

14. Inicjalizacja projektu SvelteKit + konfiguracja proxy do API
15. `CurrentOccupancy.svelte` — ostatni pomiar z auto-odświeżaniem co 5 min
16. `HistoryChart.svelte` — wykres liniowy (Chart.js / LayerCake)
17. `Heatmap.svelte` — heatmapa tygodniowa (godzina × dzień tygodnia)
18. `GymComparison.svelte` — 3 siłownie obok siebie
19. `Recommendations.svelte` — top 5 najcichszych godzin
20. `Dockerfile` dla frontendu

### Faza 5: Integracja

21. Finalny `docker-compose.yml` z health-checks i depends_on
22. Weryfikacja end-to-end

---

**Relevant files**

- `example.env` — uzupełnić o `DB_URL`
- `db/init.sql` — schemat i seed
- `collector/auth.py` — kluczowy: obsługa cookies + JWT z `httpx`

**Schemat bazy**

| Tabela                  | Klucz główny                       |
| ----------------------- | ---------------------------------- |
| `gyms`                  | `id`                               |
| `gym_occupancy_samples` | `id` (gym_id + measured_at indeks) |
| `gym_occupancy_hourly`  | `(gym_id, dow, hour)`              |
| `gym_occupancy_daily`   | `(gym_id, dow)`                    |

> `dow` = dzień tygodnia (0=pon … 6=nd), co pozwala na rekomendacje "wtorek o 7 rano jest najciszej"

**Verification**

1. `docker compose up` — collector loguje się i za 5 min wstawia pierwszy rekord do `gym_occupancy_samples`
2. Po godzinie `gym_occupancy_hourly` ma dane
3. Frontend pokazuje aktualne obłożenie dla 3 siłowni
4. `GET /api/analytics/best-times` zwraca ranking

**Decisions**

- Backup: pominięty na razie
- Brak serwisu `db` w compose — łączymy do zewnętrznego PostgreSQL przez `DATABASE_URL`
- Agregacja per `(dow, hour)` zamiast per konkretna data — lepsze dla rekomendacji "najlepszego czasu w tygodniu"

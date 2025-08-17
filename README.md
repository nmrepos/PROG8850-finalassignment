# PROG8850 — Final Assignment

**End-to-End Automated Database Management with CI/CD, Validation & Admin UI**

This repository operationalizes a simple but disciplined database lifecycle: bring up MySQL locally with Adminer, create and evolve the `ClimateData` schema, seed data, validate, and pressure-test with concurrent reads/writes. A GitHub Actions pipeline ties it together so every push runs the same choreography headlessly.

---

* **Local services**: MySQL + Adminer (docker-compose)
* **Schema management**: Create DB, create table, migrate (add `humidity`), seed data
* **Validation**: SQL checks to confirm structure + counts
* **Test harness**: Python script to run concurrent INSERT/SELECT/UPDATE
* **CI/CD**: GitHub Actions workflow replicates local flow in CI
* **Docs**: Pipeline/implementation notes included
* **License**: MIT)

---

## 🗂️ Repository Map & Why Each Exists

```
.
├─ .devcontainer/                # Codespaces/devcontainer config (consistent local env)
├─ .github/workflows/            # CI/CD: GitHub Actions workflow(s)
├─ migrations/                   # (Optional) extra SQL migration artifacts
├─ scripts/
│  └─ multi_thread_queries.py    # Concurrency test: INSERT/SELECT/UPDATE under load
├─ sql/
│  ├─ 01_create_database.sql     # Creates database (e.g., project_db)
│  ├─ 02_create_climate_table.sql# Creates ClimateData table
│  ├─ 03_add_humidity_column.sql # Evolves schema (add humidity)
│  ├─ 04_seed_data.sql           # Seeds sample rows
│  └─ 05_validation.sql          # Post-migration/data validation queries
├─ IMPLEMENTATION_REPORT.md      # Build/run notes (implementation POV)
├─ PIPELINE_DOCUMENTATION.md     # CI pipeline documentation
├─ mysql-adminer.yml             # docker-compose: MySQL + Adminer UI
├─ up.yml / down.yml             # Ansible playbooks to bring infra up/down locally
├─ schema_changes.sql            # Inline schema driver for CI step(s)
├─ test_pipeline.sh              # Local all-in test runner (orchestrates the flow)
├─ requirements.txt              # Python deps for scripts/*
├─ signoz.py                     # (Optional) Observability glue (SigNoz integration)
└─ README.md                     # Project overview (original)
```

> Filenames and layout are taken directly from the repo listing. 

---

## 🏗️ Data Model (Authoritative)

**Table: `ClimateData`**

| column          | type         | constraints                  | description             |
| --------------- | ------------ | ---------------------------- | ----------------------- |
| `record_id`     | INT          | PRIMARY KEY, AUTO\_INCREMENT | Unique row id           |
| `location`      | VARCHAR(100) | NOT NULL                     | Where it was recorded   |
| `record_date`   | DATE         | NOT NULL                     | When it was recorded    |
| `temperature`   | FLOAT        | NOT NULL                     | °C                      |
| `precipitation` | FLOAT        | NOT NULL                     | mm                      |
| `humidity`      | FLOAT        | NOT NULL                     | % (added via migration) |

> Schema listed in the repo’s README. ([GitHub][1])

---

## ⚙️ Prerequisites

* **Docker** (and Docker Compose)
* **Python 3.10+**
* **GitHub account** (to run CI)
* **`mysql` client** (optional but handy)

---

## 🚀 Quick Start (Local, Recommended)

1. **Start MySQL + Adminer**

```bash
docker compose -f mysql-adminer.yml up -d
```

> Brings up a MySQL service and Adminer UI locally. 
2. **Run the full local pipeline**

```bash
./test_pipeline.sh
```

> Exercises create → migrate → seed → validate → concurrency steps.

3. **Log in to the DB**

```bash
mysql -h 127.0.0.1 -u root -pSecret5555 project_db
```

> Default local creds and DB from the project README.

4. **Open Adminer**
   Visit `http://localhost:8080`
   Server: `db` • User: `root` • Password: `Secret5555` (admin UI for quick checks) 

---

## 🧪 Run Just the Concurrency Test

Install Python deps then run the script:

```bash
python -m pip install -r requirements.txt
python scripts/multi_thread_queries.py
```

The script will insert, read (multi-threaded), and update rows against the MySQL service started by docker-compose.

> The repo README summarizes “multi-threaded query execution” as part of the pipeline.

---

## 🤖 CI/CD (GitHub Actions)

On every push/PR to `main`, the pipeline:

1. **Bootstraps environment** (MySQL + dependencies)
2. **Applies schema** (create DB/table)
3. **Migrates** (adds `humidity`)
4. **Seeds** data (sample climate rows)
5. **Runs concurrent tests** (SELECT/INSERT/UPDATE threads)
6. **Validates** outcome (schema + data checks)

> These steps are enumerated in the repo’s README “GitHub Actions Pipeline” section.

### CI environment variables

The example step uses these defaults if secrets are not set:

```yaml
DB_HOST: ${{ secrets.DB_HOST || '127.0.0.1' }}
DB_ADMIN_USER: ${{ secrets.DB_ADMIN_USER || 'root' }}
DB_PASSWORD: ${{ secrets.DB_PASSWORD || 'Secret5555' }}
DB_NAME: ${{ secrets.DB_NAME || 'mysql' }}
```

> Defaults are documented in the README’s “Notes” block. In practice the workflow creates/uses `project_db` afterward. 

---

## 💻 Local “act” Option (Run CI Locally)

If you prefer to simulate the GitHub Actions run locally:

```bash
bin/act           # try this first
bin/act -P ubuntu-latest=-self-hosted   # fallback if the first fails
```

> The README notes using `act` for local CI emulation. 

---

## 🧩 Optional: Submodule (Infra)

To align with course infra guidance, you may add the referenced infra repo as a submodule:

```bash
git submodule add https://github.com/rhildred/docker-infra
git submodule update --init --recursive
```

> Instruction to add `docker-infra` is stated explicitly in the README.

---

## 🧰 File-by-File Execution Notes

* **`mysql-adminer.yml`**
  Docker Compose file that stands up MySQL and Adminer. Run with:

  ```bash
  docker compose -f mysql-adminer.yml up -d
  docker compose -f mysql-adminer.yml logs -f  # follow logs if needed
  docker compose -f mysql-adminer.yml down     # stop
  ```

  Use Adminer at `http://localhost:8080` as a sanity UI.

* **`sql/01_create_database.sql`**
  Creates the working database (e.g., `project_db`). Execute with:

  ```bash
  mysql -h 127.0.0.1 -u root -pSecret5555 < sql/01_create_database.sql
  ```

* **`sql/02_create_climate_table.sql`**
  Creates `ClimateData` with the base columns (no `humidity` yet).

* **`sql/03_add_humidity_column.sql`**
  Evolves the schema by adding the `humidity` column (migration).

* **`sql/04_seed_data.sql`**
  Inserts sample rows for quick testing and pipeline determinism.

* **`sql/05_validation.sql`**
  Runs consistency checks (counts, non-nulls, structure guards).

> The series of SQL files is described in the README’s project structure. Apply each with `mysql -e` or via the pipeline. 

* **`schema_changes.sql`**
  Convenience driver for CI to apply schema/migration in one go (used in the documented CI step). 

* **`scripts/multi_thread_queries.py`**
  Python harness that spins up threads to do INSERT/SELECT/UPDATE, surfacing race/locking/config issues early.

  ```bash
  python scripts/multi_thread_queries.py
  ```

* **`test_pipeline.sh`**
  Local “single-button” run that mirrors CI: spin services, apply schema/migration, seed, validate, then exercise concurrency.

  ```bash
  chmod +x test_pipeline.sh
  ./test_pipeline.sh
  ```

* **`up.yml` / `down.yml`**
  Simple Ansible playbooks to bring infra up/down if you prefer Ansible over raw compose.

  ```bash
  ansible-playbook up.yml
  ansible-playbook down.yml
  ```

* **`.github/workflows/…`**
  The GitHub Actions workflow that implements the CI steps listed above. Triggered on push/PR to `main`. 

---

## 🧪 Manual Checks (Spot-Verify)

```bash
# How many rows after seeding?
mysql -h 127.0.0.1 -u root -pSecret5555 project_db -e "SELECT COUNT(*) FROM ClimateData;"

# Has 'humidity' landed?
mysql -h 127.0.0.1 -u root -pSecret5555 project_db -e "SHOW COLUMNS FROM ClimateData LIKE 'humidity';"

# Exercise the Python harness
python scripts/multi_thread_queries.py
```

---

## 🧯 Troubleshooting Playbook

**Containers won’t start**

* `docker compose -f mysql-adminer.yml ps` and `... logs` to see MySQL init.
* If port **3306** or **8080** are busy, stop conflicting services or map alternative ports in the compose file.

**Auth failures connecting to MySQL**

* Use the documented defaults: host `127.0.0.1`, user `root`, password `Secret5555`.
* When using `Adminer`, set **Server** to `db` (the service name), not `localhost`. 

**`project_db` doesn’t exist**

* Run `sql/01_create_database.sql` explicitly or rerun `./test_pipeline.sh`.
* Verify with:

  ```bash
  mysql -h 127.0.0.1 -u root -pSecret5555 -e "SHOW DATABASES LIKE 'project_db';"
  ```

**`humidity` column missing**

* Apply `sql/03_add_humidity_column.sql` or rerun the pipeline.
* Confirm with:

  ```bash
  mysql -h 127.0.0.1 -u root -pSecret5555 project_db -e "DESCRIBE ClimateData;"
  ```

**Python script errors (deps)**

* Reinstall dependencies:

  ```bash
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

**GitHub Actions cannot connect to DB**

* In CI, set secrets if you’re not using defaults: `DB_HOST`, `DB_ADMIN_USER`, `DB_PASSWORD`, `DB_NAME`.
* If using service containers in CI, ensure MySQL is healthy before running SQL (add a wait-for-mysql step).

**Running CI locally with `act` fails**

* Try `bin/act` first; if images mismatch, use `-P ubuntu-latest=-self-hosted` as documented.

**Adminer shows but login fails**

* Use `Server: db` (service name), `root` / `Secret5555`.
* If you changed compose names or ports, update those values accordingly.

---



```bash
docker compose -f mysql-adminer.yml down
# or
ansible-playbook down.yml
```

> Both methods are noted in the README.

---

## 🔐 License

MIT. See `LICENSE`. ([GitHub][1])

---


[1]: https://github.com/nmrepos/PROG8850-finalassignment "GitHub - nmrepos/PROG8850-finalassignment"

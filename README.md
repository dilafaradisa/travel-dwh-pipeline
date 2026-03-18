# Building ELT Pipeline for Pactravel Data Warehouse

This project was created as part of the assignment from Pacmann.ai. In this project, I act as a data engineer responsible for building an ELT pipeline for a travel booking platform, PacTravel. In this scenario, PacTravel wants to build a Data Warehouse to support its growing analytical needs — specifically to track daily booking volumes and monitor average ticket prices over time. In this repository, I will focus on developing the ELT pipeline.

---

## 1. Requirements

* **OS** :
  + Linux
  + WSL (Windows Subsystem For Linux)
  + macOS

* **Tools** :
  + DBeaver
  + Docker
  + Cron

* **Programming Language** :
  + Python
  + SQL

* **Python Library** :
  + Luigi
  + Pandas
  + SQLAlchemy
  + python-dotenv

* **Transformation** :
  + dbt (data build tool)
  + dbt-utils
  + dbt-date
  + dbt-constraints

---

## 2. Architecture


### Data Warehouse Design

The warehouse uses a **star schema** dimensional model with:

**Dimension Tables**
| Table | SCD Type | Description |
|---|---|---|
| `dim_date` | Static | Date dimension seeded via dbt |
| `dim_customers` | Type 2 | Customer details |
| `dim_hotels` | Type 2 | Hotel details |
| `dim_airlines` | Type 1 | Airline details |
| `dim_aircrafts` | Type 1 | Aircraft details |
| `dim_airports` | Type 1 | Airport details |

**Fact Tables**
| Table | Type | Description |
|---|---|---|
| `fct_flight_booking` | Transaction Fact | One row per individual flight booking |
| `fct_hotel_booking` | Transaction Fact | One row per individual hotel booking |
| `fct_daily_flight_summary` | Periodic Snapshot | Daily aggregated flight booking metrics per airline |
| `fct_daily_hotel_summary` | Periodic Snapshot | Daily aggregated hotel booking metrics per hotel |

---

## 3. Preparations


* **Create and activate virtual environment** :

  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/macOS
  venv\Scripts\activate     # Windows
  ```

* **Install requirements** :

  ```bash
  pip install -r requirements.txt
  ```

* **Create `.env` file** in project root directory :

  ```
  # Source DB 
  SRC_POSTGRES_DB=...
  SRC_POSTGRES_HOST=...
  SRC_POSTGRES_USER=...
  SRC_POSTGRES_PASSWORD=...
  SRC_POSTGRES_PORT=...

  # DWH DB
  DWH_POSTGRES_DB=...
  DWH_POSTGRES_HOST=...
  DWH_POSTGRES_USER=...
  DWH_POSTGRES_PASSWORD=...
  DWH_POSTGRES_PORT=...

  # Directory
  DIR_ROOT_PROJECT=...     # <project_dir>
  DIR_TEMP_LOG=...         # <project_dir>/pipeline/temp/log
  DIR_TEMP_DATA=...        # <project_dir>/pipeline/temp/data
  DIR_LOAD_QUERY=...       # <project_dir>/pipeline/src_query/load
  DIR_LOG=...              # <project_dir>/logs/
  DIR_DBT_TRANSFORM=...    # <project_dir>/pactravel_dbt_
  ```

* **Configure and run Docker** :

  ```bash
  docker compose up -d
  ```

---

## 4. Building the Pipeline

### Create Schema for the Database

Set up schemas, tables, and attributes according to the dimensional model design:

+ [Source database schema](./helper/source_init/init.sql)
+ Target database:
  - [Staging schema (pactravel)](./helper/dwh_init/dwh-staging-schema.sql)
  - [Final schema (final)](./helper/dwh_init/dwh-final-schema.sql)

### Create Utility Functions

Several utility functions support the orchestration process:

+ [Database connector](./pipeline/utils/db_connect.py) : Functions to connect to source and DWH databases.
+ [SQL file reader](./pipeline/utils/read_sql.py) : Function to read SQL query files and return as strings.

### Create ELT Tasks with Luigi

**[ExtractData](./pipeline/extract.py)**

The `ExtractData` task extracts all tables from the PacTravel source database (`aircrafts`, `airlines`, `airports`, `customers`, `hotel`, `flight_bookings`, `hotel_bookings`) and saves them temporarily as CSV files. The outputs of this task are CSV files for each table, a task summary with status and execution time (`extract_summary_<date>.csv`), and a log file.

**[LoadData](./pipeline/load.py)**

The `LoadData` task loads the extracted CSV files into the DWH `pactravel` staging schema as-is. Before loading, all tables are truncated to ensure no duplicate data. The outputs of this task are a task summary (`load_summary_<date>.csv`) and a log file.

**[Transform](./pipeline/transform.py)**

The `Transform` task runs dbt to transform data from the staging schema into the final dimensional model. It executes `dbt deps`, `dbt seed`, `dbt run`, `dbt snapshot`, and `dbt test` sequentially. The outputs of this task are a task summary (`transform_summary_<date>.csv`) and a log file.

### Compile Tasks

All tasks are compiled into a single main script:

```bash
python elt_main.py
```

Example output logs and task summaries:

**Logs**

![log file](./img/pactravel-logs.png)

**Task Summary**

![task summary](./img/pactravel-task-summary.png)

---

## 5. Scheduling with Cron

The pipeline is scheduled to run daily at 2 AM:

```bash
# crontab -e
0 2 * * * cd <project_dir> && source venv/bin/activate && python elt_main.py >> logs/cron.log 2>&1
```

---

## 6. Results

After running the full pipeline, the following tables are available in the final schema:

**Sample Query — Daily Booking Volume**
```sql
SELECT
    dd.full_date,
    fds.total_bookings,
    fds.total_revenue
FROM fct_daily_flight_summary fds
JOIN dim_date dd ON fds.date_id = dd.date_id
ORDER BY dd.full_date DESC
LIMIT 30;
```

**Sample Query — Average Ticket Price Over Time**
```sql
SELECT
    dd.year,
    dd.month,
    da.airline_name,
    fds.avg_ticket_price,
    LAG(fds.avg_ticket_price) OVER (
        PARTITION BY fds.airline_id
        ORDER BY dd.full_date
    ) AS prev_avg_price
FROM fct_daily_flight_summary fds
JOIN dim_date dd ON fds.date_id = dd.date_id
JOIN dim_airlines da ON fds.airline_id = da.airline_id
ORDER BY da.airline_name, dd.year, dd.month;
```

# PROG8850 Final Assignment - End-to-End Automated Database Management

## Project Overview
This project implements a comprehensive CI/CD pipeline for automated database management with advanced monitoring and performance optimization using GitHub Actions, MySQL, and Python-based concurrent testing.

## 🚀 Key Features
- **Automated CI/CD Pipeline**: Complete GitHub Actions workflow for database deployment
- **Schema Management**: Automated table creation and migration (adding humidity column)
- **Concurrent Testing**: Multi-threaded INSERT, SELECT, and UPDATE operations
- **Comprehensive Validation**: Data integrity and performance verification
- **Security Best Practices**: GitHub Secrets integration with local development support

## 📊 Database Schema

### ClimateData Table Structure:
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| record_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| location | VARCHAR(100) | NOT NULL | Recording location |
| record_date | DATE | NOT NULL | Date of measurement |
| temperature | FLOAT | NOT NULL | Temperature in °C |
| precipitation | FLOAT | NOT NULL | Precipitation in mm |
| humidity | FLOAT | NOT NULL | Humidity percentage |

## 🔧 Quick Start

### Local Development Setup
1. **Start MySQL Service:**
   ```bash
   docker compose -f mysql-adminer.yml up -d
   ```

2. **Run Complete Pipeline Test:**
   ```bash
   ./test_pipeline.sh
   ```

3. **Access Database:**
   ```bash
   mysql -h 127.0.0.1 -u root -pSecret5555 project_db
   ```

4. **View Admin Interface:**
   - Navigate to http://localhost:8080
   - Server: `db`, User: `root`, Password: `Secret5555`

### GitHub Actions Pipeline
The CI/CD pipeline automatically executes on push/PR to main branch:
1. **Environment Setup** - MySQL service + dependencies
2. **Schema Deployment** - Database and table creation
3. **Schema Update** - Add humidity column
4. **Data Seeding** - 25 sample climate records
5. **Concurrent Testing** - Multi-threaded query execution
6. **Validation** - Comprehensive verification

## 📁 Project Structure
```
├── .github/workflows/
│   └── ci_cd_pipeline.yml          # Main CI/CD pipeline
├── sql/
│   ├── 01_create_database.sql      # Database creation
│   ├── 02_create_climate_table.sql # Initial schema
│   ├── 03_add_humidity_column.sql  # Schema migration
│   ├── 04_seed_data.sql           # Sample data
│   └── 05_validation.sql          # Validation queries
├── scripts/
│   └── multi_thread_queries.py    # Concurrent testing
├── .secrets                       # Local environment config
├── test_pipeline.sh              # Local testing script
└── requirements.txt               # Python dependencies
```

## 🧪 Testing Results
✅ **33 Concurrent Operations** completed successfully:
- 10 INSERT operations
- 15 SELECT operations (2 threads)
- 8 UPDATE operations
- 0 errors

## 📋 Manual Testing
```bash
# Test individual components
mysql -h 127.0.0.1 -u root -pSecret5555 project_db -e "SELECT COUNT(*) FROM ClimateData;"
python3 scripts/multi_thread_queries.py
```

## 🔒 Security
- GitHub Secrets for production credentials
- Local `.secrets` file for development (gitignored)
- Secure MySQL connection handling

## 📈 Performance Metrics
- Pipeline execution: ~2-3 minutes
- Concurrent query testing: ~1.1 seconds
- Database operations: Real-time logging and monitoring

---

Add https://github.com/rhildred/docker-infra as a submodule to this and follow the instructions on eConestoga. 

## Notes

```bash
ansible-playbook up.yml
```

To use mysql:

```bash
mysql -u root -h 127.0.0.1 -p
```

To run github actions like (notice that the environment variables default for the local case):

```yaml
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Install MySQL client
        run: sudo apt-get update && sudo apt-get install -y mysql-client

      - name: Deploy to Database
        env:
          DB_HOST: ${{ secrets.DB_HOST || '127.0.0.1' }} 
          DB_USER: ${{ secrets.DB_ADMIN_USER || 'root' }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD  || 'Secret5555'}}
          DB_NAME: ${{ secrets.DB_NAME || 'mysql' }}
        run: mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < schema_changes.sql
```

locally:

first try

```bash
bin/act
```

then if that doesn't work 

```bash
bin/act -P ubuntu-latest=-self-hosted
```

to run in the codespace.

To shut down:

```bash
ansible-playbook down.yml
```

There is also a flyway migration here. To run the migration:

```bash
docker run --rm -v "/workspaces/<repo name>/migrations:/flyway/sql" redgate/flyway -user=root -password=Secret5555 -url=jdbc:mysql://172.17.0.1:3306/flyway_test migrate
```

This is a reproducible mysql setup, with a flyway migration. It is also the start of an example of using flyway and github actions together. Flyway (jdbc) needs the database to exist. The github action creates it if it doesn't exist and flyway takes over from there.

# End-to-End Automated Database Management CI/CD Pipeline

## Project Overview

This project implements a fully automated database management system using GitHub Actions for CI/CD, featuring advanced monitoring and performance optimization for a MySQL database with climate data.

## Database Structure

### Database: `project_db`
### Table: `ClimateData`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| record_id | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for each climate data record |
| location | VARCHAR(100) | NOT NULL | Name of the location where data was recorded |
| record_date | DATE | NOT NULL | Date when the climate data was recorded |
| temperature | FLOAT | NOT NULL | Temperature recorded on the date |
| precipitation | FLOAT | NOT NULL | Precipitation level (in mm) recorded on the date |
| humidity | FLOAT | NOT NULL | Humidity level recorded as a percentage on the date |

## Project Structure

```
PROG8850-finalassignment/
├── .github/
│   └── workflows/
│       ├── ci_cd_pipeline.yml      # Main CI/CD pipeline
│       └── mysql_action.yml        # Original MySQL action
├── sql/
│   ├── 01_create_database.sql      # Database creation
│   ├── 02_create_climate_table.sql # Initial table schema
│   ├── 03_add_humidity_column.sql  # Schema update
│   ├── 04_seed_data.sql           # Sample data insertion
│   └── 05_validation.sql          # Validation queries
├── scripts/
│   └── multi_thread_queries.py    # Concurrent query testing
├── .secrets                       # Local environment variables
├── .gitignore                     # Git ignore file
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## CI/CD Pipeline Stages

### 1. Environment Setup
- Installs MySQL client and Python dependencies
- Sets up MySQL service container
- Configures database connection parameters

### 2. Initial Schema Deployment
- Creates the `project_db` database
- Deploys the `ClimateData` table with initial structure

### 3. Schema Update
- Adds the `humidity` column to the existing table
- Demonstrates database migration capabilities

### 4. Data Seeding
- Populates the table with 25 sample climate records
- Includes data from major Canadian cities across multiple months

### 5. Concurrent Query Execution
- Executes multi-threaded database operations:
  - **INSERT queries**: Adds new climate records
  - **SELECT queries**: Retrieves data with various conditions
  - **UPDATE queries**: Modifies humidity levels based on conditions

### 6. Validation Step
- Verifies table structure and column existence
- Confirms successful data seeding
- Validates concurrent query execution results
- Performs data quality checks

## Security Features

- Uses GitHub Secrets for sensitive database credentials
- Includes `.secrets` file for local development (gitignored)
- Implements proper environment variable handling

## Multi-threaded Query Testing

The `scripts/multi_thread_queries.py` script performs:

### INSERT Operations (10 concurrent)
- Adds new climate records for additional Canadian cities
- Uses random data generation for realistic testing

### SELECT Operations (15 concurrent, 2 threads)
- Temperature-based queries
- Location-specific data retrieval
- Date range aggregations
- Humidity and precipitation correlations

### UPDATE Operations (8 concurrent)
- Location-based humidity adjustments
- Temperature-dependent humidity modifications
- Precipitation-based humidity updates

## Running Locally

### Prerequisites
- Docker and Docker Compose
- MySQL client
- Python 3.x with pip

### Setup
1. Start the database:
   ```bash
   ansible-playbook up.yml
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the pipeline manually:
   ```bash
   # Execute SQL scripts in order
   mysql -h 127.0.0.1 -u root -pSecret5555 < sql/01_create_database.sql
   mysql -h 127.0.0.1 -u root -pSecret5555 < sql/02_create_climate_table.sql
   mysql -h 127.0.0.1 -u root -pSecret5555 < sql/03_add_humidity_column.sql
   mysql -h 127.0.0.1 -u root -pSecret5555 < sql/04_seed_data.sql
   
   # Run concurrent queries
   python3 scripts/multi_thread_queries.py
   
   # Validate setup
   mysql -h 127.0.0.1 -u root -pSecret5555 project_db < sql/05_validation.sql
   ```

### Testing with Act (Local GitHub Actions)
```bash
# Install act if not available
bin/act

# Or with self-hosted runner
bin/act -P ubuntu-latest=-self-hosted
```

## Monitoring and Performance

The pipeline includes:
- Real-time logging of all operations
- Performance metrics for concurrent queries
- Error tracking and reporting
- Data quality validation
- Execution time monitoring

## Key Features

1. **Automated Database Deployment**: Complete automation from schema creation to data seeding
2. **Schema Migration**: Demonstrates adding new columns to existing tables
3. **Concurrent Testing**: Multi-threaded query execution to test database robustness
4. **Comprehensive Validation**: Multiple validation steps ensure deployment success
5. **Security Best Practices**: Proper secrets management and environment configuration
6. **Error Handling**: Robust error handling and troubleshooting capabilities

## Expected Results

Upon successful pipeline execution:
- `project_db` database created
- `ClimateData` table with all required columns
- 25+ sample records inserted
- Successful concurrent query operations
- All validation checks passed
- Performance metrics logged

## Troubleshooting

Common issues and solutions:
1. **MySQL Connection Issues**: Check service startup and credentials
2. **Schema Conflicts**: Ensure clean database state before deployment
3. **Python Dependencies**: Verify all required packages are installed
4. **Permission Issues**: Ensure proper file permissions for scripts

This implementation provides a robust foundation for automated database management with comprehensive testing and validation capabilities.

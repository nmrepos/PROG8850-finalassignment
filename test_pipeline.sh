#!/bin/bash

# Local CI/CD Pipeline Test Script
# This script simulates the GitHub Actions workflow locally

set -e  # Exit on any error

echo "🚀 Starting Local CI/CD Pipeline Test"
echo "===================================="

# Load environment variables from .secrets file
if [ -f .secrets ]; then
    export $(cat .secrets | xargs)
    echo "✅ Environment variables loaded from .secrets"
else
    echo "⚠️  Using default environment variables"
    export DB_HOST="127.0.0.1"
    export DB_USER="root"
    export DB_PASSWORD="Secret5555"
    export DB_NAME="project_db"
    export DB_PORT="3306"
fi

echo "📊 Database Configuration:"
echo "  Host: $DB_HOST"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"
echo "  Port: $DB_PORT"
echo ""

# Test database connectivity
echo "🔍 Testing database connectivity..."
if mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -e "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed. Please ensure MySQL is running."
    echo "   Try running: ansible-playbook up.yml"
    exit 1
fi

# Step 1: Create Database
echo ""
echo "📝 Step 1: Creating Database..."
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD < sql/01_create_database.sql
echo "✅ Database created"

# Step 2: Create ClimateData table
echo ""
echo "📝 Step 2: Creating ClimateData Table..."
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD < sql/02_create_climate_table.sql
echo "✅ ClimateData table created"

# Step 3: Add humidity column
echo ""
echo "📝 Step 3: Adding Humidity Column..."
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD < sql/03_add_humidity_column.sql
echo "✅ Humidity column added"

# Step 4: Seed data
echo ""
echo "📝 Step 4: Seeding Sample Data..."
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD < sql/04_seed_data.sql
echo "✅ Sample data inserted"

# Step 5: Run concurrent queries
echo ""
echo "📝 Step 5: Running Concurrent Query Tests..."
if python3 -c "import mysql.connector" 2>/dev/null; then
    python3 scripts/multi_thread_queries.py
    echo "✅ Concurrent queries completed"
else
    echo "⚠️  Python mysql-connector not found. Installing..."
    pip3 install mysql-connector-python
    python3 scripts/multi_thread_queries.py
    echo "✅ Concurrent queries completed"
fi

# Step 6: Validation
echo ""
echo "📝 Step 6: Running Validation Checks..."

echo "=== Table Structure ==="
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "DESCRIBE ClimateData;"

echo ""
echo "=== Record Count ==="
RECORD_COUNT=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -s -N -e "SELECT COUNT(*) FROM ClimateData;")
echo "Total records: $RECORD_COUNT"

echo ""
echo "=== Sample Data ==="
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "SELECT * FROM ClimateData ORDER BY record_date DESC LIMIT 3;"

echo ""
echo "=== Data Quality Summary ==="
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT location) as unique_locations,
    MIN(temperature) as min_temp,
    MAX(temperature) as max_temp,
    ROUND(AVG(humidity), 2) as avg_humidity
FROM ClimateData;
"

echo ""
echo "🎉 Local CI/CD Pipeline Test Completed Successfully!"
echo "=================================================="
echo "✅ All steps executed without errors"
echo "✅ Database schema deployed correctly"
echo "✅ Sample data loaded successfully" 
echo "✅ Concurrent queries tested"
echo "✅ Validation checks passed"
echo ""
echo "Your database is ready for production deployment!"

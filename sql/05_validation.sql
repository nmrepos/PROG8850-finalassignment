-- Validation queries to verify the database setup
USE project_db;

-- Verify table structure
DESCRIBE ClimateData;

-- Check if humidity column exists
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'project_db' AND TABLE_NAME = 'ClimateData';

-- Verify sample data exists
SELECT COUNT(*) as total_records FROM ClimateData;

-- Show sample records
SELECT * FROM ClimateData LIMIT 5;

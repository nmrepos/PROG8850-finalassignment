-- Schema update: Add humidity column to ClimateData table
USE project_db;

ALTER TABLE ClimateData 
ADD COLUMN humidity FLOAT NOT NULL DEFAULT 0.0;

#!/usr/bin/env python3
"""
Multi-threaded database query execution script for ClimateData table.
This script executes concurrent INSERT, SELECT, and UPDATE queries to test database robustness.
"""

import mysql.connector
import threading
import time
import random
import os
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'Secret5555'),
            'database': os.getenv('DB_NAME', 'project_db'),
            'port': int(os.getenv('DB_PORT', '3306'))
        }
        
    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to database: {err}")
            return None

class ConcurrentQueryExecutor:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.results = {
            'inserts': 0,
            'selects': 0,
            'updates': 0,
            'errors': 0
        }
        self.lock = threading.Lock()
        
    def execute_insert_queries(self, num_queries=10):
        """Execute INSERT queries to add new climate data records"""
        connection = self.db_connection.get_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        locations = ['Edmonton', 'Winnipeg', 'Halifax', 'Victoria', 'Quebec City']
        
        try:
            for i in range(num_queries):
                location = random.choice(locations)
                record_date = datetime.now() - timedelta(days=random.randint(1, 365))
                temperature = round(random.uniform(-20.0, 35.0), 1)
                precipitation = round(random.uniform(0.0, 50.0), 1)
                humidity = round(random.uniform(30.0, 90.0), 1)
                
                query = """
                INSERT INTO ClimateData (location, record_date, temperature, precipitation, humidity)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (location, record_date.date(), temperature, precipitation, humidity))
                connection.commit()
                
                with self.lock:
                    self.results['inserts'] += 1
                    
                logger.info(f"Inserted record for {location} on {record_date.date()}")
                time.sleep(0.1)  # Small delay to simulate realistic load
                
        except mysql.connector.Error as err:
            logger.error(f"Insert error: {err}")
            with self.lock:
                self.results['errors'] += 1
        finally:
            cursor.close()
            connection.close()
            
    def execute_select_queries(self, num_queries=15):
        """Execute SELECT queries with various conditions"""
        connection = self.db_connection.get_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        
        try:
            for i in range(num_queries):
                # Random query types
                query_type = random.choice(['temperature', 'location', 'date', 'humidity'])
                
                if query_type == 'temperature':
                    min_temp = random.uniform(0.0, 25.0)
                    query = "SELECT * FROM ClimateData WHERE temperature > %s ORDER BY temperature DESC LIMIT 5"
                    cursor.execute(query, (min_temp,))
                    
                elif query_type == 'location':
                    location = random.choice(['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'])
                    query = "SELECT * FROM ClimateData WHERE location = %s ORDER BY record_date DESC LIMIT 10"
                    cursor.execute(query, (location,))
                    
                elif query_type == 'date':
                    start_date = '2024-03-01'
                    query = "SELECT location, AVG(temperature), AVG(humidity) FROM ClimateData WHERE record_date >= %s GROUP BY location"
                    cursor.execute(query, (start_date,))
                    
                elif query_type == 'humidity':
                    min_humidity = random.uniform(60.0, 80.0)
                    query = "SELECT * FROM ClimateData WHERE humidity > %s AND precipitation > 20.0 LIMIT 5"
                    cursor.execute(query, (min_humidity,))
                
                results = cursor.fetchall()
                
                with self.lock:
                    self.results['selects'] += 1
                    
                logger.info(f"Select query ({query_type}) returned {len(results)} records")
                time.sleep(0.05)
                
        except mysql.connector.Error as err:
            logger.error(f"Select error: {err}")
            with self.lock:
                self.results['errors'] += 1
        finally:
            cursor.close()
            connection.close()
            
    def execute_update_queries(self, num_queries=8):
        """Execute UPDATE queries to modify humidity levels based on location"""
        connection = self.db_connection.get_connection()
        if not connection:
            return
            
        cursor = connection.cursor()
        
        try:
            for i in range(num_queries):
                # Update humidity for specific locations and conditions
                update_type = random.choice(['location_based', 'temperature_based', 'precipitation_based'])
                
                if update_type == 'location_based':
                    location = random.choice(['Toronto', 'Vancouver', 'Montreal'])
                    humidity_adjustment = random.uniform(-5.0, 5.0)
                    query = """
                    UPDATE ClimateData 
                    SET humidity = humidity + %s 
                    WHERE location = %s AND humidity + %s BETWEEN 20.0 AND 95.0
                    """
                    cursor.execute(query, (humidity_adjustment, location, humidity_adjustment))
                    
                elif update_type == 'temperature_based':
                    min_temp = random.uniform(15.0, 25.0)
                    humidity_boost = random.uniform(2.0, 8.0)
                    query = """
                    UPDATE ClimateData 
                    SET humidity = humidity + %s 
                    WHERE temperature > %s AND humidity + %s <= 95.0
                    """
                    cursor.execute(query, (humidity_boost, min_temp, humidity_boost))
                    
                elif update_type == 'precipitation_based':
                    min_precip = random.uniform(20.0, 40.0)
                    humidity_increase = random.uniform(3.0, 10.0)
                    query = """
                    UPDATE ClimateData 
                    SET humidity = humidity + %s 
                    WHERE precipitation > %s AND humidity + %s <= 95.0
                    """
                    cursor.execute(query, (humidity_increase, min_precip, humidity_increase))
                
                connection.commit()
                affected_rows = cursor.rowcount
                
                with self.lock:
                    self.results['updates'] += 1
                    
                logger.info(f"Update query ({update_type}) affected {affected_rows} rows")
                time.sleep(0.1)
                
        except mysql.connector.Error as err:
            logger.error(f"Update error: {err}")
            with self.lock:
                self.results['errors'] += 1
        finally:
            cursor.close()
            connection.close()

    def run_concurrent_tests(self):
        """Run all query types concurrently using threads"""
        logger.info("Starting concurrent database query execution...")
        
        # Create threads for different query types
        threads = []
        
        # Insert threads
        insert_thread = threading.Thread(target=self.execute_insert_queries, args=(10,), name="INSERT-Thread")
        threads.append(insert_thread)
        
        # Select threads (multiple threads for more concurrent load)
        select_thread1 = threading.Thread(target=self.execute_select_queries, args=(8,), name="SELECT-Thread-1")
        select_thread2 = threading.Thread(target=self.execute_select_queries, args=(7,), name="SELECT-Thread-2")
        threads.extend([select_thread1, select_thread2])
        
        # Update thread
        update_thread = threading.Thread(target=self.execute_update_queries, args=(8,), name="UPDATE-Thread")
        threads.append(update_thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        end_time = time.time()
        
        # Print results
        logger.info("=" * 50)
        logger.info("CONCURRENT QUERY EXECUTION RESULTS")
        logger.info("=" * 50)
        logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")
        logger.info(f"Successful INSERT operations: {self.results['inserts']}")
        logger.info(f"Successful SELECT operations: {self.results['selects']}")
        logger.info(f"Successful UPDATE operations: {self.results['updates']}")
        logger.info(f"Total errors: {self.results['errors']}")
        logger.info(f"Total successful operations: {sum([self.results['inserts'], self.results['selects'], self.results['updates']])}")
        
        return self.results

def main():
    """Main function to execute concurrent database tests"""
    logger.info("Initializing concurrent database query tests...")
    
    # Initialize database connection
    db_conn = DatabaseConnection()
    
    # Test database connection
    test_conn = db_conn.get_connection()
    if not test_conn:
        logger.error("Failed to connect to database. Exiting...")
        return False
    test_conn.close()
    
    logger.info("Database connection successful. Starting concurrent tests...")
    
    # Initialize and run executor
    executor = ConcurrentQueryExecutor(db_conn)
    results = executor.run_concurrent_tests()
    
    # Return success status
    return results['errors'] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

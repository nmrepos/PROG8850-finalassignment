import os
import time
import random
import logging
from datetime import datetime
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
import mysql.connector
from mysql.connector import Error

class SignOzLogger:
    def __init__(self):
        # Load environment variables
        self.load_env_vars()
        
        # Initialize OpenTelemetry
        self.setup_otel()
        
        # Setup logger
        self.setup_logger()
    
    def load_env_vars(self):
        """Load environment variables from .secrets file"""
        try:
            with open('/workspaces/PROG8850-finalassignment/.secrets', 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('//'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        except FileNotFoundError:
            print("Warning: .secrets file not found")
        
        self.db_config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'Secret5555'),
            'database': os.getenv('DB_NAME', 'project_db'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
    
    def setup_otel(self):
        """Setup OpenTelemetry configuration for SignOz"""
        # Resource configuration
        resource = Resource.create({
            "service.name": "mysql-database-automation",
            "service.version": "1.0.0",
            "deployment.environment": "development",
            "host.name": "prog8850-container",
            "database.name": "project_db"
        })
        
        # Setup tracing
        trace.set_tracer_provider(TracerProvider(resource=resource))
        tracer_provider = trace.get_tracer_provider()
        
        # OTLP Span Exporter for traces
        otlp_span_exporter = OTLPSpanExporter(
            endpoint="https://otel.nidhun.me",
            insecure=False,
            headers={}
        )
        
        span_processor = BatchSpanProcessor(otlp_span_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Setup logging
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)
        self.logger_provider = logger_provider  # <-- Store for LoggingHandler
        
        # OTLP Log Exporter for logs
        otlp_log_exporter = OTLPLogExporter(
            endpoint="https://otel.nidhun.me",
            insecure=False,
            headers={}
        )
        
        log_processor = BatchLogRecordProcessor(otlp_log_exporter)
        logger_provider.add_log_record_processor(log_processor)
        
        self.tracer = trace.get_tracer(__name__)
    
    def setup_logger(self):
        """Setup Python logging with OpenTelemetry handler"""
        # Get the OpenTelemetry logging handler
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=self.logger_provider)
        
        # Setup logger
        self.logger = logging.getLogger("mysql_automation")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add OpenTelemetry handler
        self.logger.addHandler(handler)
        
        # Also add console handler for local debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(console_handler)
    
    def log_database_operation(self, operation_type, query, duration=None, records_affected=0, error=None):
        """Log database operations with structured data"""
        log_data = {
            "operation_type": operation_type,
            "query": query[:100] + "..." if len(query) > 100 else query,
            "duration_ms": duration,
            "records_affected": records_affected,
            "timestamp": datetime.now().isoformat(),
            "database": self.db_config['database'],
            "host": self.db_config['host']
        }
        
        if error:
            log_data["error"] = str(error)
            self.logger.error(f"Database operation failed: {operation_type}", extra=log_data)
        else:
            self.logger.info(f"Database operation successful: {operation_type}", extra=log_data)
    
    def log_pipeline_stage(self, stage_name, status, details=None):
        """Log CI/CD pipeline stages"""
        log_data = {
            "pipeline_stage": stage_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "project": "prog8850-database-automation"
        }
        
        if details:
            log_data["details"] = details
        
        if status == "success":
            self.logger.info(f"Pipeline stage completed: {stage_name}", extra=log_data)
        elif status == "failed":
            self.logger.error(f"Pipeline stage failed: {stage_name}", extra=log_data)
        else:
            self.logger.info(f"Pipeline stage {status}: {stage_name}", extra=log_data)
    
    def test_database_connection(self):
        """Test database connection and log the results"""
        with self.tracer.start_as_current_span("database_connection_test") as span:
            start_time = time.time()
            
            try:
                connection = mysql.connector.connect(**self.db_config)
                duration = (time.time() - start_time) * 1000
                
                if connection.is_connected():
                    cursor = connection.cursor()
                    cursor.execute("SELECT VERSION()")
                    version = cursor.fetchone()[0]
                    
                    span.set_attribute("db.operation", "connection_test")
                    span.set_attribute("db.connection_string", f"{self.db_config['host']}:{self.db_config['port']}")
                    span.set_attribute("db.user", self.db_config['user'])
                    span.set_attribute("mysql.version", version)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    
                    self.log_database_operation(
                        "CONNECTION_TEST",
                        "SELECT VERSION()",
                        duration=duration,
                        records_affected=1
                    )
                    
                    cursor.close()
                    connection.close()
                    return True
                    
            except Error as e:
                duration = (time.time() - start_time) * 1000
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                span.set_attribute("error.message", str(e))
                
                self.log_database_operation(
                    "CONNECTION_TEST",
                    "SELECT VERSION()",
                    duration=duration,
                    error=e
                )
                return False
    
    def simulate_climate_data_operations(self):
        """Simulate various database operations on ClimateData table"""
        operations = [
            ("SELECT", "SELECT COUNT(*) FROM ClimateData"),
            ("SELECT", "SELECT * FROM ClimateData WHERE temperature > 20 LIMIT 5"),
            ("SELECT", "SELECT location, AVG(temperature) FROM ClimateData GROUP BY location"),
            ("INSERT", "INSERT INTO ClimateData (location, record_date, temperature, precipitation, humidity) VALUES ('TestCity', '2024-08-16', 25.5, 10.2, 65.0)"),
            ("UPDATE", "UPDATE ClimateData SET humidity = 70.0 WHERE location = 'TestCity'"),
            ("DELETE", "DELETE FROM ClimateData WHERE location = 'TestCity'")
        ]
        
        for op_type, query in operations:
            with self.tracer.start_as_current_span(f"database_{op_type.lower()}") as span:
                start_time = time.time()
                
                try:
                    connection = mysql.connector.connect(**self.db_config)
                    cursor = connection.cursor()
                    
                    cursor.execute(query)
                    
                    if op_type in ["INSERT", "UPDATE", "DELETE"]:
                        connection.commit()
                        records_affected = cursor.rowcount
                    else:
                        records_affected = cursor.rowcount if cursor.rowcount > 0 else len(cursor.fetchall())
                    
                    duration = (time.time() - start_time) * 1000
                    
                    span.set_attribute("db.operation", op_type)
                    span.set_attribute("db.statement", query)
                    span.set_attribute("db.rows_affected", records_affected)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    
                    self.log_database_operation(
                        op_type,
                        query,
                        duration=duration,
                        records_affected=records_affected
                    )
                    
                    cursor.close()
                    connection.close()
                    
                    # Add some delay between operations
                    time.sleep(random.uniform(0.5, 2.0))
                    
                except Error as e:
                    duration = (time.time() - start_time) * 1000
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    
                    self.log_database_operation(
                        op_type,
                        query,
                        duration=duration,
                        error=e
                    )
    
    def log_performance_metrics(self):
        """Log system performance metrics"""
        try:
            # Simulate CPU and memory metrics
            cpu_usage = random.uniform(10, 80)
            memory_usage = random.uniform(30, 90)
            disk_io = random.uniform(100, 1000)
            
            metrics_data = {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory_usage,
                "disk_io_mbps": disk_io,
                "active_connections": random.randint(1, 10),
                "query_cache_hit_ratio": random.uniform(85, 98),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("System performance metrics", extra=metrics_data)
            
            # Log alerts if thresholds exceeded
            if cpu_usage > 70:
                self.logger.warning("High CPU usage detected", extra={
                    "alert_type": "high_cpu_usage",
                    "cpu_usage": cpu_usage,
                    "threshold": 70
                })
            
            if memory_usage > 85:
                self.logger.warning("High memory usage detected", extra={
                    "alert_type": "high_memory_usage", 
                    "memory_usage": memory_usage,
                    "threshold": 85
                })
                
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics: {e}")
    
    def run_comprehensive_logging_demo(self):
        """Run a comprehensive demo of logging capabilities"""
        print("🚀 Starting SignOz OpenTelemetry Logging Demo...")
        
        # Log pipeline start
        self.log_pipeline_stage("DEMO_START", "started", {"demo_type": "comprehensive_logging"})
        
        # Test database connection
        print("📊 Testing database connection...")
        if self.test_database_connection():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
        
        # Log pipeline stages
        stages = [
            ("ENVIRONMENT_SETUP", "success", {"tools": ["mysql-client", "python", "otel"]}),
            ("SCHEMA_DEPLOYMENT", "success", {"tables_created": ["ClimateData"]}),
            ("DATA_SEEDING", "success", {"records_inserted": 25}),
            ("CONCURRENT_TESTING", "in_progress", {"threads": 10})
        ]
        
        for stage, status, details in stages:
            self.log_pipeline_stage(stage, status, details)
            time.sleep(1)
        
        # Simulate database operations
        print("🔄 Simulating database operations...")
        self.simulate_climate_data_operations()
        
        # Log performance metrics
        print("📈 Logging performance metrics...")
        for i in range(5):
            self.log_performance_metrics()
            time.sleep(2)
        
        # Final pipeline completion
        self.log_pipeline_stage("DEMO_COMPLETE", "success", {
            "total_operations": 15,
            "duration_seconds": 30,
            "logs_sent": "50+"
        })
        
        print("✅ SignOz logging demo completed!")
        print("🌐 Check your logs at: https://otel.nidhun.me")

def main():
    """Main function to run the SignOz logging demo"""
    try:
        logger = SignOzLogger()
        logger.run_comprehensive_logging_demo()
    except Exception as e:
        print(f"❌ Error running SignOz logger: {e}")
        logging.error(f"SignOz logger failed: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
RAG Interface Services Startup Script

Starts all RAG Interface services in the correct order with proper health checks.
"""

import asyncio
import subprocess
import sys
import time
import os
import signal
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class ServiceManager:
    """Manages the startup and health checking of RAG Interface services."""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # Service configurations
        self.services = {
            "error_reporting": {
                "module": "error_reporting_service.main:app",
                "port": 8000,
                "host": "0.0.0.0",
                "env": {
                    "DATABASE_URL": "postgresql://rag_user:rag_password@localhost:5432/rag_interface_db",
                    "REDIS_URL": "redis://localhost:6379",
                    "LOG_LEVEL": "INFO",
                    "DEBUG": "false"
                }
            },
            "rag_integration": {
                "module": "rag_integration_service.main:app",
                "port": 8003,
                "host": "0.0.0.0",
                "env": {
                    "DATABASE_URL": "postgresql://rag_user:rag_password@localhost:5432/rag_interface_db",
                    "REDIS_URL": "redis://localhost:6379",
                    "ML_MODEL_PROVIDER": "mock",
                    "VECTOR_STORAGE_PROVIDER": "in_memory",
                    "LOG_LEVEL": "INFO",
                    "DEBUG": "false"
                }
            }
        }

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down services...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)

    def check_dependencies(self):
        """Check if required dependencies (PostgreSQL, Redis) are available."""
        print("🔍 Checking dependencies...")
        
        # Check PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="rag_interface_db",
                user="rag_user",
                password="rag_password"
            )
            conn.close()
            print("  ✅ PostgreSQL connection successful")
        except Exception as e:
            print(f"  ❌ PostgreSQL connection failed: {e}")
            return False
        
        # Check Redis
        try:
            import redis
            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            print("  ✅ Redis connection successful")
        except Exception as e:
            print(f"  ❌ Redis connection failed: {e}")
            return False
        
        return True

    def start_service(self, service_name, config):
        """Start a single service."""
        print(f"🚀 Starting {service_name} service...")
        
        # Prepare environment
        env = os.environ.copy()
        env.update(config["env"])
        env["PYTHONPATH"] = str(Path(__file__).parent / "src")
        
        # Start the service
        cmd = [
            sys.executable, "-m", "uvicorn",
            config["module"],
            "--host", config["host"],
            "--port", str(config["port"]),
            "--reload"
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[service_name] = {
                "process": process,
                "config": config
            }
            
            print(f"  ✅ {service_name} started on port {config['port']}")
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to start {service_name}: {e}")
            return False

    def check_service_health(self, service_name, config):
        """Check if a service is healthy."""
        import requests
        
        try:
            url = f"http://{config['host']}:{config['port']}/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def wait_for_service_health(self, service_name, config, timeout=30):
        """Wait for a service to become healthy."""
        print(f"⏳ Waiting for {service_name} to become healthy...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_service_health(service_name, config):
                print(f"  ✅ {service_name} is healthy")
                return True
            time.sleep(2)
        
        print(f"  ❌ {service_name} failed to become healthy within {timeout}s")
        return False

    def start_all_services(self):
        """Start all services in the correct order."""
        print("🚀 Starting RAG Interface Services...")
        
        # Check dependencies first
        if not self.check_dependencies():
            print("❌ Dependency check failed. Make sure PostgreSQL and Redis are running.")
            return False
        
        # Start services
        for service_name, config in self.services.items():
            if not self.start_service(service_name, config):
                print(f"❌ Failed to start {service_name}")
                return False
            
            # Wait a bit before starting the next service
            time.sleep(3)
            
            # Check health
            if not self.wait_for_service_health(service_name, config):
                print(f"❌ {service_name} is not healthy")
                return False
        
        print("🎉 All services started successfully!")
        return True

    def stop_all_services(self):
        """Stop all running services."""
        print("🛑 Stopping all services...")
        
        for service_name, service_info in self.processes.items():
            try:
                process = service_info["process"]
                print(f"  🛑 Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print(f"  ⚠️ Force killing {service_name}...")
                    process.kill()
                
                print(f"  ✅ {service_name} stopped")
            except Exception as e:
                print(f"  ❌ Error stopping {service_name}: {e}")

    def monitor_services(self):
        """Monitor running services and restart if needed."""
        print("👀 Monitoring services...")
        
        while self.running:
            try:
                for service_name, service_info in self.processes.items():
                    process = service_info["process"]
                    config = service_info["config"]
                    
                    # Check if process is still running
                    if process.poll() is not None:
                        print(f"⚠️ {service_name} has stopped, restarting...")
                        self.start_service(service_name, config)
                        self.wait_for_service_health(service_name, config)
                    
                    # Check health
                    elif not self.check_service_health(service_name, config):
                        print(f"⚠️ {service_name} is unhealthy")
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(5)

    def run(self):
        """Main run method."""
        self.setup_signal_handlers()
        
        if self.start_all_services():
            try:
                self.monitor_services()
            except KeyboardInterrupt:
                pass
            finally:
                self.stop_all_services()
        else:
            print("❌ Failed to start services")
            self.stop_all_services()
            sys.exit(1)


def main():
    """Main entry point."""
    print("=" * 60)
    print("🚀 RAG Interface Services Manager")
    print("=" * 60)
    
    manager = ServiceManager()
    manager.run()


if __name__ == "__main__":
    main()

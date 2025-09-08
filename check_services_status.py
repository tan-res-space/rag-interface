#!/usr/bin/env python3
"""
RAG Interface Services Status Checker

Checks the status of all RAG Interface services and provides a comprehensive report.
"""

import requests
import subprocess
import json
import sys
from datetime import datetime


def check_docker_services():
    """Check Docker container status."""
    print("🐳 Checking Docker Services...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:  # Skip header
            for line in lines[1:]:
                if 'rag-' in line:
                    print(f"  ✅ {line}")
        else:
            print("  ❌ No RAG services found in Docker")
            return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error checking Docker services: {e}")
        return False


def check_service_health(service_name, url, port):
    """Check individual service health."""
    print(f"🔍 Checking {service_name}...")
    
    try:
        health_url = f"http://localhost:{port}/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ {service_name} is healthy")
            print(f"     Status: {health_data.get('status', 'unknown')}")
            print(f"     Version: {health_data.get('version', 'unknown')}")
            print(f"     Service: {health_data.get('service', 'unknown')}")
            return True
        else:
            print(f"  ❌ {service_name} returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ {service_name} is not responding (connection refused)")
        return False
    except requests.exceptions.Timeout:
        print(f"  ❌ {service_name} timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error checking {service_name}: {e}")
        return False


def check_database_connectivity():
    """Check database connectivity."""
    print("🗄️ Checking Database Connectivity...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="rag_interface_db",
            user="rag_user",
            password="rag_password"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"  ✅ PostgreSQL connected successfully")
        print(f"     Version: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ PostgreSQL connection failed: {e}")
        return False


def check_redis_connectivity():
    """Check Redis connectivity."""
    print("🔴 Checking Redis Connectivity...")
    
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        
        # Test basic operations
        r.ping()
        r.set("test_key", "test_value")
        value = r.get("test_key")
        r.delete("test_key")
        
        if value == "test_value":
            print(f"  ✅ Redis connected successfully")
            info = r.info()
            print(f"     Version: {info.get('redis_version', 'unknown')}")
            print(f"     Memory: {info.get('used_memory_human', 'unknown')}")
            return True
        else:
            print(f"  ❌ Redis test operation failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Redis connection failed: {e}")
        return False


def test_api_endpoints():
    """Test key API endpoints."""
    print("🔗 Testing API Endpoints...")
    
    endpoints = [
        {
            "name": "Error Reporting - Health",
            "url": "http://localhost:8000/health",
            "method": "GET"
        },
        {
            "name": "Error Reporting - API Info",
            "url": "http://localhost:8000/api/v1/info",
            "method": "GET"
        },
        {
            "name": "RAG Integration - Health",
            "url": "http://localhost:8003/health",
            "method": "GET"
        },
        {
            "name": "RAG Integration - API Info",
            "url": "http://localhost:8003/api/v1/info",
            "method": "GET"
        }
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        try:
            if endpoint["method"] == "GET":
                response = requests.get(endpoint["url"], timeout=5)
            else:
                response = requests.post(endpoint["url"], timeout=5)
            
            if response.status_code in [200, 201]:
                print(f"  ✅ {endpoint['name']} - Status: {response.status_code}")
                success_count += 1
            else:
                print(f"  ⚠️ {endpoint['name']} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {endpoint['name']} - Error: {e}")
    
    return success_count == len(endpoints)


def generate_status_report():
    """Generate comprehensive status report."""
    print("=" * 60)
    print("🚀 RAG Interface Services Status Report")
    print("=" * 60)
    print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check all components
    checks = [
        ("Docker Services", check_docker_services),
        ("Database Connectivity", check_database_connectivity),
        ("Redis Connectivity", check_redis_connectivity),
        ("Error Reporting Service", lambda: check_service_health("Error Reporting Service", "localhost", 8000)),
        ("RAG Integration Service", lambda: check_service_health("RAG Integration Service", "localhost", 8003)),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print()
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ Error during {check_name} check: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    print(f"\n🎯 Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All services are running successfully!")
        return 0
    else:
        print("⚠️ Some services need attention")
        return 1


def main():
    """Main entry point."""
    try:
        exit_code = generate_status_report()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Status check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during status check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

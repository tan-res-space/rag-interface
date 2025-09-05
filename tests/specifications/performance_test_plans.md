# Performance Test Plans
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Framework:** Artillery.js for load testing, k6 for stress testing  
**Performance Targets:** API <500ms, Dashboard <2s, Database <100ms

---

## Performance Test Overview

This document specifies comprehensive performance testing plans for the quality-based speaker bucket management system, covering load testing, stress testing, and performance benchmarking.

---

## 1. API Performance Tests

### 1.1 Enhanced Error Reporting API Load Tests

#### Test Plan: `PERF-API-ER-001: Error Reporting Endpoint Load Test`

**Objective:** Validate that the enhanced error reporting API can handle expected load with acceptable response times.

**Test Configuration:**
```yaml
# artillery-error-reporting.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10  # 10 requests per second
      name: "Warm up"
    - duration: 300
      arrivalRate: 50  # 50 requests per second
      name: "Sustained load"
    - duration: 120
      arrivalRate: 100 # 100 requests per second
      name: "Peak load"
  defaults:
    headers:
      Authorization: 'Bearer {{ $randomString() }}'
      Content-Type: 'application/json'

scenarios:
  - name: "Submit Enhanced Error Report"
    weight: 100
    flow:
      - post:
          url: "/api/v1/errors"
          json:
            job_id: "{{ $randomUuid() }}"
            speaker_id: "speaker-{{ $randomInt(1, 1000) }}"
            client_id: "client-{{ $randomInt(1, 100) }}"
            bucket_type: "{{ $randomPick(['no_touch', 'low_touch', 'medium_touch', 'high_touch']) }}"
            original_text: "The patient has severe hypertension and diabetes"
            corrected_text: "The patient has severe high blood pressure and diabetes"
            error_categories: ["medical_terminology"]
            metadata:
              audio_quality: "{{ $randomPick(['good', 'fair', 'poor']) }}"
              speaker_clarity: "{{ $randomPick(['clear', 'somewhat_clear', 'unclear']) }}"
              background_noise: "{{ $randomPick(['none', 'low', 'medium', 'high']) }}"
              number_of_speakers: "{{ $randomPick(['one', 'two', 'three', 'four', 'five']) }}"
              overlapping_speech: "{{ $randomBoolean() }}"
              requires_specialized_knowledge: "{{ $randomBoolean() }}"
              additional_notes: "Performance test generated error report"
          expect:
            - statusCode: 201
            - hasProperty: "error_id"
          capture:
            - json: "$.error_id"
              as: "errorId"
```

**Performance Criteria:**
- **Response Time**: 95th percentile < 500ms
- **Throughput**: Handle 100 requests/second
- **Error Rate**: < 1% error rate
- **Resource Usage**: CPU < 80%, Memory < 4GB

#### Test Plan: `PERF-API-SH-001: Speaker History API Load Test`

**Test Configuration:**
```yaml
# artillery-speaker-history.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 180
      arrivalRate: 30
      name: "Speaker history load test"

scenarios:
  - name: "Get Speaker History"
    weight: 70
    flow:
      - get:
          url: "/api/v1/speakers/speaker-{{ $randomInt(1, 1000) }}/history"
          expect:
            - statusCode: 200
            - hasProperty: "speaker_id"
            - hasProperty: "performance_metrics"
  
  - name: "Get Performance Trends"
    weight: 30
    flow:
      - get:
          url: "/api/v1/speakers/speaker-{{ $randomInt(1, 1000) }}/performance-trends"
          expect:
            - statusCode: 200
            - hasProperty: "improvement_indicators"
```

### 1.2 Database Query Performance Tests

#### Test Plan: `PERF-DB-001: Enhanced Metadata Query Performance`

**Objective:** Ensure database queries with enhanced metadata filters perform within acceptable limits.

**Test Scenarios:**
```sql
-- Test 1: Complex metadata filtering query
EXPLAIN ANALYZE
SELECT er.*, spm.current_bucket, spm.rectification_rate
FROM error_reports er
JOIN speaker_performance_metrics spm ON er.speaker_id = spm.speaker_id
WHERE er.bucket_type = 'medium_touch'
  AND er.requires_specialized_knowledge = true
  AND er.number_of_speakers = 'one'
  AND er.created_at >= NOW() - INTERVAL '30 days'
ORDER BY er.created_at DESC
LIMIT 50;

-- Test 2: Speaker history aggregation query
EXPLAIN ANALYZE
SELECT 
  speaker_id,
  COUNT(*) as total_errors,
  COUNT(CASE WHEN status = 'rectified' THEN 1 END) as rectified_errors,
  AVG(CASE WHEN audio_quality = 'good' THEN 3 WHEN audio_quality = 'fair' THEN 2 ELSE 1 END) as avg_quality
FROM error_reports
WHERE speaker_id = 'speaker-123'
  AND created_at >= NOW() - INTERVAL '6 months'
GROUP BY speaker_id;

-- Test 3: Bucket distribution analytics query
EXPLAIN ANALYZE
SELECT 
  current_bucket,
  COUNT(*) as speaker_count,
  AVG(rectification_rate) as avg_rectification_rate,
  AVG(EXTRACT(EPOCH FROM time_in_current_bucket) / 86400) as avg_days_in_bucket
FROM speaker_performance_metrics
GROUP BY current_bucket;
```

**Performance Criteria:**
- **Query Execution Time**: < 100ms for all queries
- **Index Usage**: All queries should use appropriate indexes
- **Connection Pool**: Maintain < 50% pool utilization under load

---

## 2. Frontend Performance Tests

### 2.1 Dashboard Loading Performance

#### Test Plan: `PERF-FE-001: Dashboard Component Loading`

**Test Configuration:**
```javascript
// k6-dashboard-performance.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 50 }, // Ramp up to 50 users
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 0 },  // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
  },
};

export default function() {
  // Test dashboard loading
  let dashboardResponse = http.get('http://localhost:5173/dashboard');
  check(dashboardResponse, {
    'dashboard status is 200': (r) => r.status === 200,
    'dashboard loads in <2s': (r) => r.timings.duration < 2000,
  });
  
  // Test bucket overview API
  let bucketResponse = http.get('http://localhost:8000/api/v1/dashboard/bucket-overview');
  check(bucketResponse, {
    'bucket overview status is 200': (r) => r.status === 200,
    'bucket overview loads in <500ms': (r) => r.timings.duration < 500,
  });
  
  // Test performance metrics API
  let metricsResponse = http.get('http://localhost:8000/api/v1/dashboard/performance-metrics');
  check(metricsResponse, {
    'metrics status is 200': (r) => r.status === 200,
    'metrics loads in <500ms': (r) => r.timings.duration < 500,
  });
  
  errorRate.add(dashboardResponse.status !== 200);
  sleep(1);
}
```

### 2.2 Error Reporting Form Performance

#### Test Plan: `PERF-FE-002: Error Reporting Form Interaction`

**Test Configuration:**
```javascript
// playwright-form-performance.js
import { test, expect } from '@playwright/test';

test('Error reporting form performance', async ({ page }) => {
  // Start performance monitoring
  await page.goto('/error-reporting');
  
  // Measure initial page load
  const navigationTiming = await page.evaluate(() => {
    return {
      loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart,
      domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
    };
  });
  
  expect(navigationTiming.loadComplete).toBeLessThan(3000); // 3s load time
  expect(navigationTiming.domReady).toBeLessThan(1500);     // 1.5s DOM ready
  
  // Measure form interaction performance
  const startTime = Date.now();
  
  // Complete error reporting workflow
  await page.locator('[data-testid="selectable-text"]').dblclick();
  await page.click('button:has-text("Next")');
  await page.click('button:has-text("Medical Terminology")');
  await page.click('button:has-text("Next")');
  await page.fill('[placeholder="Enter the corrected text..."]', 'corrected text');
  await page.click('button:has-text("Next")');
  
  // Fill enhanced metadata form
  await page.fill('[data-testid="speaker-id"]', 'speaker-123');
  await page.selectOption('[data-testid="bucket-type"]', 'medium_touch');
  await page.selectOption('[data-testid="audio-quality"]', 'good');
  await page.selectOption('[data-testid="number-of-speakers"]', 'one');
  await page.check('[data-testid="overlapping-speech-no"]');
  await page.check('[data-testid="requires-specialized-knowledge-yes"]');
  
  const endTime = Date.now();
  const workflowTime = endTime - startTime;
  
  expect(workflowTime).toBeLessThan(10000); // Complete workflow in <10s
});
```

---

## 3. Vector Database Performance Tests

### 3.1 Enhanced Metadata Search Performance

#### Test Plan: `PERF-VDB-001: Vector Search with Enhanced Metadata`

**Test Configuration:**
```python
# vector_db_performance_test.py
import asyncio
import time
import statistics
from typing import List
import pytest

class VectorDBPerformanceTest:
    def __init__(self, vector_db_client):
        self.client = vector_db_client
        self.test_results = []
    
    async def test_enhanced_metadata_search_performance(self):
        """Test vector search performance with enhanced metadata filters"""
        
        search_scenarios = [
            {
                "query": "medical terminology error",
                "filters": {
                    "bucket_type": "medium_touch",
                    "requires_specialized_knowledge": True
                },
                "top_k": 10
            },
            {
                "query": "pronunciation error",
                "filters": {
                    "number_of_speakers": "one",
                    "overlapping_speech": False,
                    "audio_quality": "good"
                },
                "top_k": 20
            },
            {
                "query": "grammar correction",
                "filters": {
                    "bucket_type": "high_touch",
                    "background_noise": "low"
                },
                "top_k": 15
            }
        ]
        
        for scenario in search_scenarios:
            response_times = []
            
            # Run each scenario 100 times
            for _ in range(100):
                start_time = time.time()
                
                results = await self.client.search(
                    query_text=scenario["query"],
                    filters=scenario["filters"],
                    top_k=scenario["top_k"]
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
            
            # Calculate statistics
            avg_time = statistics.mean(response_times)
            p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
            
            self.test_results.append({
                "scenario": scenario,
                "avg_response_time": avg_time,
                "p95_response_time": p95_time,
                "p99_response_time": p99_time
            })
            
            # Performance assertions
            assert avg_time < 200, f"Average response time {avg_time}ms exceeds 200ms limit"
            assert p95_time < 500, f"95th percentile {p95_time}ms exceeds 500ms limit"
            assert p99_time < 1000, f"99th percentile {p99_time}ms exceeds 1000ms limit"
    
    async def test_bulk_insert_performance(self):
        """Test bulk insertion performance for enhanced metadata"""
        
        # Generate test data with enhanced metadata
        test_vectors = []
        for i in range(1000):
            test_vectors.append({
                "id": f"test-vector-{i}",
                "text": f"Test error text {i}",
                "embedding": [0.1] * 768,  # Mock embedding
                "metadata": {
                    "speaker_id": f"speaker-{i % 100}",
                    "bucket_type": ["no_touch", "low_touch", "medium_touch", "high_touch"][i % 4],
                    "number_of_speakers": ["one", "two", "three"][i % 3],
                    "overlapping_speech": i % 2 == 0,
                    "requires_specialized_knowledge": i % 3 == 0,
                    "audio_quality": ["good", "fair", "poor"][i % 3]
                }
            })
        
        # Test bulk insertion
        start_time = time.time()
        await self.client.bulk_insert(test_vectors)
        end_time = time.time()
        
        insertion_time = end_time - start_time
        vectors_per_second = len(test_vectors) / insertion_time
        
        # Performance assertions
        assert vectors_per_second > 100, f"Insertion rate {vectors_per_second} vectors/sec is too slow"
        assert insertion_time < 30, f"Bulk insertion took {insertion_time}s, exceeds 30s limit"
```

---

## 4. Stress Testing

### 4.1 System Breaking Point Tests

#### Test Plan: `STRESS-001: System Breaking Point Analysis`

**Test Configuration:**
```yaml
# artillery-stress-test.yml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 300
      arrivalRate: 1
      rampTo: 200  # Gradually increase to 200 req/sec
      name: "Stress ramp up"
    - duration: 600
      arrivalRate: 200
      name: "Sustained stress"
    - duration: 300
      arrivalRate: 200
      rampTo: 500  # Push to breaking point
      name: "Breaking point test"

scenarios:
  - name: "Mixed Load Stress Test"
    weight: 100
    flow:
      - think: 1
      - loop:
        - post:
            url: "/api/v1/errors"
            json:
              job_id: "{{ $randomUuid() }}"
              speaker_id: "speaker-{{ $randomInt(1, 10000) }}"
              bucket_type: "{{ $randomPick(['no_touch', 'low_touch', 'medium_touch', 'high_touch']) }}"
              metadata:
                number_of_speakers: "{{ $randomPick(['one', 'two', 'three', 'four', 'five']) }}"
                overlapping_speech: "{{ $randomBoolean() }}"
                requires_specialized_knowledge: "{{ $randomBoolean() }}"
        - get:
            url: "/api/v1/speakers/speaker-{{ $randomInt(1, 1000) }}/history"
        - get:
            url: "/api/v1/dashboard/bucket-overview"
        count: 3
```

### 4.2 Memory Leak Detection

#### Test Plan: `STRESS-002: Memory Leak Detection`

**Test Configuration:**
```javascript
// memory-leak-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30m', target: 50 }, // Run for 30 minutes
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
  },
};

export default function() {
  // Continuous load to detect memory leaks
  let responses = [];
  
  for (let i = 0; i < 10; i++) {
    responses.push(http.post('http://localhost:8000/api/v1/errors', JSON.stringify({
      job_id: `job-${Date.now()}-${i}`,
      speaker_id: `speaker-${Math.floor(Math.random() * 1000)}`,
      bucket_type: ['no_touch', 'low_touch', 'medium_touch', 'high_touch'][Math.floor(Math.random() * 4)],
      metadata: {
        number_of_speakers: ['one', 'two', 'three'][Math.floor(Math.random() * 3)],
        overlapping_speech: Math.random() > 0.5,
        requires_specialized_knowledge: Math.random() > 0.5,
        additional_notes: 'Memory leak test data '.repeat(50) // Large payload
      }
    }), {
      headers: { 'Content-Type': 'application/json' }
    }));
  }
  
  // Check all responses
  responses.forEach(response => {
    check(response, {
      'status is 201': (r) => r.status === 201,
    });
  });
  
  sleep(1);
}
```

---

## 5. Performance Monitoring and Alerting

### 5.1 Real-time Performance Monitoring

**Monitoring Configuration:**
```yaml
# prometheus-config.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rag-interface-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'rag-interface-frontend'
    static_configs:
      - targets: ['localhost:5173']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:5432']
    scrape_interval: 10s
```

**Performance Alerts:**
```yaml
# alerting-rules.yml
groups:
  - name: performance_alerts
    rules:
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "API response time is high"
          description: "95th percentile response time is {{ $value }}s"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
      
      - alert: DatabaseSlowQueries
        expr: pg_stat_activity_max_tx_duration > 100
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Slow database queries detected"
          description: "Query duration is {{ $value }}ms"
```

---

## 6. Performance Test Execution

### Test Execution Scripts
```bash
#!/bin/bash
# run-performance-tests.sh

echo "Starting Performance Test Suite..."

# 1. API Load Tests
echo "Running API Load Tests..."
artillery run tests/performance/artillery-error-reporting.yml
artillery run tests/performance/artillery-speaker-history.yml

# 2. Database Performance Tests
echo "Running Database Performance Tests..."
psql -d test_db -f tests/performance/database-performance-queries.sql

# 3. Frontend Performance Tests
echo "Running Frontend Performance Tests..."
npx playwright test tests/performance/frontend-performance.spec.ts

# 4. Vector Database Performance Tests
echo "Running Vector Database Performance Tests..."
python tests/performance/vector_db_performance_test.py

# 5. Stress Tests
echo "Running Stress Tests..."
artillery run tests/performance/artillery-stress-test.yml

# 6. Memory Leak Tests
echo "Running Memory Leak Tests..."
k6 run tests/performance/memory-leak-test.js

echo "Performance Test Suite Complete!"
```

### Performance Report Generation
```python
# generate-performance-report.py
import json
import pandas as pd
import matplotlib.pyplot as plt

def generate_performance_report():
    """Generate comprehensive performance test report"""
    
    # Load test results
    api_results = load_artillery_results('api-load-test-results.json')
    db_results = load_database_results('db-performance-results.json')
    frontend_results = load_playwright_results('frontend-performance-results.json')
    
    # Generate charts
    create_response_time_chart(api_results)
    create_throughput_chart(api_results)
    create_database_performance_chart(db_results)
    
    # Generate summary report
    create_summary_report({
        'api': api_results,
        'database': db_results,
        'frontend': frontend_results
    })

if __name__ == "__main__":
    generate_performance_report()
```

### Performance Criteria Summary
| Component | Metric | Target | Critical |
|-----------|--------|---------|----------|
| API Endpoints | Response Time (95th) | <500ms | <1000ms |
| Dashboard | Page Load | <2s | <5s |
| Database Queries | Execution Time | <100ms | <500ms |
| Vector Search | Search Time | <200ms | <1000ms |
| Error Rate | All Components | <1% | <5% |
| Throughput | API | 100 req/sec | 50 req/sec |

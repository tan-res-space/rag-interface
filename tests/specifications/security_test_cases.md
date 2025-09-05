# Security Test Cases
## Quality-Based Speaker Bucket Management System

**Date:** December 19, 2024  
**Version:** 2.0  
**Framework:** OWASP ZAP, Burp Suite, Custom Security Tests  
**Compliance:** HIPAA, SOC 2, GDPR

---

## Security Test Overview

This document specifies comprehensive security test cases for the quality-based speaker bucket management system, covering authentication, authorization, data protection, and compliance requirements.

---

## 1. Authentication and Authorization Tests

### 1.1 JWT Token Security Tests

#### Test Case: `SEC-AUTH-001: JWT Token Validation`

**Objective:** Ensure JWT tokens are properly validated and secure.

**Test Steps:**
```python
import jwt
import requests
import pytest
from datetime import datetime, timedelta

class TestJWTSecurity:
    
    def test_invalid_jwt_token_rejection(self):
        """Test that invalid JWT tokens are rejected"""
        
        invalid_tokens = [
            "invalid.token.here",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
            "",
            None,
            "Bearer malformed_token"
        ]
        
        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            response = requests.get(
                "http://localhost:8000/api/v1/speakers/speaker-123/history",
                headers=headers
            )
            assert response.status_code == 401
            assert "Invalid token" in response.json()["error"]["message"]
    
    def test_expired_jwt_token_rejection(self):
        """Test that expired JWT tokens are rejected"""
        
        # Create expired token
        expired_payload = {
            "user_id": "test-user",
            "role": "qa",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        expired_token = jwt.encode(expired_payload, "secret", algorithm="HS256")
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = requests.get(
            "http://localhost:8000/api/v1/speakers/speaker-123/history",
            headers=headers
        )
        
        assert response.status_code == 401
        assert "Token expired" in response.json()["error"]["message"]
    
    def test_jwt_token_tampering_detection(self):
        """Test that tampered JWT tokens are detected"""
        
        # Create valid token
        valid_payload = {
            "user_id": "test-user",
            "role": "qa",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        valid_token = jwt.encode(valid_payload, "secret", algorithm="HS256")
        
        # Tamper with token by changing last character
        tampered_token = valid_token[:-1] + "X"
        
        headers = {"Authorization": f"Bearer {tampered_token}"}
        response = requests.get(
            "http://localhost:8000/api/v1/speakers/speaker-123/history",
            headers=headers
        )
        
        assert response.status_code == 401
        assert "Invalid signature" in response.json()["error"]["message"]
```

#### Test Case: `SEC-AUTH-002: Role-Based Access Control`

**Test Steps:**
```python
def test_role_based_access_control(self):
    """Test that users can only access resources appropriate to their role"""
    
    # QA role should have full access
    qa_token = create_test_token(role="qa")
    qa_headers = {"Authorization": f"Bearer {qa_token}"}
    
    response = requests.get(
        "http://localhost:8000/api/v1/speakers/speaker-123/history",
        headers=qa_headers
    )
    assert response.status_code == 200
    
    # MT role should have limited access
    mt_token = create_test_token(role="mt")
    mt_headers = {"Authorization": f"Bearer {mt_token}"}
    
    response = requests.post(
        "http://localhost:8000/api/v1/verification/pull-jobs",
        json={"speaker_id": "speaker-123"},
        headers=mt_headers
    )
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["error"]["message"]
    
    # Admin role should have administrative access
    admin_token = create_test_token(role="admin")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.get(
        "http://localhost:8000/api/v1/admin/system-config",
        headers=admin_headers
    )
    assert response.status_code == 200
```

### 1.2 Session Management Security

#### Test Case: `SEC-SESSION-001: Session Security Validation`

**Test Steps:**
```python
def test_session_security(self):
    """Test session management security measures"""
    
    # Test session timeout
    token = create_test_token(exp_minutes=1)  # 1 minute expiry
    headers = {"Authorization": f"Bearer {token}"}
    
    # Initial request should work
    response = requests.get(
        "http://localhost:8000/api/v1/dashboard/bucket-overview",
        headers=headers
    )
    assert response.status_code == 200
    
    # Wait for token to expire
    time.sleep(65)  # Wait 65 seconds
    
    # Request should now fail
    response = requests.get(
        "http://localhost:8000/api/v1/dashboard/bucket-overview",
        headers=headers
    )
    assert response.status_code == 401
```

---

## 2. Data Protection and Encryption Tests

### 2.1 Sensitive Data Encryption

#### Test Case: `SEC-DATA-001: Sensitive Field Encryption`

**Test Steps:**
```python
def test_sensitive_data_encryption(self):
    """Test that sensitive data fields are encrypted in storage"""
    
    # Submit error report with sensitive data
    sensitive_data = {
        "job_id": "job-123",
        "speaker_id": "speaker-456",
        "bucket_type": "medium_touch",
        "metadata": {
            "additional_notes": "Patient has history of cardiac issues and diabetes",
            "context_notes": "Sensitive medical information discussed"
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/errors",
        json=sensitive_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    error_id = response.json()["error_id"]
    
    # Check database directly to ensure encryption
    db_record = get_error_report_from_db(error_id)
    
    # Sensitive fields should be encrypted (not readable)
    assert db_record["additional_notes"] != sensitive_data["metadata"]["additional_notes"]
    assert "cardiac" not in db_record["additional_notes"]  # Original text not visible
    assert len(db_record["additional_notes"]) > 50  # Encrypted data is longer
    
    # API response should return decrypted data
    api_response = requests.get(
        f"http://localhost:8000/api/v1/errors/{error_id}",
        headers=auth_headers
    )
    api_data = api_response.json()
    assert api_data["metadata"]["additional_notes"] == sensitive_data["metadata"]["additional_notes"]
```

### 2.2 Data Transmission Security

#### Test Case: `SEC-TRANS-001: HTTPS Enforcement`

**Test Steps:**
```python
def test_https_enforcement(self):
    """Test that HTTPS is enforced for all communications"""
    
    # Test HTTP redirect to HTTPS
    response = requests.get("http://localhost:8000/api/v1/health", allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["Location"].startswith("https://")
    
    # Test HTTPS connection
    response = requests.get("https://localhost:8443/api/v1/health", verify=False)
    assert response.status_code == 200
    
    # Test security headers
    assert "Strict-Transport-Security" in response.headers
    assert "X-Content-Type-Options" in response.headers
    assert "X-Frame-Options" in response.headers
```

---

## 3. Input Validation and Sanitization Tests

### 3.1 SQL Injection Prevention

#### Test Case: `SEC-INJ-001: SQL Injection Prevention`

**Test Steps:**
```python
def test_sql_injection_prevention(self):
    """Test that SQL injection attacks are prevented"""
    
    sql_injection_payloads = [
        "'; DROP TABLE error_reports; --",
        "' OR '1'='1",
        "'; INSERT INTO error_reports (speaker_id) VALUES ('malicious'); --",
        "' UNION SELECT * FROM users --",
        "'; UPDATE speaker_performance_metrics SET rectification_rate = 0; --"
    ]
    
    for payload in sql_injection_payloads:
        # Test in speaker_id field
        malicious_data = {
            "job_id": "job-123",
            "speaker_id": payload,
            "bucket_type": "medium_touch",
            "original_text": "test",
            "corrected_text": "test"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/errors",
            json=malicious_data,
            headers=auth_headers
        )
        
        # Should either reject with validation error or sanitize input
        assert response.status_code in [400, 422]
        
        # Verify database integrity
        db_integrity_check = check_database_integrity()
        assert db_integrity_check["tables_exist"]
        assert db_integrity_check["data_consistent"]
```

### 3.2 XSS Prevention

#### Test Case: `SEC-XSS-001: Cross-Site Scripting Prevention`

**Test Steps:**
```python
def test_xss_prevention(self):
    """Test that XSS attacks are prevented"""
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "';alert('XSS');//"
    ]
    
    for payload in xss_payloads:
        # Test in additional_notes field
        malicious_data = {
            "job_id": "job-123",
            "speaker_id": "speaker-456",
            "bucket_type": "medium_touch",
            "metadata": {
                "additional_notes": payload
            }
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/errors",
            json=malicious_data,
            headers=auth_headers
        )
        
        if response.status_code == 201:
            # If accepted, verify output is sanitized
            error_id = response.json()["error_id"]
            get_response = requests.get(
                f"http://localhost:8000/api/v1/errors/{error_id}",
                headers=auth_headers
            )
            
            returned_notes = get_response.json()["metadata"]["additional_notes"]
            
            # Script tags should be escaped or removed
            assert "<script>" not in returned_notes
            assert "javascript:" not in returned_notes
            assert "onerror=" not in returned_notes
```

---

## 4. Copy-Paste Restriction Security Tests

### 4.1 Frontend Copy-Paste Prevention

#### Test Case: `SEC-COPY-001: Copy-Paste Restriction Enforcement`

**Test Steps:**
```typescript
// playwright-security-test.ts
import { test, expect } from '@playwright/test';

test('Copy-paste restrictions are enforced', async ({ page }) => {
  await page.goto('/error-reporting');
  
  // Test copy prevention
  await page.locator('[data-testid="selectable-text"]').selectText();
  
  // Attempt to copy using keyboard shortcut
  await page.keyboard.press('Control+C');
  
  // Verify copy warning appears
  await expect(page.locator('[data-testid="copy-warning"]')).toBeVisible();
  await expect(page.locator('[data-testid="copy-warning"]')).toContainText(
    'Copy operation is not allowed'
  );
  
  // Test paste prevention
  await page.fill('[data-testid="correction-input"]', '');
  await page.keyboard.press('Control+V');
  
  // Verify paste is blocked
  await expect(page.locator('[data-testid="correction-input"]')).toHaveValue('');
  await expect(page.locator('[data-testid="paste-warning"]')).toBeVisible();
  
  // Test right-click context menu disabled
  await page.locator('[data-testid="selectable-text"]').click({ button: 'right' });
  await expect(page.locator('.context-menu')).not.toBeVisible();
  
  // Test drag and drop prevention
  const sourceElement = page.locator('[data-testid="selectable-text"]');
  const targetElement = page.locator('[data-testid="correction-input"]');
  
  await sourceElement.dragTo(targetElement);
  
  // Verify drag and drop is blocked
  await expect(page.locator('[data-testid="drag-warning"]')).toBeVisible();
  await expect(targetElement).toHaveValue('');
});
```

### 4.2 Browser Developer Tools Detection

#### Test Case: `SEC-DEV-001: Developer Tools Detection`

**Test Steps:**
```typescript
test('Developer tools usage detection', async ({ page }) => {
  await page.goto('/error-reporting');
  
  // Simulate developer tools opening
  await page.evaluate(() => {
    // Trigger developer tools detection
    const devtools = {
      open: true,
      orientation: 'vertical'
    };
    window.dispatchEvent(new CustomEvent('devtoolschange', { detail: devtools }));
  });
  
  // Verify warning message appears
  await expect(page.locator('[data-testid="devtools-warning"]')).toBeVisible();
  await expect(page.locator('[data-testid="devtools-warning"]')).toContainText(
    'Developer tools detected. This action has been logged for security purposes.'
  );
  
  // Verify audit log entry is created
  const auditLogs = await page.evaluate(() => {
    return window.localStorage.getItem('security_audit_log');
  });
  
  expect(auditLogs).toContain('devtools_opened');
});
```

---

## 5. API Security Tests

### 5.1 Rate Limiting Security

#### Test Case: `SEC-RATE-001: Rate Limiting Protection`

**Test Steps:**
```python
def test_rate_limiting_protection(self):
    """Test that rate limiting prevents abuse"""
    
    # Make rapid requests to trigger rate limiting
    responses = []
    for i in range(150):  # Exceed rate limit
        response = requests.post(
            "http://localhost:8000/api/v1/errors",
            json={
                "job_id": f"job-{i}",
                "speaker_id": "speaker-123",
                "bucket_type": "medium_touch"
            },
            headers=auth_headers
        )
        responses.append(response)
    
    # Verify rate limiting is triggered
    rate_limited_responses = [r for r in responses if r.status_code == 429]
    assert len(rate_limited_responses) > 0
    
    # Verify rate limit headers
    rate_limit_response = rate_limited_responses[0]
    assert "X-RateLimit-Limit" in rate_limit_response.headers
    assert "X-RateLimit-Remaining" in rate_limit_response.headers
    assert "Retry-After" in rate_limit_response.headers
```

### 5.2 CORS Security

#### Test Case: `SEC-CORS-001: CORS Configuration Security`

**Test Steps:**
```python
def test_cors_security(self):
    """Test that CORS is properly configured"""
    
    # Test allowed origins
    allowed_origins = [
        "https://rag-interface.example.com",
        "https://localhost:5173"
    ]
    
    for origin in allowed_origins:
        response = requests.options(
            "http://localhost:8000/api/v1/errors",
            headers={"Origin": origin}
        )
        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == origin
    
    # Test blocked origins
    blocked_origins = [
        "https://malicious-site.com",
        "http://localhost:3000",
        "https://evil.example.com"
    ]
    
    for origin in blocked_origins:
        response = requests.options(
            "http://localhost:8000/api/v1/errors",
            headers={"Origin": origin}
        )
        assert "Access-Control-Allow-Origin" not in response.headers or \
               response.headers.get("Access-Control-Allow-Origin") != origin
```

---

## 6. Compliance and Audit Tests

### 6.1 HIPAA Compliance Tests

#### Test Case: `SEC-HIPAA-001: HIPAA Compliance Validation`

**Test Steps:**
```python
def test_hipaa_compliance(self):
    """Test HIPAA compliance requirements"""
    
    # Test audit logging
    response = requests.post(
        "http://localhost:8000/api/v1/errors",
        json={
            "job_id": "job-123",
            "speaker_id": "speaker-456",
            "metadata": {
                "additional_notes": "Patient medical information"
            }
        },
        headers=auth_headers
    )
    
    # Verify audit log entry
    audit_logs = get_audit_logs()
    latest_log = audit_logs[-1]
    
    assert latest_log["action"] == "error_report_created"
    assert latest_log["user_id"] == "test-user"
    assert latest_log["timestamp"] is not None
    assert latest_log["ip_address"] is not None
    assert "medical information" not in latest_log["details"]  # PHI not logged
    
    # Test data retention policies
    old_data = create_test_data_older_than(days=2555)  # 7 years + 1 day
    cleanup_response = requests.post(
        "http://localhost:8000/api/v1/admin/cleanup-expired-data",
        headers=admin_headers
    )
    
    assert cleanup_response.status_code == 200
    assert cleanup_response.json()["records_deleted"] > 0
```

### 6.2 Data Access Audit

#### Test Case: `SEC-AUDIT-001: Data Access Auditing`

**Test Steps:**
```python
def test_data_access_auditing(self):
    """Test that all data access is properly audited"""
    
    # Access speaker history
    response = requests.get(
        "http://localhost:8000/api/v1/speakers/speaker-123/history",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Verify audit log entry
    audit_logs = get_audit_logs(action="data_access")
    latest_access_log = audit_logs[-1]
    
    assert latest_access_log["resource"] == "speaker_history"
    assert latest_access_log["resource_id"] == "speaker-123"
    assert latest_access_log["user_id"] == "test-user"
    assert latest_access_log["access_granted"] is True
    
    # Test unauthorized access attempt
    unauthorized_response = requests.get(
        "http://localhost:8000/api/v1/speakers/speaker-456/history",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert unauthorized_response.status_code == 401
    
    # Verify failed access is logged
    failed_access_logs = get_audit_logs(action="unauthorized_access_attempt")
    latest_failed_log = failed_access_logs[-1]
    
    assert latest_failed_log["resource"] == "speaker_history"
    assert latest_failed_log["resource_id"] == "speaker-456"
    assert latest_failed_log["access_granted"] is False
    assert latest_failed_log["failure_reason"] == "invalid_token"
```

---

## 7. Security Test Automation

### Test Execution Framework
```python
# security_test_runner.py
import pytest
import subprocess
import json
from typing import Dict, List

class SecurityTestRunner:
    def __init__(self):
        self.test_results = {}
    
    def run_owasp_zap_scan(self, target_url: str) -> Dict:
        """Run OWASP ZAP security scan"""
        
        zap_command = [
            "zap-baseline.py",
            "-t", target_url,
            "-J", "zap-report.json",
            "-r", "zap-report.html"
        ]
        
        result = subprocess.run(zap_command, capture_output=True, text=True)
        
        with open("zap-report.json", "r") as f:
            zap_results = json.load(f)
        
        return {
            "scan_status": "completed",
            "vulnerabilities_found": len(zap_results.get("alerts", [])),
            "high_risk": len([a for a in zap_results.get("alerts", []) if a["risk"] == "High"]),
            "medium_risk": len([a for a in zap_results.get("alerts", []) if a["risk"] == "Medium"]),
            "report_path": "zap-report.html"
        }
    
    def run_custom_security_tests(self) -> Dict:
        """Run custom security test suite"""
        
        result = pytest.main([
            "tests/security/",
            "--tb=short",
            "--json-report",
            "--json-report-file=security-test-results.json"
        ])
        
        with open("security-test-results.json", "r") as f:
            test_results = json.load(f)
        
        return {
            "tests_run": test_results["summary"]["total"],
            "tests_passed": test_results["summary"]["passed"],
            "tests_failed": test_results["summary"]["failed"],
            "security_issues": test_results["summary"]["failed"]
        }
    
    def generate_security_report(self) -> str:
        """Generate comprehensive security test report"""
        
        zap_results = self.run_owasp_zap_scan("http://localhost:8000")
        custom_results = self.run_custom_security_tests()
        
        report = f"""
        Security Test Report
        ===================
        
        OWASP ZAP Scan Results:
        - Vulnerabilities Found: {zap_results['vulnerabilities_found']}
        - High Risk: {zap_results['high_risk']}
        - Medium Risk: {zap_results['medium_risk']}
        
        Custom Security Tests:
        - Tests Run: {custom_results['tests_run']}
        - Tests Passed: {custom_results['tests_passed']}
        - Security Issues: {custom_results['security_issues']}
        
        Overall Security Status: {'PASS' if custom_results['security_issues'] == 0 and zap_results['high_risk'] == 0 else 'FAIL'}
        """
        
        return report

if __name__ == "__main__":
    runner = SecurityTestRunner()
    report = runner.generate_security_report()
    print(report)
```

### Continuous Security Testing
```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  security-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
        pip install pytest-security
    
    - name: Run security tests
      run: |
        python tests/security/security_test_runner.py
    
    - name: Upload security report
      uses: actions/upload-artifact@v3
      with:
        name: security-report
        path: security-test-results.json
```

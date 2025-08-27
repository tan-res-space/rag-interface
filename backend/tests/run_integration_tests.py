#!/usr/bin/env python3
"""
Comprehensive integration test runner for speaker bucket management system.
"""

import asyncio
import sys
import time
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pytest
import psutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    status: str  # passed, failed, skipped
    duration: float
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None


@dataclass
class TestSuite:
    """Test suite data structure."""
    name: str
    tests: List[TestResult]
    total_duration: float
    passed: int
    failed: int
    skipped: int
    coverage_percentage: Optional[float] = None


@dataclass
class TestReport:
    """Comprehensive test report."""
    timestamp: str
    total_duration: float
    test_suites: List[TestSuite]
    system_info: Dict[str, Any]
    performance_summary: Dict[str, Any]
    overall_status: str


class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.cpu_samples = []
        self.memory_samples = []
        self.monitoring = False
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.monitoring = True
        self.cpu_samples = []
        self.memory_samples = []
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.end_time = time.time()
        self.monitoring = False
        logger.info("Performance monitoring stopped")
    
    def sample_metrics(self):
        """Sample current system metrics."""
        if not self.monitoring:
            return
        
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            self.cpu_samples.append(cpu_percent)
            self.memory_samples.append(memory.percent)
        except Exception as e:
            logger.warning(f"Failed to sample metrics: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.cpu_samples or not self.memory_samples:
            return {}
        
        return {
            "duration": self.end_time - self.start_time if self.end_time else 0,
            "cpu_usage": {
                "average": sum(self.cpu_samples) / len(self.cpu_samples),
                "max": max(self.cpu_samples),
                "min": min(self.cpu_samples),
                "samples": len(self.cpu_samples)
            },
            "memory_usage": {
                "average": sum(self.memory_samples) / len(self.memory_samples),
                "max": max(self.memory_samples),
                "min": min(self.memory_samples),
                "samples": len(self.memory_samples)
            }
        }


class IntegrationTestRunner:
    """Main integration test runner."""
    
    def __init__(self, test_dir: Path = None):
        self.test_dir = test_dir or Path(__file__).parent / "integration"
        self.performance_monitor = PerformanceMonitor()
        self.test_results: List[TestSuite] = []
    
    async def run_test_suite(self, suite_name: str, test_files: List[str]) -> TestSuite:
        """Run a specific test suite."""
        logger.info(f"Running test suite: {suite_name}")
        
        suite_start_time = time.time()
        test_results = []
        
        for test_file in test_files:
            test_path = self.test_dir / test_file
            if not test_path.exists():
                logger.warning(f"Test file not found: {test_path}")
                continue
            
            # Run pytest for this file
            result = await self._run_pytest(test_path)
            test_results.extend(result)
        
        suite_duration = time.time() - suite_start_time
        
        # Calculate suite statistics
        passed = sum(1 for t in test_results if t.status == "passed")
        failed = sum(1 for t in test_results if t.status == "failed")
        skipped = sum(1 for t in test_results if t.status == "skipped")
        
        return TestSuite(
            name=suite_name,
            tests=test_results,
            total_duration=suite_duration,
            passed=passed,
            failed=failed,
            skipped=skipped
        )
    
    async def _run_pytest(self, test_path: Path) -> List[TestResult]:
        """Run pytest for a specific test file."""
        logger.info(f"Running tests in: {test_path}")
        
        # Use pytest programmatically
        import subprocess
        
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=/tmp/pytest_report.json"
        ]
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test file
            )
            
            duration = time.time() - start_time
            
            # Parse pytest JSON report
            try:
                with open("/tmp/pytest_report.json", "r") as f:
                    pytest_report = json.load(f)
                
                return self._parse_pytest_report(pytest_report, duration)
            
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error(f"Failed to parse pytest report: {e}")
                return [TestResult(
                    test_name=str(test_path),
                    status="failed",
                    duration=duration,
                    error_message=f"Failed to parse test results: {e}"
                )]
        
        except subprocess.TimeoutExpired:
            return [TestResult(
                test_name=str(test_path),
                status="failed",
                duration=300,
                error_message="Test execution timed out"
            )]
        
        except Exception as e:
            return [TestResult(
                test_name=str(test_path),
                status="failed",
                duration=time.time() - start_time,
                error_message=str(e)
            )]
    
    def _parse_pytest_report(self, report: Dict, total_duration: float) -> List[TestResult]:
        """Parse pytest JSON report into TestResult objects."""
        results = []
        
        for test in report.get("tests", []):
            test_result = TestResult(
                test_name=test.get("nodeid", "unknown"),
                status=test.get("outcome", "unknown"),
                duration=test.get("duration", 0),
                error_message=test.get("call", {}).get("longrepr") if test.get("outcome") == "failed" else None
            )
            results.append(test_result)
        
        return results
    
    async def run_all_tests(self, include_performance: bool = True) -> TestReport:
        """Run all integration tests."""
        logger.info("Starting comprehensive integration test run")
        
        if include_performance:
            self.performance_monitor.start_monitoring()
        
        start_time = time.time()
        
        # Define test suites
        test_suites_config = {
            "Speaker Management": [
                "test_speaker_management_workflow.py"
            ],
            "RAG Processing": [
                "test_rag_processing_workflow.py"
            ],
            "MT Validation": [
                "test_mt_validation_workflow.py"
            ],
            "End-to-End": [
                "test_end_to_end_workflow.py"
            ]
        }
        
        # Run test suites
        test_suites = []
        for suite_name, test_files in test_suites_config.items():
            try:
                suite_result = await self.run_test_suite(suite_name, test_files)
                test_suites.append(suite_result)
                
                # Sample performance metrics
                if include_performance:
                    self.performance_monitor.sample_metrics()
                
            except Exception as e:
                logger.error(f"Failed to run test suite {suite_name}: {e}")
                # Create failed suite
                failed_suite = TestSuite(
                    name=suite_name,
                    tests=[TestResult(
                        test_name=suite_name,
                        status="failed",
                        duration=0,
                        error_message=str(e)
                    )],
                    total_duration=0,
                    passed=0,
                    failed=1,
                    skipped=0
                )
                test_suites.append(failed_suite)
        
        total_duration = time.time() - start_time
        
        if include_performance:
            self.performance_monitor.stop_monitoring()
        
        # Calculate overall statistics
        total_passed = sum(suite.passed for suite in test_suites)
        total_failed = sum(suite.failed for suite in test_suites)
        total_skipped = sum(suite.skipped for suite in test_suites)
        
        overall_status = "passed" if total_failed == 0 else "failed"
        
        # Generate report
        report = TestReport(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_duration=total_duration,
            test_suites=test_suites,
            system_info=self._get_system_info(),
            performance_summary=self.performance_monitor.get_summary() if include_performance else {},
            overall_status=overall_status
        )
        
        return report
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            return {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_usage_gb": round(psutil.disk_usage("/").total / (1024**3), 2)
            }
        except Exception as e:
            logger.warning(f"Failed to get system info: {e}")
            return {"error": str(e)}
    
    def generate_report(self, report: TestReport, output_file: Optional[Path] = None) -> str:
        """Generate human-readable test report."""
        lines = []
        lines.append("=" * 80)
        lines.append("SPEAKER BUCKET MANAGEMENT - INTEGRATION TEST REPORT")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {report.timestamp}")
        lines.append(f"Total Duration: {report.total_duration:.2f} seconds")
        lines.append(f"Overall Status: {report.overall_status.upper()}")
        lines.append("")
        
        # System Information
        lines.append("SYSTEM INFORMATION")
        lines.append("-" * 40)
        for key, value in report.system_info.items():
            lines.append(f"{key}: {value}")
        lines.append("")
        
        # Performance Summary
        if report.performance_summary:
            lines.append("PERFORMANCE SUMMARY")
            lines.append("-" * 40)
            perf = report.performance_summary
            lines.append(f"Test Duration: {perf.get('duration', 0):.2f} seconds")
            
            if 'cpu_usage' in perf:
                cpu = perf['cpu_usage']
                lines.append(f"CPU Usage - Avg: {cpu['average']:.1f}%, Max: {cpu['max']:.1f}%")
            
            if 'memory_usage' in perf:
                mem = perf['memory_usage']
                lines.append(f"Memory Usage - Avg: {mem['average']:.1f}%, Max: {mem['max']:.1f}%")
            lines.append("")
        
        # Test Suite Results
        lines.append("TEST SUITE RESULTS")
        lines.append("-" * 40)
        
        for suite in report.test_suites:
            lines.append(f"\n{suite.name}:")
            lines.append(f"  Duration: {suite.total_duration:.2f}s")
            lines.append(f"  Passed: {suite.passed}")
            lines.append(f"  Failed: {suite.failed}")
            lines.append(f"  Skipped: {suite.skipped}")
            
            if suite.failed > 0:
                lines.append("  Failed Tests:")
                for test in suite.tests:
                    if test.status == "failed":
                        lines.append(f"    - {test.test_name}")
                        if test.error_message:
                            lines.append(f"      Error: {test.error_message[:100]}...")
        
        # Summary
        total_tests = sum(len(suite.tests) for suite in report.test_suites)
        total_passed = sum(suite.passed for suite in report.test_suites)
        total_failed = sum(suite.failed for suite in report.test_suites)
        total_skipped = sum(suite.skipped for suite in report.test_suites)
        
        lines.append("\nOVERALL SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Tests: {total_tests}")
        lines.append(f"Passed: {total_passed}")
        lines.append(f"Failed: {total_failed}")
        lines.append(f"Skipped: {total_skipped}")
        lines.append(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        lines.append("=" * 80)
        
        report_text = "\n".join(lines)
        
        # Save to file if specified
        if output_file:
            output_file.write_text(report_text)
            logger.info(f"Report saved to: {output_file}")
        
        return report_text


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run integration tests for speaker bucket management")
    parser.add_argument("--output", "-o", type=Path, help="Output file for test report")
    parser.add_argument("--no-performance", action="store_true", help="Disable performance monitoring")
    parser.add_argument("--suite", "-s", help="Run specific test suite only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize test runner
    runner = IntegrationTestRunner()
    
    try:
        # Run tests
        if args.suite:
            # Run specific suite
            test_files = {
                "speaker": ["test_speaker_management_workflow.py"],
                "rag": ["test_rag_processing_workflow.py"],
                "mt": ["test_mt_validation_workflow.py"],
                "e2e": ["test_end_to_end_workflow.py"]
            }.get(args.suite.lower(), [])
            
            if not test_files:
                logger.error(f"Unknown test suite: {args.suite}")
                sys.exit(1)
            
            suite_result = await runner.run_test_suite(args.suite, test_files)
            
            # Create minimal report
            report = TestReport(
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                total_duration=suite_result.total_duration,
                test_suites=[suite_result],
                system_info=runner._get_system_info(),
                performance_summary={},
                overall_status="passed" if suite_result.failed == 0 else "failed"
            )
        else:
            # Run all tests
            report = await runner.run_all_tests(include_performance=not args.no_performance)
        
        # Generate and display report
        report_text = runner.generate_report(report, args.output)
        print(report_text)
        
        # Exit with appropriate code
        sys.exit(0 if report.overall_status == "passed" else 1)
        
    except KeyboardInterrupt:
        logger.info("Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

/**
 * Critical Bug Test Runner
 * 
 * Runs comprehensive tests for the Error Reporting Step 4 critical bug
 * and generates detailed reports.
 */

import { execSync } from 'child_process';
import { writeFileSync, readFileSync, existsSync } from 'fs';
import { join } from 'path';

interface TestResult {
  testName: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
  consoleErrors?: string[];
  networkErrors?: string[];
}

interface TestReport {
  timestamp: string;
  totalTests: number;
  passed: number;
  failed: number;
  skipped: number;
  criticalBugFixed: boolean;
  results: TestResult[];
  summary: string;
}

class CriticalBugTestRunner {
  private results: TestResult[] = [];
  private startTime: number = 0;

  async runTests(): Promise<TestReport> {
    console.log('🚀 Starting Critical Bug Investigation Tests...');
    this.startTime = Date.now();

    try {
      // Run critical bug tests
      await this.runCriticalBugTests();
      
      // Run backend integration tests
      await this.runBackendIntegrationTests();
      
      // Generate report
      const report = this.generateReport();
      
      // Save report
      this.saveReport(report);
      
      return report;
    } catch (error) {
      console.error('❌ Test execution failed:', error);
      throw error;
    }
  }

  private async runCriticalBugTests(): Promise<void> {
    console.log('🔍 Running Critical Bug Tests...');
    
    try {
      const output = execSync(
        'npx playwright test error-reporting-critical-bug.spec.ts --reporter=json',
        { 
          cwd: process.cwd(),
          encoding: 'utf8',
          timeout: 300000 // 5 minutes
        }
      );
      
      this.parsePlaywrightOutput(output, 'Critical Bug');
    } catch (error: any) {
      console.log('⚠️ Critical bug tests completed with issues');
      if (error.stdout) {
        this.parsePlaywrightOutput(error.stdout, 'Critical Bug');
      }
    }
  }

  private async runBackendIntegrationTests(): Promise<void> {
    console.log('🔗 Running Backend Integration Tests...');
    
    try {
      const output = execSync(
        'npx playwright test error-reporting-backend-integration.spec.ts --reporter=json',
        { 
          cwd: process.cwd(),
          encoding: 'utf8',
          timeout: 300000 // 5 minutes
        }
      );
      
      this.parsePlaywrightOutput(output, 'Backend Integration');
    } catch (error: any) {
      console.log('⚠️ Backend integration tests completed with issues');
      if (error.stdout) {
        this.parsePlaywrightOutput(error.stdout, 'Backend Integration');
      }
    }
  }

  private parsePlaywrightOutput(output: string, testType: string): void {
    try {
      const jsonOutput = JSON.parse(output);
      
      if (jsonOutput.suites) {
        jsonOutput.suites.forEach((suite: any) => {
          suite.specs?.forEach((spec: any) => {
            spec.tests?.forEach((test: any) => {
              const result: TestResult = {
                testName: `${testType}: ${test.title}`,
                status: this.mapPlaywrightStatus(test.results?.[0]?.status),
                duration: test.results?.[0]?.duration || 0,
                error: test.results?.[0]?.error?.message
              };
              
              this.results.push(result);
            });
          });
        });
      }
    } catch (error) {
      console.log('⚠️ Could not parse test output as JSON, treating as text output');
      // Fallback to text parsing
      this.parseTextOutput(output, testType);
    }
  }

  private parseTextOutput(output: string, testType: string): void {
    const lines = output.split('\n');
    let currentTest = '';
    
    lines.forEach(line => {
      if (line.includes('✓') || line.includes('✗') || line.includes('○')) {
        const status = line.includes('✓') ? 'passed' : 
                     line.includes('✗') ? 'failed' : 'skipped';
        
        const testName = line.replace(/[✓✗○]\s*/, '').trim();
        
        this.results.push({
          testName: `${testType}: ${testName}`,
          status: status as 'passed' | 'failed' | 'skipped',
          duration: 0
        });
      }
    });
  }

  private mapPlaywrightStatus(status: string): 'passed' | 'failed' | 'skipped' {
    switch (status) {
      case 'passed': return 'passed';
      case 'failed': return 'failed';
      case 'skipped': return 'skipped';
      default: return 'failed';
    }
  }

  private generateReport(): TestReport {
    const totalTests = this.results.length;
    const passed = this.results.filter(r => r.status === 'passed').length;
    const failed = this.results.filter(r => r.status === 'failed').length;
    const skipped = this.results.filter(r => r.status === 'skipped').length;

    // Check if critical bug is fixed
    const criticalBugTest = this.results.find(r => 
      r.testName.includes('CRITICAL') && r.testName.includes('Step 4 to Step 5')
    );
    const criticalBugFixed = criticalBugTest?.status === 'passed';

    const summary = this.generateSummary(totalTests, passed, failed, skipped, criticalBugFixed);

    return {
      timestamp: new Date().toISOString(),
      totalTests,
      passed,
      failed,
      skipped,
      criticalBugFixed,
      results: this.results,
      summary
    };
  }

  private generateSummary(total: number, passed: number, failed: number, skipped: number, criticalBugFixed: boolean): string {
    const duration = Date.now() - this.startTime;
    
    let summary = `
🧪 ERROR REPORTING CRITICAL BUG TEST REPORT
============================================

📊 Test Results:
- Total Tests: ${total}
- Passed: ${passed} ✅
- Failed: ${failed} ❌
- Skipped: ${skipped} ⏭️
- Duration: ${Math.round(duration / 1000)}s

🎯 Critical Bug Status: ${criticalBugFixed ? 'FIXED ✅' : 'NOT FIXED ❌'}

`;

    if (criticalBugFixed) {
      summary += `
✅ SUCCESS: The critical bug in Step 4 "Next" button has been resolved!
The transition from "Add Context" to "Review & Submit" is working correctly.

`;
    } else {
      summary += `
❌ ISSUE: The critical bug in Step 4 "Next" button is still present.
The transition from "Add Context" to "Review & Submit" is failing.

`;
    }

    // Add failed test details
    const failedTests = this.results.filter(r => r.status === 'failed');
    if (failedTests.length > 0) {
      summary += `
🔍 Failed Tests Details:
`;
      failedTests.forEach(test => {
        summary += `- ${test.testName}\n`;
        if (test.error) {
          summary += `  Error: ${test.error}\n`;
        }
      });
    }

    // Add recommendations
    summary += `
📋 Recommendations:
`;

    if (!criticalBugFixed) {
      summary += `
1. Check EnhancedMetadataInput component validation logic
2. Verify bucket type selection is properly handled
3. Check for JavaScript console errors during Step 4 transition
4. Validate form data structure matches backend expectations
5. Test with different bucket type selections
`;
    } else {
      summary += `
1. Continue monitoring Step 4 transitions in production
2. Add automated regression tests for bucket type functionality
3. Verify backend integration with new bucket types
4. Test edge cases with missing or invalid data
`;
    }

    return summary;
  }

  private saveReport(report: TestReport): void {
    const reportPath = join(process.cwd(), 'playwright-report', 'critical-bug-report.json');
    const summaryPath = join(process.cwd(), 'playwright-report', 'critical-bug-summary.txt');
    
    try {
      writeFileSync(reportPath, JSON.stringify(report, null, 2));
      writeFileSync(summaryPath, report.summary);
      
      console.log(`📄 Report saved to: ${reportPath}`);
      console.log(`📄 Summary saved to: ${summaryPath}`);
    } catch (error) {
      console.error('❌ Failed to save report:', error);
    }
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  const runner = new CriticalBugTestRunner();
  
  runner.runTests()
    .then(report => {
      console.log(report.summary);
      process.exit(report.criticalBugFixed ? 0 : 1);
    })
    .catch(error => {
      console.error('❌ Test execution failed:', error);
      process.exit(1);
    });
}

export { CriticalBugTestRunner, TestResult, TestReport };

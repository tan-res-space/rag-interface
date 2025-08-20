/**
 * Simple domain types tests
 */

import { describe, it, expect } from 'vitest';
import { UserRole, UserStatus, SeverityLevel, ErrorStatus } from '@domain/types';

describe('Domain Types', () => {
  it('should have correct UserRole enum values', () => {
    expect(UserRole.ADMIN).toBe('admin');
    expect(UserRole.QA_SUPERVISOR).toBe('qa_supervisor');
    expect(UserRole.QA_PERSONNEL).toBe('qa_personnel');
    expect(UserRole.MTS_PERSONNEL).toBe('mts_personnel');
    expect(UserRole.VIEWER).toBe('viewer');
  });

  it('should have correct UserStatus enum values', () => {
    expect(UserStatus.ACTIVE).toBe('active');
    expect(UserStatus.INACTIVE).toBe('inactive');
    expect(UserStatus.SUSPENDED).toBe('suspended');
    expect(UserStatus.PENDING).toBe('pending');
  });

  it('should have correct SeverityLevel enum values', () => {
    expect(SeverityLevel.LOW).toBe('low');
    expect(SeverityLevel.MEDIUM).toBe('medium');
    expect(SeverityLevel.HIGH).toBe('high');
    expect(SeverityLevel.CRITICAL).toBe('critical');
  });

  it('should have correct ErrorStatus enum values', () => {
    expect(ErrorStatus.PENDING).toBe('pending');
    expect(ErrorStatus.PROCESSED).toBe('processed');
    expect(ErrorStatus.ARCHIVED).toBe('archived');
  });
});

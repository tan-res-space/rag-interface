/**
 * User domain types based on User Management Service schemas
 */

export enum UserRole {
  ADMIN = 'admin',
  QA_SUPERVISOR = 'qa_supervisor',
  QA_PERSONNEL = 'qa_personnel',
  MTS_PERSONNEL = 'mts_personnel',
  VIEWER = 'viewer',
}

export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  SUSPENDED = 'suspended',
  PENDING = 'pending',
}

export interface User {
  userId: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  roles: UserRole[];
  permissions: string[];
  status: UserStatus;
  department?: string;
  phoneNumber?: string;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
  isActive: boolean;
  metadata?: Record<string, any>;
}

export interface AuthenticationRequest {
  username: string;
  password: string;
  ipAddress?: string;
  userAgent?: string;
}

export interface AuthenticationResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
  user: User;
}

export interface TokenValidationResponse {
  valid: boolean;
  userId?: string;
  username?: string;
  permissions: string[];
  expiresAt?: string;
  message: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  roles: UserRole[];
  department?: string;
  phoneNumber?: string;
  metadata?: Record<string, any>;
}

export interface UpdateUserRequest {
  userId: string;
  firstName?: string;
  lastName?: string;
  email?: string;
  department?: string;
  phoneNumber?: string;
  metadata?: Record<string, any>;
}

export interface ChangePasswordRequest {
  userId: string;
  currentPassword: string;
  newPassword: string;
}

export interface UserAuditLogEntry {
  id: string;
  userId: string;
  action: string;
  details: Record<string, any>;
  performedBy: string;
  timestamp: string;
  ipAddress?: string;
  userAgent?: string;
}

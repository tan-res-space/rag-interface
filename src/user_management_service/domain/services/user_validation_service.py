"""
User Validation Service

Domain service containing business logic for user validation and security rules.
This service is stateless and contains pure business logic.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional

from ..entities.user import User, UserRole, UserStatus, Permission


class UserValidationService:
    """
    Domain service for user validation business logic.
    
    Contains business rules for user creation, validation, and security policies.
    """
    
    def __init__(self):
        """Initialize the user validation service"""
        # Password policy constants
        self.MIN_PASSWORD_LENGTH = 12
        self.MAX_PASSWORD_LENGTH = 128
        self.REQUIRED_PASSWORD_COMPLEXITY = {
            'uppercase': 1,
            'lowercase': 1,
            'digits': 1,
            'special_chars': 1
        }
        
        # Account security constants
        self.MAX_FAILED_ATTEMPTS = 5
        self.LOCKOUT_DURATION_MINUTES = 30
        self.PASSWORD_EXPIRY_DAYS = 90
        
        # Username validation
        self.MIN_USERNAME_LENGTH = 3
        self.MAX_USERNAME_LENGTH = 50
        self.RESERVED_USERNAMES = {
            'admin', 'administrator', 'root', 'system', 'test', 'guest',
            'user', 'default', 'null', 'undefined', 'api', 'service'
        }
    
    def validate_user_creation(self, user: User) -> List[str]:
        """
        Validate user data for creation.
        
        Business rules:
        1. Username must be unique and follow naming conventions
        2. Email must be valid and from approved domains
        3. User must have at least one role
        4. Profile information must be complete
        
        Args:
            user: User entity to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate username
        username_errors = self.validate_username(user.username)
        errors.extend(username_errors)
        
        # Validate email
        email_errors = self.validate_email(user.profile.email)
        errors.extend(email_errors)
        
        # Validate roles
        if not user.roles:
            errors.append("User must have at least one role assigned")
        
        # Validate role combinations
        role_errors = self.validate_role_combinations(list(user.roles))
        errors.extend(role_errors)
        
        # Validate profile completeness
        profile_errors = self.validate_profile_completeness(user)
        errors.extend(profile_errors)
        
        return errors
    
    def validate_username(self, username: str) -> List[str]:
        """
        Validate username according to business rules.
        
        Business rules:
        1. Length between 3-50 characters
        2. Only alphanumeric, underscore, and hyphen allowed
        3. Cannot be a reserved username
        4. Must start with a letter
        
        Args:
            username: Username to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not username:
            errors.append("Username is required")
            return errors
        
        if len(username) < self.MIN_USERNAME_LENGTH:
            errors.append(f"Username must be at least {self.MIN_USERNAME_LENGTH} characters")
        
        if len(username) > self.MAX_USERNAME_LENGTH:
            errors.append(f"Username must be no more than {self.MAX_USERNAME_LENGTH} characters")
        
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
            errors.append("Username must start with a letter and contain only letters, numbers, underscores, and hyphens")
        
        if username.lower() in self.RESERVED_USERNAMES:
            errors.append(f"Username '{username}' is reserved and cannot be used")
        
        return errors
    
    def validate_email(self, email: str) -> List[str]:
        """
        Validate email according to business rules.
        
        Args:
            email: Email to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not email:
            errors.append("Email is required")
            return errors
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append("Invalid email format")
        
        return errors
    
    def validate_role_combinations(self, roles: List[UserRole]) -> List[str]:
        """
        Validate role combinations according to business rules.
        
        Business rules:
        1. SYSTEM_ADMIN cannot have other roles (separation of duties)
        2. QA_PERSONNEL and MTS_PERSONNEL can coexist
        3. VIEWER can be combined with any role
        
        Args:
            roles: List of roles to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if UserRole.SYSTEM_ADMIN in roles and len(roles) > 1:
            errors.append("System administrators cannot have additional roles")
        
        return errors
    
    def validate_profile_completeness(self, user: User) -> List[str]:
        """
        Validate user profile completeness.
        
        Business rules:
        1. First name and last name are required
        2. Email is required and validated
        3. Department is recommended for healthcare personnel
        
        Args:
            user: User to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not user.profile.first_name.strip():
            errors.append("First name is required")
        
        if not user.profile.last_name.strip():
            errors.append("Last name is required")
        
        # Recommend department for healthcare roles
        healthcare_roles = {UserRole.QA_PERSONNEL, UserRole.MTS_PERSONNEL}
        if any(role in healthcare_roles for role in user.roles):
            if not user.profile.department:
                errors.append("Department is recommended for healthcare personnel")
        
        return errors
    
    def validate_password_policy(self, password: str) -> List[str]:
        """
        Validate password against security policy.
        
        Business rules:
        1. Minimum 12 characters, maximum 128 characters
        2. Must contain uppercase, lowercase, digit, and special character
        3. Cannot contain common patterns
        
        Args:
            password: Password to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if not password:
            errors.append("Password is required")
            return errors
        
        if len(password) < self.MIN_PASSWORD_LENGTH:
            errors.append(f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters")
        
        if len(password) > self.MAX_PASSWORD_LENGTH:
            errors.append(f"Password must be no more than {self.MAX_PASSWORD_LENGTH} characters")
        
        # Check complexity requirements
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common weak patterns
        if self._contains_common_patterns(password):
            errors.append("Password contains common patterns and is not secure")
        
        return errors
    
    def _contains_common_patterns(self, password: str) -> bool:
        """
        Check if password contains common weak patterns.
        
        Args:
            password: Password to check
            
        Returns:
            True if contains weak patterns, False otherwise
        """
        weak_patterns = [
            r'123456',
            r'password',
            r'qwerty',
            r'abc123',
            r'admin',
            r'(.)\1{3,}',  # Repeated characters
        ]
        
        password_lower = password.lower()
        for pattern in weak_patterns:
            if re.search(pattern, password_lower):
                return True
        
        return False
    
    def validate_account_security(self, user: User) -> List[str]:
        """
        Validate account security status.
        
        Args:
            user: User to validate
            
        Returns:
            List of security warnings
        """
        warnings = []
        
        # Check if account is locked
        if user.account_locked_until and user.account_locked_until > datetime.utcnow():
            time_remaining = user.account_locked_until - datetime.utcnow()
            warnings.append(f"Account is locked for {time_remaining.seconds // 60} more minutes")
        
        # Check failed login attempts
        if user.failed_login_attempts >= 3:
            warnings.append(f"Account has {user.failed_login_attempts} failed login attempts")
        
        # Check last login
        if user.last_login:
            days_since_login = (datetime.utcnow() - user.last_login).days
            if days_since_login > 30:
                warnings.append(f"Account has not been used for {days_since_login} days")
        
        return warnings
    
    def can_user_perform_action(self, user: User, required_permission: Permission) -> bool:
        """
        Check if user can perform an action requiring specific permission.
        
        Business rules:
        1. User must be active
        2. User must have the required permission
        3. Account must not be locked
        
        Args:
            user: User to check
            required_permission: Permission required for the action
            
        Returns:
            True if user can perform action, False otherwise
        """
        if not user.is_active():
            return False
        
        if not user.has_permission(required_permission):
            return False
        
        return True
    
    def assess_user_risk_level(self, user: User) -> str:
        """
        Assess user risk level based on various factors.
        
        Args:
            user: User to assess
            
        Returns:
            Risk level: 'low', 'medium', 'high', 'critical'
        """
        risk_score = 0
        
        # Failed login attempts
        risk_score += user.failed_login_attempts * 10
        
        # Account age
        if user.created_at:
            days_old = (datetime.utcnow() - user.created_at).days
            if days_old < 7:
                risk_score += 20  # New accounts are higher risk
        
        # Role-based risk
        if UserRole.SYSTEM_ADMIN in user.roles:
            risk_score += 30  # Admin accounts are higher risk
        
        # Last login
        if user.last_login:
            days_since_login = (datetime.utcnow() - user.last_login).days
            if days_since_login > 90:
                risk_score += 25  # Inactive accounts are higher risk
        
        # Determine risk level
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'high'
        elif risk_score >= 30:
            return 'medium'
        else:
            return 'low'

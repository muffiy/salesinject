# Password-Based Authentication Design

## Overview
Implement password-based authentication alongside existing Telegram authentication to allow users to log in using phone number and password credentials.

## Requirements
- Support phone number + password authentication
- Store credentials securely in a separate table
- Maintain compatibility with existing Telegram auth
- Follow security best practices for password storage

## Architecture

### Components
1. **User Model** - Extended with phone_number column
2. **UserCredentials Model** - New table for password hashes
3. **Auth Endpoints** - New /auth/password-login endpoint
4. **Password Service** - Handles hashing and verification

### Data Flow
1. User submits phone number and password to /auth/password-login
2. Service looks up user by phone_number
3. Retrieves credentials from user_credentials table
4. Verifies password hash using bcrypt
5. Returns JWT token on success

### Security Considerations
- Use bcrypt for password hashing with appropriate work factor
- Store only password hashes, never plaintext passwords
- Implement rate limiting on auth endpoints
- Use secure, HTTP-only cookies for token storage (if applicable)
- Validate phone number format

## Database Schema

### Users Table (Extended)
```sql
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) UNIQUE;
```

### UserCredentials Table (New)
```sql
CREATE TABLE user_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);
```

## API Endpoints

### POST /auth/password-login
```json
{
  "phone_number": "+1234567890",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "jwt.token.here",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "phone_number": "+1234567890",
    "username": "optional_username"
  }
}
```

## Implementation Plan

### Phase 1: Database Changes
1. Add phone_number column to users table
2. Create user_credentials table
3. Create migration scripts

### Phase 2: Service Layer
1. Create password hashing service using bcrypt
2. Create credential repository for DB operations
3. Create authentication service

### Phase 3: API Layer
1. Implement /auth/password-login endpoint
2. Add input validation and error handling
3. Integrate with existing token generation

### Phase 4: Security
1. Implement rate limiting on auth endpoints
2. Add phone number validation
3. Set appropriate bcrypt work factor

## Error Handling
- Invalid phone number format: 400 Bad Request
- User not found: 401 Unauthorized (generic message to prevent enumeration)
- Invalid password: 401 Unauthorized
- Server errors: 500 Internal Server Error

## Testing Strategy
1. Unit tests for password hashing service
2. Integration tests for credential storage/retrieval
3. API endpoint tests for success and failure cases
4. Security tests for common vulnerabilities

## Dependencies
- bcrypt library for password hashing
- Existing JWT token generation infrastructure
- SQLAlchemy for ORM operations

## Future Enhancements
- Password reset functionality
- Account lockout after failed attempts
- Multi-factor authentication option
- Password strength requirements
# Superuser Role System Setup

This document explains how to set up and use the superuser role system in the HRMS application.

## Overview

The HRMS application uses a role-based access control (RBAC) system where:
- **Superusers** are created via Django management commands (shell only)
- **Regular users** are created via API endpoints
- **Superuser role** contains all permissions and can be assigned to users
- **API routes** cannot create superusers for security reasons

## Initial Setup

### 1. Create Superuser Role

First, create the superuser role with all permissions:

```bash
python manage.py setup_superuser_role
```

This command will:
- Seed all permissions (if not already done)
- Create a "Superuser" role with all permissions
- Assign the superuser role to existing superusers

### 2. Create Your First Superuser

Create a superuser via management command:

```bash
python manage.py create_superuser \
  --email admin@yourcompany.com \
  --password YourSecurePassword123 \
  --first-name Admin \
  --last-name User
```

## Management Commands

### Available Commands

1. **Setup Superuser Role System**
   ```bash
   python manage.py setup_superuser_role [--force]
   ```
   - Creates superuser role with all permissions
   - Assigns role to existing superusers
   - Use `--force` to recreate the role

2. **Create Superuser Role Only**
   ```bash
   python manage.py create_superuser_role [--force]
   ```
   - Creates only the superuser role
   - Use `--force` to recreate if it exists

3. **Create New Superuser**
   ```bash
   python manage.py create_superuser \
     --email user@example.com \
     --password password123 \
     --first-name John \
     --last-name Doe
   ```
   - Creates a new superuser with superuser role

4. **Assign Superuser Role to Existing Users**
   ```bash
   python manage.py assign_superuser_role [--email user@example.com]
   ```
   - Assigns superuser role to existing superusers
   - Use `--email` to target a specific user

## API Endpoints

### User Management (Regular Users Only)

- **POST** `/api/v1/auth/register/` - Create regular user
- **GET** `/api/v1/auth/users/` - List users (superusers see all, others see only themselves)
- **GET** `/api/v1/auth/users/me/` - Get current user profile
- **POST** `/api/v1/auth/users/{id}/assign_roles/` - Assign roles to user

### Role Management

- **GET** `/api/v1/auth/roles/` - List all roles
- **POST** `/api/v1/auth/roles/` - Create new role
- **PUT** `/api/v1/auth/roles/{id}/` - Update role
- **DELETE** `/api/v1/auth/roles/{id}/` - Delete role

### Invitation Management

- **POST** `/api/v1/auth/invitations/` - Create invitation
- **GET** `/api/v1/auth/invitations/` - List invitations
- **POST** `/api/v1/auth/accept-invitation/` - Accept invitation

## Security Features

### Superuser Protection
- Superusers can only be created via management commands
- API endpoints cannot create superusers
- Regular user creation via API automatically sets `is_superuser=False`

### Role-Based Access
- Users with "Superuser" role have all permissions
- Regular users have permissions based on their assigned roles
- Effective superuser check: `user.is_effective_superuser()`

### Permission System
- All permissions are seeded via `seed_permissions` command
- Superuser role automatically gets all permissions
- Regular roles can be assigned specific permissions

## User Types

### 1. Django Superuser (`is_superuser=True`)
- Created via `python manage.py createsuperuser`
- Has Django admin access
- Has all permissions by default
- Should also have "Superuser" role for consistency

### 2. Superuser Role User
- Has "Superuser" role assigned
- Has all permissions via role
- May or may not be Django superuser
- Can be created via management command

### 3. Regular User
- Created via API endpoints
- Has specific roles assigned
- Permissions based on assigned roles
- Cannot access Django admin (unless `is_staff=True`)

## Best Practices

1. **Initial Setup**: Always run `setup_superuser_role` after deployment
2. **Superuser Creation**: Use management commands for superusers
3. **Regular Users**: Use API endpoints for regular users
4. **Role Assignment**: Assign appropriate roles to users based on their responsibilities
5. **Security**: Never create superusers via API endpoints

## Troubleshooting

### Superuser Role Not Found
```bash
python manage.py create_superuser_role
```

### Permissions Not Working
```bash
python manage.py seed_permissions
python manage.py assign_superuser_role
```

### User Can't Access Resources
- Check if user has appropriate role
- Verify role has required permissions
- Ensure user is not deactivated

## Example Workflow

1. **Initial Setup**:
   ```bash
   python manage.py migrate
   python manage.py setup_superuser_role
   python manage.py create_superuser --email admin@company.com --password admin123 --first-name Admin --last-name User
   ```

2. **Create Regular Users**:
   - Use API endpoint: `POST /api/v1/auth/register/`
   - Or invite via: `POST /api/v1/auth/invitations/`

3. **Assign Roles**:
   - Create roles via: `POST /api/v1/auth/roles/`
   - Assign roles via: `POST /api/v1/auth/users/{id}/assign_roles/`

This system ensures security while providing flexibility for user management.

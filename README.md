# Content Management System (CMS) API

## Table of Contents
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Authentication & User Management](#authentication--user-management)
  - [User Registration](#1-user-registration)
  - [User Login](#2-user-login)
  - [Obtain Token](#3-obtain-token)
  - [Refresh Token](#4-refresh-token)
  - [List Users](#5-list-users)
- [Content Management](#content-management)
  - [Create Content](#1-create-content)
  - [Update Content Status](#2-update-content-status)
  - [Approve Content](#3-approve-content)
- [Task Management](#task-management)
  - [Create Task](#1-create-task)
  - [List Tasks](#2-list-tasks)
  - [Get Task Details](#3-get-task-details)
- [Authentication Headers](#authentication-headers)
- [Status Codes](#status-codes)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository
```bash
git clone 
cd 
```

2. Create and activate virtual environment

For Windows:
```bash
python -m venv virtual_env_name
cd virtual_env_name\Scripts\activate
```

For Unix/MacOS:
```bash
python -m venv virtual_env_name
source virtual_env_name/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Authentication & User Management

### 1. User Registration
**Endpoint:** `POST /api/auth/register`

**Body:**
```json
{
    "email": "kashem@gmail.com",
    "first_name": "kashem",
    "last_name": "hossain",
    "password": "1234",
    "username": "kashem123",
    "role": 2  // 1=Admin, 2=Manager, 3=Content Writer
}
```

**Success Response:** (201 Created)
```json
{
    "success": true,
    "statusCode": 201,
    "message": "User successfully registered!",
    "user": {
        "email": "kashem@gmail.com",
        "first_name": "kashem",
        "last_name": "hossain",
        "username": "kashem123",
        "role": 2
    }
}
```

### 2. User Login
**Endpoint:** `POST /api/auth/login`

**Body:**
```json
{
    "email": "abul@gmail.com",
    "password": "1234"
}
```

**Success Response:** (200 OK)
```json
{
    "success": true,
    "statusCode": 200,
    "message": "User logged in successfully",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "authenticatedUser": {
        "email": "abul@gmail.com",
        "role": "3"
    }
}
```

### 3. Obtain Token
**Endpoint:** `POST /api/auth/api/token/` or `POST /api/auth/token/obtain/`

**Body:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Success Response:** (200 OK)
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Refresh Token
**Endpoint:** `POST /api/auth/token/refresh/`

**Body:**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Success Response:** (200 OK)
```json
{
    "access": "new_access_token_here"
}
```

### 5. List Users
**Endpoint:** `GET /api/auth/users`

**Authorization:** Bearer Token required

**Success Response:** (200 OK)
```json
[
    {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "role": 2
    }
    // ... more users
]
```

## Content Management

### 1. Create Content
**Endpoint:** `POST /api/auth/content/`

**Authorization:** Bearer Token required

**Body:**
```json
{
    "title": "Content testing",
    "content": "Content body text"
}
```

**Success Response:** (201 Created)
```json
{
    "id": 4,
    "title": "Content testing",
    "content": "Content body text",
    "status": "ASSIGNED",
    "created_at": "2025-01-12T08:46:47.258314Z",
    "updated_at": "2025-01-12T08:46:47.258314Z",
    "created_by": 23,
    "last_modified_by": 23,
    "feedbacks": [],
    "is_editable": true
}
```

### 2. Update Content Status
**Endpoint:** `PATCH /api/auth/content/{id}/state/`

**Authorization:** Bearer Token required (Admin only)

**Body:**
```json
{
    "status": "PENDING_REVIEW"
}
```

**Success Response:** (200 OK)
```json
{
    "id": 4,
    "title": "Content testing",
    "content": "Content body text",
    "status": "PENDING_REVIEW",
    "created_at": "2025-01-12T08:46:47.258314Z",
    "updated_at": "2025-01-12T08:48:55.472511Z",
    "created_by": 23,
    "last_modified_by": 24,
    "feedbacks": [],
    "is_editable": true
}
```

### 3. Approve Content
**Endpoint:** `PATCH /api/auth/content/{id}/approve/`

**Authorization:** Bearer Token required (Admin only)

**Success Response:** (200 OK)
```json
{
    "id": 4,
    "title": "Content testing",
    "content": "Content body text",
    "status": "APPROVED",
    "is_editable": false
}
```

## Task Management

### 1. Create Task
**Endpoint:** `POST /api/auth/tasks/`

**Authorization:** Bearer Token required

**Body:**
```json
{
    "title": "Task Title",
    "description": "Task description",
    "assigned_to": 23,
    "due_date": "2025-01-20T00:00:00Z",
    "content_id": 4
}
```

**Success Response:** (201 Created)
```json
{
    "id": 3,
    "content": {
        // content object details
    },
    "assigned_to": 23,
    "assigned_to_name": "abul12",
    "assigned_by": 24,
    "assigned_by_name": "kashem123",
    "assigned_at": "2025-01-12T09:03:16.727499Z"
}
```

### 2. List Tasks
**Endpoint:** `GET /api/auth/tasks/`

**Authorization:** Bearer Token required

**Success Response:** (200 OK)
```json
[
    {
        "id": 1,
        "content": {
            // content object details
        },
        "assigned_to": 16,
        "assigned_to_name": "writer123",
        "assigned_by": 3,
        "assigned_by_name": "pri",
        "assigned_at": "2025-01-11T17:06:41.648237Z"
    }
]
```

### 3. Get Task Details
**Endpoint:** `GET /api/auth/tasks/{id}/`

**Authorization:** Bearer Token required

**Success Response:** (200 OK)
```json
{
    "id": 2,
    "content": {
        // content object details
    },
    "assigned_to": 21,
    "assigned_to_name": "adf1",
    "assigned_by": 22,
    "assigned_by_name": "mrt123",
    "assigned_at": "2025-01-12T08:25:24.797147Z"
}
```

## Authentication Headers
For all protected endpoints, include:
```
Authorization: Bearer <access_token>
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

# Database Structure

## Overview
This document describes the database schema, tables, and migrations used in the project.

### Migrations

#### Initial Migration
- **File**: `alembic/versions/initial_migration.py`
- **Description**: Sets up the base schema for the database, including tables for users, subscriptions, and webhooks.

### Schema

#### `users`
- **Description**: Stores user information.
- **Columns**:
  - `id` (Primary Key): Unique identifier for the user.
  - `name` (String): Name of the user.
  - `email` (String): Email address of the user.
  - `created_at` (Timestamp): Account creation date.

#### `subscriptions`
- **Description**: Tracks subscription details.
- **Columns**:
  - `id` (Primary Key): Unique identifier for the subscription.
  - `user_id` (Foreign Key): References the `users` table.
  - `plan` (String): Subscription plan (e.g., "basic", "premium").
  - `status` (String): Current status of the subscription (e.g., "active", "cancelled").
  - `created_at` (Timestamp): Subscription creation date.

#### `webhooks`
- **Description**: Logs webhook events.
- **Columns**:
  - `id` (Primary Key): Unique identifier for the webhook.
  - `subscription_id` (Foreign Key): References the `subscriptions` table.
  - `event_type` (String): Type of event (e.g., "payment_success", "subscription_cancelled").
  - `payload` (JSON): JSON payload of the webhook.
  - `created_at` (Timestamp): Timestamp of the webhook event.
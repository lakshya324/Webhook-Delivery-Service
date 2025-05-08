# Models

## Overview
This document provides details about the data models used in the project, including their fields and relationships.

### Key Models

#### `User`
- **Description**: Represents a user in the system.
- **Fields**:
  - `id` (Integer, Primary Key): Unique identifier for the user.
  - `name` (String): Name of the user.
  - `email` (String): Email address of the user.
  - `created_at` (DateTime): Timestamp of when the user was created.

#### `Subscription`
- **Description**: Represents a subscription associated with a user.
- **Fields**:
  - `id` (Integer, Primary Key): Unique identifier for the subscription.
  - `user_id` (Integer, Foreign Key): References the `User` model.
  - `plan` (String): Subscription plan (e.g., "basic", "premium").
  - `status` (String): Current status of the subscription (e.g., "active", "cancelled").
  - `created_at` (DateTime): Timestamp of when the subscription was created.

#### `WebhookEvent`
- **Description**: Represents a webhook event received by the system.
- **Fields**:
  - `id` (Integer, Primary Key): Unique identifier for the webhook event.
  - `subscription_id` (Integer, Foreign Key): References the `Subscription` model.
  - `event_type` (String): Type of event (e.g., "payment_success", "subscription_cancelled").
  - `payload` (JSON): JSON payload of the webhook.
  - `created_at` (DateTime): Timestamp of when the webhook event was received.
# API Endpoints

## Overview
This document provides details about the API endpoints available in the project.

### Endpoints

#### `/api/stats`
- **Method**: GET
- **Description**: Fetches statistical data for a subscription.
- **Response**:
  - `subscription_id`: The ID of the subscription.
  - `target_url`: The target URL of the subscription.
  - `total`: Total number of delivery attempts.
  - `success`: Number of successful deliveries.
  - `failure`: Number of failed deliveries.
  - `pending`: Number of pending deliveries.
  - `success_rate`: Percentage of successful deliveries.

#### `/api/subscriptions`
- **Method**: POST
- **Description**: Creates a new subscription.
- **Request Body**:
  - `target_url` (string): The URL to which webhooks will be delivered.
  - `secret_key` (string, optional): A secret key for signature verification.
  - `event_types` (array of strings, optional): List of event types to subscribe to.
- **Response**:
  - `id`: The ID of the created subscription.
  - `target_url`: The target URL of the subscription.
  - `created_at`: Timestamp of creation.

#### `/api/webhooks/ingest/{subscription_id}`
- **Method**: POST
- **Description**: Ingests a webhook payload for a specific subscription.
- **Headers**:
  - `X-Webhook-Event` (string, optional): The type of event.
  - `X-Hub-Signature-256` (string, optional): HMAC-SHA256 signature of the payload.
- **Request Body**:
  - JSON payload of the webhook.
- **Response**:
  - `status`: Status of the ingestion (e.g., "accepted").
  - `webhook_id`: The ID of the ingested webhook.

#### `/api/webhooks/{webhook_id}/status`
- **Method**: GET
- **Description**: Retrieves the delivery status of a specific webhook.
- **Response**:
  - List of delivery logs, each containing:
    - `attempt_number`: The attempt number.
    - `status`: The status of the delivery (e.g., "success", "failure").
    - `status_code`: HTTP status code returned by the target server.
    - `error_details`: Details of any errors encountered.

#### `/api/webhooks/subscription/{subscription_id}`
- **Method**: GET
- **Description**: Retrieves all webhooks for a specific subscription.
- **Query Parameters**:
  - `skip` (integer, optional): Number of records to skip.
  - `limit` (integer, optional): Maximum number of records to return.
- **Response**:
  - List of webhooks, each containing:
    - `id`: The ID of the webhook.
    - `event_type`: The type of event.
    - `payload`: The JSON payload of the webhook.
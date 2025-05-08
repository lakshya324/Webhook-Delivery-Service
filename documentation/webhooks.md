# Webhooks

## Overview
This document provides details about the webhook functionality in the project, including how webhooks are ingested, processed, and delivered.

### Workflow

1. **Webhook Ingestion**:
   - Endpoint: `/api/webhooks/ingest/{subscription_id}`
   - The system receives a webhook payload via a POST request.
   - Headers:
     - `X-Webhook-Event`: Specifies the type of event.
     - `X-Hub-Signature-256`: HMAC-SHA256 signature for payload verification.
   - The payload is validated and stored in the database.

2. **Webhook Processing**:
   - A background worker fetches pending webhooks from the database.
   - The worker attempts to deliver the webhook to the target URL specified in the subscription.

3. **Delivery Status Tracking**:
   - Delivery attempts are logged, including the HTTP status code and any errors encountered.
   - The status can be queried via the `/api/webhooks/{webhook_id}/status` endpoint.

### Key Components

#### Database
- **Table**: `webhooks`
  - Stores webhook events and their metadata.
- **Table**: `delivery_logs`
  - Tracks delivery attempts for each webhook.

#### Worker
- **File**: `app/worker.py`
  - Implements the logic for processing and delivering webhooks.

#### API Endpoints
- **Ingest Webhook**: `/api/webhooks/ingest/{subscription_id}`
- **Get Delivery Status**: `/api/webhooks/{webhook_id}/status`
- **List Webhooks for Subscription**: `/api/webhooks/subscription/{subscription_id}`

### Security

- **Payload Verification**:
  - The `X-Hub-Signature-256` header is used to verify the integrity and authenticity of the payload.
  - The signature is computed using the subscription's secret key.

- **Rate Limiting**:
  - To prevent abuse, the system enforces rate limits on webhook ingestion endpoints.

### Error Handling

- **Retries**:
  - Failed delivery attempts are retried with exponential backoff.

- **Dead Letter Queue**:
  - Webhooks that fail after multiple retries are moved to a dead letter queue for manual inspection.
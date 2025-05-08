import sys
import os
import unittest
from fastapi.testclient import TestClient
import uuid
from datetime import datetime, timedelta

# Explicitly set PYTHONPATH to the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.main import app
from app.models import DeliveryStatus
from app.core.database import SessionLocal, engine, Base

class TestWebhookAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()
        
        # Create test data
        self.test_subscription = {
            "target_url": "https://example.com/webhook",
            "secret_key": "test-secret",
            "event_types": ["order.created", "user.updated"]
        }
        
        self.test_webhook_payload = {
            "message": "Test webhook payload",
            "timestamp": datetime.utcnow().isoformat()
        }

    def tearDown(self):
        self.db.close()

    def test_create_subscription(self):
        response = self.client.post(
            "/api/v1/subscriptions/",
            json=self.test_subscription
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["target_url"], self.test_subscription["target_url"])
        self.assertEqual(data["secret_key"], self.test_subscription["secret_key"])
        self.assertEqual(data["event_types"], self.test_subscription["event_types"])
        
        # Use the created subscription ID for further tests
        return data["id"]

    def test_get_subscription(self):
        # First create a subscription
        subscription_id = self.test_create_subscription()
        
        # Now get it
        response = self.client.get(f"/api/v1/subscriptions/{subscription_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], subscription_id)
        self.assertEqual(data["target_url"], self.test_subscription["target_url"])
        
    def test_update_subscription(self):
        # First create a subscription
        subscription_id = self.test_create_subscription()
        
        # Now update it
        update_data = {
            "target_url": "https://updated-example.com/webhook"
        }
        response = self.client.put(
            f"/api/v1/subscriptions/{subscription_id}",
            json=update_data
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["target_url"], update_data["target_url"])
        
    def test_delete_subscription(self):
        # First create a subscription
        subscription_id = self.test_create_subscription()
        
        # Now delete it
        response = self.client.delete(f"/api/v1/subscriptions/{subscription_id}")
        self.assertEqual(response.status_code, 204)
        
        # Verify it's deleted
        response = self.client.get(f"/api/v1/subscriptions/{subscription_id}")
        self.assertEqual(response.status_code, 404)
    
    def test_ingest_webhook(self):
        # First create a subscription
        subscription_id = self.test_create_subscription()
        
        # Now ingest a webhook
        response = self.client.post(
            f"/api/v1/webhooks/ingest/{subscription_id}",
            json=self.test_webhook_payload,
            headers={"X-Webhook-Event": "order.created"}
        )
        self.assertEqual(response.status_code, 202)
        data = response.json()
        self.assertIn("webhook_id", data)
        self.assertEqual(data["status"], "accepted")
        
        # Use the created webhook ID for further tests
        return data["webhook_id"]
    
    def test_get_webhook_status(self):
        # First create a subscription and ingest a webhook
        webhook_id = self.test_ingest_webhook()
        
        # Now get webhook status
        response = self.client.get(f"/api/v1/webhooks/{webhook_id}/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        if data:  # If worker has already processed it
            self.assertEqual(data[0]["webhook_id"], webhook_id)
    
    def test_get_subscription_webhooks(self):
        # First create a subscription and ingest a webhook
        subscription_id = self.test_create_subscription()
        webhook_id = self.test_ingest_webhook()  # This uses the same subscription
        
        # Now get webhooks for subscription
        response = self.client.get(f"/api/v1/webhooks/subscription/{subscription_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(isinstance(data, list))
        if data:  # The webhook should be in the list
            self.assertEqual(data[0]["id"], webhook_id)
            self.assertEqual(data[0]["subscription_id"], subscription_id)
            
    def test_get_subscription_stats(self):
        # First create a subscription and ingest a webhook
        subscription_id = self.test_create_subscription()
        webhook_id = self.test_ingest_webhook()  # This uses the same subscription
        
        # Now get subscription stats
        response = self.client.get(f"/api/v1/stats/subscription/{subscription_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["subscription_id"], subscription_id)
        self.assertTrue("total" in data)
        self.assertTrue("success" in data)
        self.assertTrue("failure" in data)
        self.assertTrue("pending" in data)

if __name__ == "__main__":
    unittest.main()
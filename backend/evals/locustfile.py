from locust import HttpUser, task, between

class WebhookUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def send_webhook(self):
        self.client.post(
            "/webhook/bolna",
            headers={
                "Authorization": "Bearer 32942641de1e511bed16087c775726ab729711229a754112b4da981e82d68f86",
                "X-API-Key": "251c3e1189ffa8ffae57b7cf403a1f2bb85ff62247960fc673b4e0eeab4ef536",
                "X-Tenant-ID": "tenant_a",
                "Content-Type": "application/json",
            },
            json={
                "execution_id": "load_test_001",
                "agent_id": "agent_001",
                "status": "completed",
                "duration": 30.0,
            }
        )
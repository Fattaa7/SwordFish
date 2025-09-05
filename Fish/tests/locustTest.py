from locust import HttpUser, task, between

class QueryUser(HttpUser):
    wait_time = between(1, 3)  # Simulate user think time

    @task
    def send_query(self):
        payload = {
            "text": "What is the capital of Egypt?"
        }
        self.client.post("/workspaces/3/conversations/1/queries", json=payload)

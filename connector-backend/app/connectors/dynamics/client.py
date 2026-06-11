import requests

from app.config import (
    DYNAMICS_BASE_URL,
    DYNAMICS_TOKEN
)

class DynamicsClient:

    def __init__(self):

        self.headers = {
            "Authorization": f"Bearer {DYNAMICS_TOKEN}",
            "Content-Type": "application/json"
        }

    def get_customers(self):

        url = f"{DYNAMICS_BASE_URL}/customers"

        response = requests.get(
            url,
            headers=self.headers
        )

        response.raise_for_status()

        return {
            "status_code": response.status_code,
            "response": response.text
        }
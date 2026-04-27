import requests

class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def getUsers(self, ):
        url = f"{self.base_url}/users"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def createUser(self, body=None):
        url = f"{self.base_url}/users"
        response = requests.post(url, json=body)
        response.raise_for_status()
        return response.json()

    def getUserById(self, userId=None):
        url = f"{self.base_url}/users/{userId}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def deleteUser(self, userId=None):
        url = f"{self.base_url}/users/{userId}"
        response = requests.delete(url)
        response.raise_for_status()
        return response.json()


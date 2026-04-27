import requests

class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url

    def listPets(self, limit=None):
        url = f"{self.base_url}/pets"
        params = {'limit': limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def createPets(self, body=None):
        url = f"{self.base_url}/pets"
        response = requests.post(url, json=body)
        response.raise_for_status()
        return response.json()

    def showPetById(self, petId=None):
        url = f"{self.base_url}/pets/{petId}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


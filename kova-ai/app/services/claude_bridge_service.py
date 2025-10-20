import requests

class ClaudeBridgeService:
    def __init__(self, api_key, repo_url):
        self.api_key = api_key
        self.repo_url = repo_url
        self.base_url = 'https://api.claude.ai/v1/'

    def connect_to_claude(self):
        headers = {'Authorization': f'Bearer {self.api_key}'}
        response = requests.get(self.base_url + 'connect', headers=headers)
        return response.json()

    def fetch_kova_ai_data(self):
        response = requests.get(self.repo_url)
        return response.json()

    def sync_with_claude(self):
        kova_data = self.fetch_kova_ai_data()
        headers = {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}
        response = requests.post(self.base_url + 'sync', json=kova_data, headers=headers)
        return response.json()

    def run(self):
        self.connect_to_claude()
        self.sync_with_claude()
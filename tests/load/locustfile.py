from locust import HttpUser, task, between
import random
import string

class LinkShortenerUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        self.email = f"load_test_{random.randint(100000, 999999)}@test.com"
        self.password = "testpass123"
        self.token = None
        self.my_links = []
        
        self.register_user()
        self.login_user()
    
    def register_user(self):
        response = self.client.post(
            "/auth/register",
            json={
                "email": self.email,
                "password": self.password
            }
        )
        if response.status_code == 201:
            print(f"User {self.email} registered")
    
    def login_user(self):
        response = self.client.post(
            "/auth/jwt/login",
            data={
                "username": self.email,
                "password": self.password
            }
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print(f"User {self.email} logged in")
    
    def get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(3)
    def create_short_link(self):
        random_url = f"https://example.com/{''.join(random.choices(string.ascii_lowercase, k=10))}"
        
        with self.client.post(
            "/links/shorten",
            json={"original_url": random_url},
            headers=self.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.my_links.append(data["short_code"])
                response.success()
            else:
                response.failure(f"Failed to create link: {response.status_code}")
    
    @task(2)
    def redirect_to_link(self):
        if not self.my_links:
            return
        
        short_code = random.choice(self.my_links)
        with self.client.get(
            f"/links/{short_code}",
            allow_redirects=False,
            catch_response=True
        ) as response:
            if response.status_code == 307:
                response.success()
            else:
                response.failure(f"Expected 307, got {response.status_code}")

    @task(2)
    def delete_link(self):
        if not self.my_links:
            return
        
        short_code = random.choice(self.my_links)
        with self.client.delete(
            f"/links/{short_code}",
            headers=self.get_headers(),
            catch_response=True
        ) as del_response:
            if del_response.status_code == 204:
                del_response.success()
                self.my_links.remove(short_code)
            else:
                del_response.failure(f"Expected 204, got {del_response.status_code}")
                return
        
        with self.client.get(
            "/links/my",
            headers=self.get_headers(),
            catch_response=True
        ) as get_response:
            if get_response.status_code == 200:
                links = get_response.json()
                if not any(link["short_code"] == short_code for link in links):
                    get_response.success()
                else:
                    get_response.failure(f"Link with code {short_code} is not deleted")
            else:
                get_response.failure(f"Failed to get my links: {get_response.status_code}")
    
    @task(1)
    def get_link_stats(self):
        if not self.my_links:
            return
        
        short_code = random.choice(self.my_links)
        with self.client.get(
            f"/links/{short_code}/stats",
            headers=self.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get stats: {response.status_code}")
    
    @task(1)
    def search_links(self):
        with self.client.get(
            "/links/search",
            params={"original_url": "example.com"},
            headers=self.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed: {response.status_code}")
    
    @task(1)
    def get_my_links(self):
        with self.client.get(
            "/links/my",
            headers=self.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get my links: {response.status_code}")
    
    @task(1)
    def update_link(self):
        if not self.my_links:
            return
        
        short_code = random.choice(self.my_links)
        with self.client.put(
            f"/links/{short_code}",
            json={"original_url": "https://updated-example.com"},
            headers=self.get_headers(),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to update link: {response.status_code}")
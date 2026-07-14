# api.py - Comprehensive API Integration Toolkit
import asyncio
import hashlib
import hmac
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Any, Dict, List, Optional

import aiohttp
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response container"""

    success: bool
    data: Any
    status_code: int
    headers: Dict
    error: Optional[str] = None
    latency: Optional[float] = None


class APIClient(ABC):
    """Abstract base class for API clients"""

    @abstractmethod
    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        pass

    @abstractmethod
    def authenticate(self, **kwargs):
        pass


class RESTAPIClient(APIClient):
    """
    Generic REST API Client with authentication and rate limiting
    """

    def __init__(
        self, base_url: str, default_headers: Dict = None, rate_limit: int = 100
    ):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.default_headers = default_headers or {}
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.auth_token = None

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "APIClient/1.0"}
        )
        self.session.headers.update(self.default_headers)

    def _handle_rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_between_requests = 1.0 / self.rate_limit
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < time_between_requests:
            sleep_time = time_between_requests - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def authenticate(self, auth_type: str, **credentials):
        """Handle different authentication methods"""
        if auth_type == "bearer":
            self.auth_token = credentials.get("token")
            self.session.headers["Authorization"] = f"Bearer {self.auth_token}"

        elif auth_type == "basic":
            username = credentials.get("username")
            password = credentials.get("password")
            self.session.auth = (username, password)

        elif auth_type == "api_key":
            key_name = credentials.get("key_name", "X-API-Key")
            key_value = credentials.get("key_value")
            self.session.headers[key_name] = key_value

        elif auth_type == "hmac":
            # Store HMAC credentials for signing requests
            self.hmac_key = credentials.get("hmac_key")
            self.hmac_secret = credentials.get("hmac_secret")

    def _sign_hmac_request(self, method: str, endpoint: str, data: str = ""):
        """Sign request using HMAC authentication"""
        if hasattr(self, "hmac_key") and hasattr(self, "hmac_secret"):
            timestamp = str(int(time.time()))
            message = f"{method}{endpoint}{data}{timestamp}"
            signature = hmac.new(
                self.hmac_secret.encode(), message.encode(), hashlib.sha256
            ).hexdigest()

            self.session.headers.update(
                {
                    "X-Auth-Key": self.hmac_key,
                    "X-Auth-Timestamp": timestamp,
                    "X-Auth-Signature": signature,
                }
            )

    def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make API request with error handling and rate limiting"""
        self._handle_rate_limit()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()

        try:
            # Handle HMAC authentication
            if hasattr(self, "hmac_key"):
                data_str = (
                    json.dumps(kwargs.get("json", {})) if kwargs.get("json") else ""
                )
                self._sign_hmac_request(method, endpoint, data_str)

            response = self.session.request(method, url, **kwargs)
            latency = time.time() - start_time

            # Parse response
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text

            return APIResponse(
                success=200 <= response.status_code < 300,
                data=response_data,
                status_code=response.status_code,
                headers=dict(response.headers),
                latency=latency,
            )

        except requests.exceptions.RequestException as e:
            return APIResponse(
                success=False,
                data=None,
                status_code=0,
                headers={},
                error=str(e),
                latency=time.time() - start_time,
            )

    # Convenience methods
    def get(self, endpoint: str, **kwargs) -> APIResponse:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> APIResponse:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> APIResponse:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> APIResponse:
        return self.request("DELETE", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> APIResponse:
        return self.request("PATCH", endpoint, **kwargs)


class AsyncAPIClient:
    """Asynchronous API client"""

    def __init__(self, base_url: str, default_headers: Dict = None):
        self.base_url = base_url
        self.default_headers = default_headers or {}

    async def request(self, method: str, endpoint: str, **kwargs) -> APIResponse:
        """Make async API request"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()

        try:
            async with aiohttp.ClientSession(headers=self.default_headers) as session:
                async with session.request(method, url, **kwargs) as response:
                    latency = time.time() - start_time

                    try:
                        data = await response.json()
                    except:
                        data = await response.text()

                    return APIResponse(
                        success=200 <= response.status < 300,
                        data=data,
                        status_code=response.status,
                        headers=dict(response.headers),
                        latency=latency,
                    )
        except Exception as e:
            return APIResponse(
                success=False,
                data=None,
                status_code=0,
                headers={},
                error=str(e),
                latency=time.time() - start_time,
            )


# ===== SPECIFIC API IMPLEMENTATIONS =====


class OpenAIClient(RESTAPIClient):
    """OpenAI API client"""

    def __init__(self, api_key: str):
        super().__init__("https://api.openai.com/v1")
        self.authenticate("bearer", token=api_key)

    def chat_completion(
        self, messages: List[Dict], model: str = "gpt-3.5-turbo", **kwargs
    ) -> APIResponse:
        payload = {"model": model, "messages": messages, **kwargs}
        return self.post("/chat/completions", json=payload)

    def generate_image(
        self, prompt: str, size: str = "1024x1024", n: int = 1
    ) -> APIResponse:
        payload = {"prompt": prompt, "n": n, "size": size}
        return self.post("/images/generations", json=payload)


class GitHubClient(RESTAPIClient):
    """GitHub API client"""

    def __init__(self, token: str = None):
        super().__init__("https://api.github.com")
        if token:
            self.authenticate("bearer", token=token)

    def get_user_repos(self, username: str) -> APIResponse:
        return self.get(f"/users/{username}/repos")

    def create_repo(
        self, name: str, private: bool = False, description: str = ""
    ) -> APIResponse:
        payload = {
            "name": name,
            "private": private,
            "description": description,
            "auto_init": True,
        }
        return self.post("/user/repos", json=payload)

    def search_repositories(
        self, query: str, sort: str = "stars", order: str = "desc"
    ) -> APIResponse:
        return self.get(
            "/search/repositories", params={"q": query, "sort": sort, "order": order}
        )


class TwitterClient(RESTAPIClient):
    """Twitter API v2 client"""

    def __init__(self, bearer_token: str):
        super().__init__("https://api.twitter.com/2")
        self.authenticate("bearer", token=bearer_token)

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> APIResponse:
        return self.get(f"/users/{user_id}/tweets", params={"max_results": max_results})

    def search_tweets(self, query: str, max_results: int = 10) -> APIResponse:
        return self.get(
            "/tweets/search/recent", params={"query": query, "max_results": max_results}
        )


class WeatherAPIClient(RESTAPIClient):
    """OpenWeatherMap API client"""

    def __init__(self, api_key: str):
        super().__init__("https://api.openweathermap.org/data/2.5")
        self.api_key = api_key

    def get_current_weather(
        self, city: str, country_code: str = None, units: str = "metric"
    ) -> APIResponse:
        query = f"{city},{country_code}" if country_code else city
        params = {"q": query, "appid": self.api_key, "units": units}
        return self.get("/weather", params=params)

    def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> APIResponse:
        params = {"q": city, "appid": self.api_key, "units": units, "cnt": days}
        return self.get("/forecast", params=params)


class StripeClient(RESTAPIClient):
    """Stripe API client"""

    def __init__(self, api_key: str):
        super().__init__("https://api.stripe.com/v1")
        self.authenticate("basic", username=api_key, password="")

    def create_customer(self, email: str, name: str = None) -> APIResponse:
        data = {"email": email}
        if name:
            data["name"] = name
        return self.post("/customers", data=data)

    def create_payment_intent(
        self, amount: int, currency: str = "usd", customer: str = None
    ) -> APIResponse:
        data = {
            "amount": amount,
            "currency": currency,
        }
        if customer:
            data["customer"] = customer
        return self.post("/payment_intents", data=data)


# ===== API UTILITIES =====


class APIManager:
    """Manage multiple API clients"""

    def __init__(self):
        self.clients = {}

    def register_client(self, name: str, client: APIClient):
        self.clients[name] = client

    def get_client(self, name: str) -> APIClient:
        return self.clients.get(name)

    def make_concurrent_requests(
        self, requests_config: List[Dict]
    ) -> List[APIResponse]:
        """Make multiple API requests concurrently"""

        async def make_requests():
            tasks = []
            for config in requests_config:
                client_name = config["client"]
                method = config["method"]
                endpoint = config["endpoint"]
                client = self.clients[client_name]

                if isinstance(client, AsyncAPIClient):
                    task = client.request(method, endpoint, **config.get("kwargs", {}))
                else:
                    # Convert sync client to async
                    task = asyncio.to_thread(
                        client.request, method, endpoint, **config.get("kwargs", {})
                    )

                tasks.append(task)

            return await asyncio.gather(*tasks, return_exceptions=True)

        results = asyncio.run(make_requests())
        return [result for result in results if isinstance(result, APIResponse)]


def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator for API calls"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e

                    logger.warning(
                        f"Attempt {retries} failed: {e}. Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper

    return decorator


def cache_response(ttl: int = 300):
    """Cache API responses decorator"""
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            if key in cache:
                timestamp, data = cache[key]
                if time.time() - timestamp < ttl:
                    return data

            # Call function and cache result
            result = func(*args, **kwargs)
            cache[key] = (time.time(), result)
            return result

        return wrapper

    return decorator


# ===== USAGE EXAMPLES =====


def main():
    """Demonstrate API client usage"""

    # Initialize API manager
    manager = APIManager()

    # Register various API clients (using placeholder keys)
    # manager.register_client('openai', OpenAIClient(api_key="your_openai_key"))
    # manager.register_client('github', GitHubClient(token="your_github_token"))
    # manager.register_client('weather', WeatherAPIClient(api_key="your_weather_key"))

    # Example with generic REST client
    json_placeholder = RESTAPIClient("https://jsonplaceholder.typicode.com")
    manager.register_client("json_placeholder", json_placeholder)

    # Make some requests
    print("=== Testing JSONPlaceholder API ===")

    # Get posts
    response = json_placeholder.get("/posts")
    if response.success:
        print(f"Retrieved {len(response.data)} posts")
        print(f"First post title: {response.data[0]['title']}")
    else:
        print(f"Error: {response.error}")

    # Create a new post
    new_post = {"title": "Test Post", "body": "This is a test post", "userId": 1}
    response = json_placeholder.post("/posts", json=new_post)
    if response.success:
        print(f"Created post with ID: {response.data['id']}")

    # Concurrent requests example
    print("\n=== Testing Concurrent Requests ===")
    requests_config = [
        {"client": "json_placeholder", "method": "GET", "endpoint": "/posts/1"},
        {"client": "json_placeholder", "method": "GET", "endpoint": "/posts/2"},
        {"client": "json_placeholder", "method": "GET", "endpoint": "/posts/3"},
    ]

    # Note: This would work better with async clients
    # results = manager.make_concurrent_requests(requests_config)
    # for i, result in enumerate(results):
    #     if result.success:
    #         print(f"Request {i+1}: Success - {result.data['title']}")


@retry(max_retries=3, delay=1)
@cache_response(ttl=60)
def cached_retry_api_call(client: RESTAPIClient, endpoint: str):
    """Example of using retry and cache decorators"""
    return client.get(endpoint)


# Quick utility functions
def make_api_call(
    url: str, method: str = "GET", headers: Dict = None, data: Dict = None
) -> Dict:
    """Quick one-off API call utility"""
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None


def download_file(url: str, save_path: str, chunk_size: int = 8192) -> bool:
    """Download file from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


if __name__ == "__main__":
    main()

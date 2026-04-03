from api import APIManager, RESTAPIClient

# Quick API call
response = make_api_call("https://api.github.com/users/octocat")
print(response)

# Using specific API clients
# github = GitHubClient("your_token")
# repos = github.get_user_repos("octocat")

# Using generic REST client
api = RESTAPIClient("https://jsonplaceholder.typicode.com")
posts = api.get("/posts")
if posts.success:
    for post in posts.data[:5]:
        print(post["title"])

# API Manager for multiple services
manager = APIManager()
# manager.register_client('github', github)
# manager.register_client('openai', OpenAIClient("your_key"))

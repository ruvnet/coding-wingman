#              - Coding Wingman
#     /\__/\   - main.py 
#    ( o.o  )  - v0.0.1
#      >^<     - by @rUv

# Import the necessary modules and libraries
from fastapi import FastAPI, HTTPException   # FastAPI framework and Request object
from pydantic import BaseModel
import httpx                                 # Library for making asynchronous HTTP requests
import os                                    # Provides access to operating system-dependent functionality

# Initialize FastAPI app
app = FastAPI()

# Retrieve the GitHub API token from environment variables
GITHUB_API_TOKEN = os.getenv("GITHUB_TOKEN")
# Determine if Bearer token should be used based on environment variable
USE_BEARER_TOKEN = os.getenv("USE_BEARER_TOKEN", "False").lower() == "true"

# Conditionally setting the Authorization header
if GITHUB_API_TOKEN:
    if USE_BEARER_TOKEN:
        # Use Bearer token for Authorization
        headers = {
            "Authorization": f"Bearer {GITHUB_API_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
    else:
        # Use regular token for Authorization
        headers = {
            "Authorization": f"token {GITHUB_API_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
else:
    # Raise an error if no GitHub API token is provided
    raise EnvironmentError("No GitHub API token provided in environment variables.")

# GitHub Search API URL
GITHUB_SEARCH_API_URL = "https://api.github.com/search"

# Pydantic model for search requests
class SearchRequest(BaseModel):
    query: str

# Function to perform a search on GitHub
async def perform_search(search_type: str, query: str):
    """
    Perform a search on GitHub.

    Args:
    search_type (str): The type of search (code, commits, issues, etc.).
    query (str): The search query string.

    Returns:
    dict: JSON response from GitHub API.
    """
    url = f"{GITHUB_SEARCH_API_URL}/{search_type}?q={query}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()

# Endpoint to search code on GitHub
@app.post("/search/code/")
async def search_code(request: SearchRequest = SearchRequest(query="FastAPI filename:main.py")):
    """
    Search code on GitHub.
    Default query: {"query": "FastAPI filename:main.py"}
    """
    return await perform_search("code", request.query)

# Endpoint to search commits on GitHub
@app.post("/search/commits/")
async def search_commits(request: SearchRequest = SearchRequest(query="fix bug repo:openai/gpt-3")):
    """
    Search commits on GitHub.
    Default query: {"query": "fix bug repo:openai/gpt-3"}
    """
    return await perform_search("commits", request.query)

# Endpoint to search issues on GitHub
@app.post("/search/issues/")
async def search_issues(request: SearchRequest = SearchRequest(query="bug label:bug")):
    """
    Search issues on GitHub.
    Default query: {"query": "bug label:bug"}
    """
    return await perform_search("issues", request.query)

# Endpoint to search labels on GitHub
@app.post("/search/labels/")
async def search_labels(request: SearchRequest = SearchRequest(query="bug repo:openai/gpt-3")):
    """
    Search labels on GitHub.
    Default query: {"query": "bug repo:openai/gpt-3"}
    """
    return await perform_search("labels", request.query)

# Endpoint to search repositories on GitHub
@app.post("/search/repositories/")
async def search_repositories(request: SearchRequest = SearchRequest(query="FastAPI stars:>1000")):
    """
    Search repositories on GitHub.
    Default query: {"query": "FastAPI stars:>1000"}
    """
    return await perform_search("repositories", request.query)

# Endpoint to search topics on GitHub
@app.post("/search/topics/")
async def search_topics(request: SearchRequest = SearchRequest(query="machine-learning")):
    """
    Search topics on GitHub.
    Default query: {"query": "machine-learning"}
    """
    return await perform_search("topics", request.query)

# Endpoint to search users on GitHub
@app.post("/search/users/")
async def search_users(request: SearchRequest = SearchRequest(query="ruvnet")):
    """
    Search users on GitHub.
    Default query: {"query": "ruvnet"}
    """
    return await perform_search("users", request.query)

# Main function to run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

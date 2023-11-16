#              - Coding Wingman
#     /\__/\   - main.py 
#    ( o.o  )  - v0.0.1
#      >^<     - by @rUv

from fastapi.security import HTTPBearer, OAuth2AuthorizationCodeBearer
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import RedirectResponse
import httpx
import os
import json
from fastapi.responses import StreamingResponse

# Initialize a new FastAPI application,
# and use the FASTAPI_SERVER_URL environment variable to specify the server url.
# If FASTAPI_SERVER_URL is not set, the servers list will be empty,
# and FastAPI will default to serving the API on http://localhost:8000.
app = FastAPI(servers=[{"url": os.getenv("FASTAPI_SERVER_URL")}] if os.getenv("FASTAPI_SERVER_URL") else [])

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Redirects to the automatically generated FastAPI documentation page
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url='/docs')
  
# Retrieve tokens from environment variables
GITHUB_API_TOKEN = os.getenv("GITHUB_TOKEN")
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")

# Security scheme for bearer with JWT
security = HTTPBearer()

# Uncomment the lines below and comment out the line above if you want to use OAuth2 with Authorization Code flow
# You will also need to set up redirection endpoint and provide your client id, client secret, 
# authorization URL, and token URL for your OAuth flow with GitHub.

# OAUTH2_SCHEME_NAME = 'OAUTH2_SCHEME_NAME'

# oauth2_scheme = OAuth2AuthorizationCodeBearer(
#     authorizationUrl="https://github.com/login/oauth/authorize",
#     tokenUrl="https://github.com/login/oauth/access_token",
#     refreshUrl=None,
#     scheme_name=OAUTH2_SCHEME_NAME,
# )

# To enable OAuth2, use OAUTH2_SCHEME_NAME instead of security when creating dependency in endpoint functions.
# For example:
# def verify_token(token: str = Depends(oauth2_scheme)):
#     # Your code to verify the token (e.g., call to your auth server)

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the authorization token sent with the request.
    """
    if authorization.credentials != API_BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing Bearer token")

if not GITHUB_API_TOKEN:
    raise EnvironmentError("No GitHub API token provided in environment variables.")
    
# Headers for GitHub API requests
headers = {
    "Authorization": f"token {GITHUB_API_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

GITHUB_SEARCH_API_URL = "https://api.github.com/search"
async def perform_search(search_type: str, query: str, page: int = 1, per_page: int = 10):
    # Construct the search URL with query parameters for search type, query, pagination page, and results per page
    url = f"{GITHUB_SEARCH_API_URL}/{search_type}?q={query}&page={page}&per_page={per_page}"
    
    # Perform an asynchronous HTTP GET request using the constructed URL and custom headers
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    
    # If the response status code is not 200 (OK), raise an HTTPException with the response details
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    # Return the JSON response content if the request was successful
    return response.json()

class SearchRequest(BaseModel):
    # Textual search query or keywords
    query: str
    # Starting page number for search results pagination
    page: int = 1
    # Number of search results per page
    per_page: int = 2

# Endpoint to search for code snippets on GitHub using a user-specified search query.
# It requires the 'SearchRequest' object for query parameters and a valid bearer token for authorization.
@app.post("/search/code/")
async def search_code(request: SearchRequest, token: HTTPAuthorizationCredentials = Depends(verify_token)):
    return await perform_search("code", request.query, request.page, request.per_page)
  
# Endpoint to search for commits on GitHub using a user-specified search query or the default query "fix bug repo:openai/gpt-3".
# It requires the 'SearchRequest' object for query parameters and a valid bearer token for authorization. 
@app.post("/search/commits/")
async def search_commits(request: SearchRequest = SearchRequest(query="fix bug repo:openai/gpt-3"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    return await perform_search("commits", request.query)

def generate_paginated_response(results, char_limit: int = 500):
    """
    Paginate results beyond a certain character count.
    """
    # Convert the results to string, then to a list of characters for pagination
    results_str = json.dumps(results)
    paginated_result = [results_str[i:i+char_limit] for i in range(0, len(results_str), char_limit)]

    # Generator function to yield paginated results
    def paginated_json_generator():
        for page in paginated_result:
            yield page

    return StreamingResponse(paginated_json_generator(), media_type="application/json")

@app.post("/search/issues/")
async def search_issues(request: SearchRequest = SearchRequest(query="bug label:bug"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search issues on GitHub with automatic pagination beyond a certain character count.
    Default query: "bug label:bug"
    """
    results = await perform_search("issues", request.query, request.page, request.per_page)
    return generate_paginated_response(results)
@app.post("/search/labels/")
async def search_labels(request: SearchRequest = SearchRequest(query="bug repo:openai/gpt-3"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search labels on GitHub.
    Default query: "bug repo:openai/gpt-3"
    """
    return await perform_search("labels", request.query)

@app.post("/search/repositories/")
async def search_repositories(request: SearchRequest = SearchRequest(query="FastAPI stars:>1000"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search repositories on GitHub.
    Default query: "FastAPI stars:>1000"
    """
    return await perform_search("repositories", request.query)

@app.post("/search/topics/")
async def search_topics(request: SearchRequest = SearchRequest(query="machine-learning"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search topics on GitHub.
    Default query: "machine-learning"
    """
    return await perform_search("topics", request.query)

@app.post("/search/users/")
async def search_users(request: SearchRequest = SearchRequest(query="ruvnet"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search users on GitHub.
    Default query: "ruvnet"
    """
    return await perform_search("users", request.query)

# If this script is run as the main script, it starts the uvicorn server with the specified host and port.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

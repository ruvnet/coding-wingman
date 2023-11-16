#              - Coding Wingman
#     /\__/\   - main.py 
#    ( o.o  )  - v0.0.1
#      >^<     - by @rUv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import RedirectResponse
import httpx
import os

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "OK"}
  
@app.get("/")
async def redirect_to_docs():
    """
    Redirect the root path to the /docs path for the API documentation.
    """
    return RedirectResponse(url='/docs')
  
# Retrieve tokens from environment variables
GITHUB_API_TOKEN = os.getenv("GITHUB_TOKEN")
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")

security = HTTPBearer()

def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    if authorization.credentials != API_BEARER_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing Bearer token")

if not GITHUB_API_TOKEN:
    raise EnvironmentError("No GitHub API token provided in environment variables.")
headers = {
    "Authorization": f"token {GITHUB_API_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

GITHUB_SEARCH_API_URL = "https://api.github.com/search"

class SearchRequest(BaseModel):
    query: str

async def perform_search(search_type: str, query: str):
    url = f"{GITHUB_SEARCH_API_URL}/{search_type}?q={query}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

# Define endpoints for searching GitHub
@app.post("/search/code/")
async def search_code(request: SearchRequest = SearchRequest(query="FastAPI filename:main.py"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search code on GitHub.
    Default query: "FastAPI filename:main.py"
    """
    return await perform_search("code", request.query)

@app.post("/search/commits/")
async def search_commits(request: SearchRequest = SearchRequest(query="fix bug repo:openai/gpt-3"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search commits on GitHub.
    Default query: "fix bug repo:openai/gpt-3"
    """
    return await perform_search("commits", request.query)

@app.post("/search/issues/")
async def search_issues(request: SearchRequest = SearchRequest(query="bug label:bug"), token: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Search issues on GitHub.
    Default query: "bug label:bug"
    """
    return await perform_search("issues", request.query)

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

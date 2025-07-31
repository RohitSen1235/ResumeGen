import os
import asyncio
import json
import httpx
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from both backend/.env and root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../.env'))

# LinkedIn OAuth Configuration
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')

# Set redirect URI based on production mode
prod_mode = os.getenv('PROD_MODE', 'False').lower() == 'true'
prod_host = os.getenv('PROD_HOST', 'localhost')

if prod_mode and prod_host != 'localhost':
    REDIRECT_URI = f"https://{prod_host}/auth/linkedin/callback"
else:
    REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost/auth/linkedin/callback')

# LinkedIn API Endpoints
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
PROFILE_URL = "https://api.linkedin.com/v2/userinfo"

async def get_authorization_url(state: str) -> str:
    """Generate LinkedIn OAuth authorization URL"""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": "openid profile email"
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{AUTH_URL}?{query_string}"

async def exchange_code_for_token(code: str) -> Dict:
    """Exchange authorization code for access token"""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        return response.json()

async def get_user_profile(access_token: str) -> Dict:
    """Get basic user profile information from LinkedIn"""
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(PROFILE_URL, headers=headers)
        response.raise_for_status()
        return response.json()

async def test_linkedin_auth():
    try:
        # Get authorization URL
        auth_url = await get_authorization_url(state="test_state")
        print(f"Authorization URL: {auth_url}")
        
        # User needs to visit this URL and paste the code here
        code = input("Enter the authorization code from the redirect URL: ")
        
        # Exchange code for token
        token_data = await exchange_code_for_token(code)
        print("\nToken Data:")
        print(json.dumps(token_data, indent=2))
        
        # Get user profile
        profile = await get_user_profile(token_data['access_token'])
        print("\nProfile Data:")
        print(json.dumps(profile, indent=2))
        
        # Save raw response to file
        with open('linkedin_response.json', 'w') as f:
            json.dump(profile, f, indent=2)
            
        print("\nRaw response saved to linkedin_response.json")
        
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: LinkedIn OAuth credentials not configured")
        print("Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables")
    else:
        asyncio.run(test_linkedin_auth())

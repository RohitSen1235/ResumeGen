import os
import json
import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LinkedInOAuth:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        
        # Set redirect URI based on production mode
        prod_mode = os.getenv('PROD_MODE', 'False').lower() == 'true'
        prod_host = os.getenv('PROD_HOST', 'localhost')
        
        if prod_mode and prod_host != 'localhost':
            self.redirect_uri = f"https://{prod_host}/auth/linkedin/callback"
        else:
            self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost/auth/linkedin/callback')
        
        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn OAuth credentials not configured")
        
        # LinkedIn OAuth URLs
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.profile_url = "https://api.linkedin.com/v2/userinfo"
        self.email_url = "https://api.linkedin.com/v2/userinfo"
        
        # OAuth scopes for LinkedIn (OpenID Connect standard)
        self.scopes = [
            "openid",
            "profile",
            "email"
        ]
        
        # Only use endpoints that work with basic profile scope
        self.summary_url = None  # Not available with basic scope
        self.positions_url = None  # Requires additional permissions
        self.education_url = None  # Requires additional permissions
        self.skills_url = None  # Requires additional permissions
    
    def get_authorization_url(self, state: str) -> str:
        """Generate LinkedIn OAuth authorization URL"""
        if not self.client_id:
            raise HTTPException(status_code=500, detail="LinkedIn OAuth not configured")
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(self.scopes)
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Dict:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            raise HTTPException(status_code=500, detail="LinkedIn OAuth not configured")
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"LinkedIn token exchange failed: {response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            return response.json()
    
    async def get_user_profile(self, access_token: str) -> Dict:
        """Get user profile information from LinkedIn"""
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_data = {}
        
        async with httpx.AsyncClient() as client:
            try:
                # Get basic profile info
                profile_response = await client.get(self.profile_url, headers=headers)
                if profile_response.status_code != 200:
                    logger.error(f"LinkedIn profile fetch failed: {profile_response.text}")
                    raise HTTPException(status_code=400, detail="Failed to fetch LinkedIn profile")
                
                profile_data = profile_response.json()
                
                # Extract basic profile information
                email = profile_data.get("email", "")
                given_name = profile_data.get("given_name", "")
                family_name = profile_data.get("family_name", "")
                name = profile_data.get("name", f"{given_name} {family_name}".strip())
                
                # Format response with only available data
                profile = {
                    "id": profile_data.get("sub"),
                    "first_name": given_name,
                    "last_name": family_name,
                    "email": email,
                    "profile_picture": profile_data.get("picture"),
                    "summary": "",
                    "positions": [],
                    "education": [],
                    "skills": []
                }
                
                # Convert positions to schema format
                if profile["positions"]:
                    profile["positions"] = [{
                        "id": pos.get("id"),
                        "title": pos.get("title"),
                        "company_name": pos.get("companyName"),
                        "location": pos.get("locationName"),
                        "start_date": pos.get("startDate", {}).get("year"),
                        "end_date": pos.get("endDate", {}).get("year") if "endDate" in pos else None,
                        "description": pos.get("description"),
                        "is_current": pos.get("isCurrent", False)
                    } for pos in profile["positions"]]
                
                # Convert education to schema format
                if profile["education"]:
                    profile["education"] = [{
                        "id": edu.get("id"),
                        "school_name": edu.get("schoolName"),
                        "degree": edu.get("degreeName"),
                        "field_of_study": edu.get("fieldOfStudy"),
                        "start_date": edu.get("startDate", {}).get("year"),
                        "end_date": edu.get("endDate", {}).get("year") if "endDate" in edu else None,
                        "description": edu.get("description")
                    } for edu in profile["education"]]
                
                # Convert skills to schema format
                if profile["skills"]:
                    profile["skills"] = [{
                        "id": skill.get("id"),
                        "name": skill.get("name"),
                        "proficiency": skill.get("proficiencyLevel")
                    } for skill in profile["skills"]]
                
                # Log the complete profile data before returning
                logger.info("Successfully fetched LinkedIn profile data:")
                logger.info(f"ID: {profile.get('id')}")
                logger.info(f"Name: {profile.get('first_name')} {profile.get('last_name')}")
                logger.info(f"Email: {profile.get('email')}")
                logger.info(f"Profile Picture: {profile.get('profile_picture')}")
                logger.info(f"Summary: {profile.get('summary')}")
                logger.info(f"Positions: {len(profile.get('positions', []))} positions")
                logger.info(f"Education: {len(profile.get('education', []))} education entries")
                logger.info(f"Skills: {len(profile.get('skills', []))} skills")
                logger.debug("Full profile data:\n" + json.dumps(profile, indent=2))
                return profile
                
            except Exception as e:
                logger.error(f"Error fetching LinkedIn profile: {str(e)}", exc_info=True)
                raise HTTPException(status_code=500, detail="Error fetching LinkedIn profile data")
    
    def _extract_profile_picture(self, profile_data: Dict) -> Optional[str]:
        """Extract profile picture URL from LinkedIn profile data"""
        try:
            profile_picture = profile_data.get("profilePicture", {})
            display_image = profile_picture.get("displayImage~", {})
            elements = display_image.get("elements", [])
            
            if elements:
                # Get the largest image
                largest_image = max(elements, key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("storageSize", {}).get("width", 0))
                identifiers = largest_image.get("identifiers", [])
                if identifiers:
                    return identifiers[0].get("identifier")
        except Exception as e:
            logger.error(f"Error extracting profile picture: {str(e)}")
            return None
        
        return None

# Global instance
linkedin_oauth = LinkedInOAuth()

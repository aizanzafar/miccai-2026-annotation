import requests
import base64
import json
from datetime import datetime

def save_to_github(annotations, annotator_id):
    """
    Automatically save annotations to GitHub using GitHub API.
    
    Args:
        annotations: List of annotation dictionaries
        annotator_id: Annotator's ID for filename
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import streamlit as st
        
        # Get GitHub credentials from Streamlit secrets
        token = st.secrets.get("github_token", "")
        repo = st.secrets.get("github_repo", "aizanzafar/miccai-2026-annotation")
        branch = st.secrets.get("github_branch", "main")
        
        if not token:
            return False, "GitHub token not configured. Using manual download instead."
        
        # Prepare file content
        filename = f"annotations/{annotator_id}.json"
        content = json.dumps(annotations, indent=2)
        content_bytes = content.encode('utf-8')
        content_b64 = base64.b64encode(content_bytes).decode('utf-8')
        
        # GitHub API endpoint
        api_url = f"https://api.github.com/repos/{repo}/contents/{filename}"
        
        # Headers
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check if file exists (to get SHA for update)
        response = requests.get(api_url, headers=headers, params={"ref": branch})
        
        # Prepare commit data
        commit_data = {
            "message": f"Auto-save: {annotator_id} - {len(annotations)} annotations ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
            "content": content_b64,
            "branch": branch
        }
        
        # If file exists, add SHA for update
        if response.status_code == 200:
            commit_data["sha"] = response.json()["sha"]
        
        # Create/update file
        response = requests.put(api_url, headers=headers, json=commit_data)
        
        if response.status_code in [200, 201]:
            return True, f"✅ Auto-saved {len(annotations)} annotations to GitHub!"
        else:
            return False, f"❌ GitHub save failed: {response.status_code} - {response.text[:100]}"
            
    except Exception as e:
        return False, f"❌ Error saving to GitHub: {str(e)}"


def load_from_github(annotator_id):
    """
    Load existing annotations from GitHub.
    
    Args:
        annotator_id: Annotator's ID for filename
    
    Returns:
        list: Existing annotations or empty list if not found
    """
    try:
        import streamlit as st
        
        # Get GitHub credentials from Streamlit secrets
        token = st.secrets.get("github_token", "")
        repo = st.secrets.get("github_repo", "aizanzafar/miccai-2026-annotation")
        branch = st.secrets.get("github_branch", "main")
        
        if not token:
            return []
        
        # Prepare file path
        filename = f"annotations/{annotator_id}.json"
        
        # GitHub API endpoint
        api_url = f"https://api.github.com/repos/{repo}/contents/{filename}"
        
        # Headers
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Try to get file
        response = requests.get(api_url, headers=headers, params={"ref": branch})
        
        if response.status_code == 200:
            # Decode content
            content_b64 = response.json()["content"]
            content_bytes = base64.b64decode(content_b64)
            content_str = content_bytes.decode('utf-8')
            annotations = json.loads(content_str)
            return annotations
        else:
            return []
            
    except Exception as e:
        return []


def test_github_connection():
    """Test if GitHub API is accessible with current token."""
    try:
        import streamlit as st
        token = st.secrets.get("github_token", "")
        repo = st.secrets.get("github_repo", "aizanzafar/miccai-2026-annotation")
        
        if not token:
            return False, "No GitHub token configured"
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Test connection by getting repo info
        response = requests.get(f"https://api.github.com/repos/{repo}", headers=headers)
        
        if response.status_code == 200:
            return True, "✅ GitHub connection successful"
        else:
            return False, f"❌ GitHub connection failed: {response.status_code}"
            
    except Exception as e:
        return False, f"❌ Connection error: {str(e)}"

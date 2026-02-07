import msal
import os
import atexit
import logging
from .config import Config

# Cache file in the user's home directory (or local)
CACHE_FILE = ".token_cache.bin"

def _load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())
    
    # Save cache on exit
    atexit.register(lambda: open(CACHE_FILE, "w").write(cache.serialize()) if cache.has_state_changed else None)
    return cache

def get_access_token():
    """
    Acquires an access token using MSAL (Interactive or Silent).
    """
    app = msal.PublicClientApplication(
        Config.CLIENT_ID, 
        authority=Config.AUTHORITY,
        token_cache=_load_cache()
    )

    result = None
    accounts = app.get_accounts()
    
    if accounts:
        # Try to get token silently
        logging.info(f"Found account in cache: {accounts[0]['username']}")
        result = app.acquire_token_silent(Config.SCOPES, account=accounts[0])

    if not result:
        # Interactive login (launches browser)
        print(">>> Launching browser for login... <<<")
        
        try:
             # Try first with explicit localhost redirect if registered
             result = app.acquire_token_interactive(scopes=Config.SCOPES, port=8080)
        except Exception as e:
             logging.warning(f"Interactive browser failed: {e}. Trying device flow as fallback...")
             # Initiate Device Code Flow (safer for terminal apps)
             flow = app.initiate_device_flow(scopes=Config.SCOPES)
             if "user_code" not in flow:
                  raise ValueError("Failed to create device flow")

             print(flow["message"])
             result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result["access_token"]
    else:
        error = result.get("error")
        desc = result.get("error_description")
        raise Exception(f"Could not acquire token: {error} - {desc}")

if __name__ == "__main__":
    try:
        token = get_access_token()
        print("Access token acquired successfully!")
        print(f"Token (first 20 chars): {token[:20]}...")
    except Exception as e:
        print(f"Auth failed: {e}")

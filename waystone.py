import requests
import json
import datetime
import base64
import argparse

# Constants
TOKEN_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
ROADTOOLS_AUTH_FILE = ".roadtools_auth"

def decode_jwt(token):
    try:
        payload_base64 = token.split('.')[1]
        payload_base64 += '=' * (4 - len(payload_base64) % 4)  # Add padding
        payload = json.loads(base64.urlsafe_b64decode(payload_base64))
        return payload
    except Exception as e:
        print(f"[-] Error decoding JWT: {e}")
        return None

def exchange_code_for_token(auth_code, tenant_id, client_id, redirect_uri, user_agent):
    """ Exchange the authorization code for an access token """
    token_url = TOKEN_URL_TEMPLATE.format(tenant=tenant_id)
    
    data = {
        "client_id": client_id,
        "grant_type": "authorization_code",
        "scope": "https://graph.windows.net/.default offline_access openid profile",
        "code": auth_code,
        "redirect_uri": redirect_uri
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": user_agent
    }

    print("[*] Requesting access token...")
    response = requests.post(token_url, data=data, headers=headers)
    
    if response.status_code != 200:
        print(f"[-] Failed to get token: {response.text}")
        return None

    return response.json()

def save_roadtools_auth(token_response):
    """ Convert OAuth token response to ROADTools format and saves it to .roadtools_auth """
    expires_on = datetime.datetime.now() + datetime.timedelta(seconds=token_response["expires_in"])
    
    # Decode tenant ID from the ID token
    id_token_payload = decode_jwt(token_response.get("id_token", ""))
    tenant_id = id_token_payload.get("tid", "unknown-tenant")

    roadtools_auth = {
        "tokenType": token_response["token_type"],
        "expiresOn": expires_on.strftime("%Y-%m-%d %H:%M:%S"),
        "tenantId": tenant_id,
        "_clientId": "1b730954-1685-4b74-9bfd-dac224a7b894",  # Microsoft Entra Client ID - used by ROADTools by default.
        "accessToken": token_response["access_token"],
        "refreshToken": token_response["refresh_token"],
        "idToken": token_response["id_token"]
    }

    with open(ROADTOOLS_AUTH_FILE, "w") as f:
        json.dump(roadtools_auth, f, indent=4)

    print(f"[+] Successfully saved tokens to {ROADTOOLS_AUTH_FILE}")

def main():
    parser = argparse.ArgumentParser(description="Exchange OAuth Code for Access Token & Save in ROADTools Format")
    
    parser.add_argument("-c", "--auth_code", required=True, help="Authorization Code from Microsoft Login")
    parser.add_argument("-t", "--tenant_id", required=True, help="Azure Tenant ID (or 'organizations')")
    parser.add_argument("-u", "--user_agent", default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/131.0.2903.86", 
                        help="Set a custom user agent for the request, default is Edge UA as of 03/05/2025.")
    parser.add_argument("-r", "--redirect_uri", default="https://login.microsoftonline.com/common/oauth2/nativeclient",
                        help="Redirect URI used in authentication")
    parser.add_argument("--client_id", default="1b730954-1685-4b74-9bfd-dac224a7b894",
                        help="Client ID (Default: Microsoft Entra ID - same used by ROADTools.)")

    args = parser.parse_args()

    token_response = exchange_code_for_token(args.auth_code, args.tenant_id, args.client_id, args.redirect_uri, args.user_agent)

    if token_response:
        save_roadtools_auth(token_response)
        print("[+] Authentication successful! You can now use ROADTools.")

if __name__ == "__main__":
    main()

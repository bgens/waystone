# Waystone

## Overview

This script automates the process of exchanging an **OAuth authorization code** for an **access token** and formatting the output for use with **ROADTools**. The script:
- Exchanges an authorization code for an access token using Azure AD (Entra ID).
- Extracts the `tenantId` from the ID token.
- Saves the response in **ROADTools format** (`.roadtools_auth`).

## Features

- Uses `argparse` for command-line input.
- Supports custom **User-Agent** headers.
- Extracts `tenantId` automatically from the ID token.
- Saves output in **ROADTools-compatible JSON format**.
- Uses the **default ROADTools client ID** for authentication.

## Installation

**Clone the Repository**
   ```bash
   git clone https://github.com/bgens/waystone.git
   cd waystone
   ```

## Usage

### 1. Obtain an Authorization Code

The intent here is for you to obtain the authorization code yourself and provide it to the script. 

Yes, there are other ways to get to the JWT or generate an authorization token, but my use case required
manually grabbing the token via the following process due environment specific constraints. 

To get an authorization code, visit the following URL in your browser, replacing `{tenant}` as needed. 

Note, `{tenant}` can also be organization or you can try common and hope it sorts itself out:

```
https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?
client_id=1b730954-1685-4b74-9bfd-dac224a7b894
&response_type=code
&redirect_uri=https%3A%2F%2Flogin.microsoftonline.com%2Fcommon%2Foauth2%2Fnativeclient
&scope=offline_access%20openid%20profile%20https%3A%2F%2Fgraph.windows.net%2F.default
&state=12345
&prompt=select_account
```

After logging in and completing MFA (if required), you will be redirected to a URL like:

```
https://login.microsoftonline.com/common/oauth2/nativeclient?code=YOUR_AUTH_CODE&state=12345
```

The page should be blank but take note of the params in the URL, this is what we care about.

Copy the value of `code=YOUR_AUTH_CODE`.

### 2. Run the Script

Run the script with the authorization code and tenant ID:

```bash
python waystone.py -c "AUTHORIZATION_CODE_HERE" -t "TENANT_ID_HERE"
```

Optional parameters:
- `--client_id` (Default: `1b730954-1685-4b74-9bfd-dac224a7b894`)
- `--redirect_uri` (Default: `https://login.microsoftonline.com/common/oauth2/nativeclient`)
- `--user_agent` (Set a **custom User-Agent**)

Example with a custom User-Agent:

```bash
python waystone.py -c "AUTHORIZATION_CODE_HERE" -t "TENANT_ID_HERE" -u "CustomUserAgent/1.0"
```

### 3. Verify the Output

Once complete, the script will generate a `.roadtools_auth` file:

```json
{
    "tokenType": "Bearer",
    "expiresOn": "2025-03-06 12:34:56",
    "tenantId": "your-tenant-id-here",
    "_clientId": "1b730954-1685-4b74-9bfd-dac224a7b894",
    "accessToken": "your_access_token_here",
    "refreshToken": "your_refresh_token_here",
    "idToken": "your_id_token_here"
}
```

### 4. Use the Token with ROADTools

Export the token file path:


## Troubleshooting

### Access Token Starts with `1.` Instead of `eyJ`
If your access token does not start with `eyJ` (a JWT), you may have an **opaque token**. Ensure that:
- You are using the **v2.0 token endpoint**.
- You are requesting the correct scope (`https://graph.windows.net/.default`).

### Refreshing the Token
The `.roadtools_auth` file contains a `refreshToken`, which can be used to obtain a new `accessToken` without re-authenticating.

At some point I'll add a feature to use refresh tokens for you but until then google it :)

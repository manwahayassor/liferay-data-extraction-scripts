import requests
import json
import argparse
import sys
from requests.auth import HTTPBasicAuth

# Cache for role details to avoid redundant API calls
role_cache = {}

def get_role_details(base_url, auth, erc):
    """
    Fetches detailed information for a role by its external reference code.
    """
    if not erc:
        return None
        
    if erc in role_cache:
        return role_cache[erc]
    
    url = f"{base_url.rstrip('/')}/o/headless-admin-user/v1.0/roles/by-external-reference-code/{erc}"
    try:
        print(f"Fetching role details for ERC: {erc}")
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        role_data = response.json()
        role_cache[erc] = role_data
        return role_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching role details for {erc}: {e}", file=sys.stderr)
        return None

def get_all_items(base_url, endpoint, auth):
    """
    Fetches all items from a paginated Liferay Headless API endpoint.
    """
    items = []
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    while url:
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            data = response.json()
            
            items.extend(data.get('items', []))
            
            # Check for next page
            actions = data.get('actions', {})
            next_url = actions.get('next', {}).get('href')
            
            if next_url:
                url = next_url
            else:
                # Fallback for some endpoints
                url = data.get('nextPageURL')
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}", file=sys.stderr)
            break
            
    return items

def transform_user(base_url, auth, user_item):
    """
    Transforms a Liferay user-account item into the requested format,
    enriching it with detailed role permissions.
    """
    role_briefs = user_item.get('roleBriefs', [])
    permissions = []
    
    for rb in role_briefs:
        erc = rb.get('externalReferenceCode')
        role_details = get_role_details(base_url, auth, erc)
        
        # Determine role type string
        role_type_val = rb.get('roleType')
        role_type_str = role_type_val if role_type_val is not None else None
        
        if role_details:
            # Flatten actionIds from rolePermissions list
            action_ids = []
            role_perms = role_details.get('rolePermissions', [])
            if isinstance(role_perms, list):
                for perm in role_perms:
                    action_ids.extend(perm.get('actionIds', []))
            elif isinstance(role_perms, dict):
                # Fallback if it's a single object in some versions
                action_ids.extend(role_perms.get('actionIds', []))
            
            # Remove duplicates
            action_ids = list(set(action_ids))

            permissions.append({
                "actionIds": action_ids,
                "roleExternalReferenceCode": erc,
                "roleName": role_details.get('name'),
                "roleType": role_type_str
            })
        else:
            # Fallback to roleBrief data if detailed lookup fails
            permissions.append({
                "actionIds": [],
                "roleExternalReferenceCode": erc,
                "roleName": rb.get('name'),
                "roleType": role_type_str
            })
        
    return {
        "alternateName": user_item.get("alternateName"),
        "birthDate": user_item.get("birthDate"),
        "emailAddress": user_item.get("emailAddress"),
        "externalReferenceCode": user_item.get("externalReferenceCode"),
        "familyName": user_item.get("familyName"),
        "givenName": user_item.get("givenName"),
        "jobTitle": user_item.get("jobTitle"),
        "languageDisplayName": user_item.get("languageDisplayName"),
        "languageId": user_item.get("languageId"),
        "name": user_item.get("name"),
        "password":"default_12345",
        "permissions": permissions
    }

def main():
    parser = argparse.ArgumentParser(description="Extract Liferay user-accounts with detailed permissions.")
    parser.add_argument("--url", required=True, help="Base URL of Liferay")
    parser.add_argument("--user", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--output", default="users_with_permissions.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    auth = HTTPBasicAuth(args.user, args.password)
    base_url = args.url
    
    print("Fetching user accounts...")
    # Updated endpoint with pageSize=200
    user_accounts = get_all_items(base_url, "/o/headless-admin-user/v1.0/user-accounts?pageSize=200", auth)
    
    print(f"Processing {len(user_accounts)} users...")
    transformed_users = []
    for u in user_accounts:
        transformed_users.append(transform_user(base_url, auth, u))
    
    print(f"Writing {len(transformed_users)} users to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(transformed_users, f, indent=4)
        
    print("Extraction complete.")

if __name__ == "__main__":
    main()

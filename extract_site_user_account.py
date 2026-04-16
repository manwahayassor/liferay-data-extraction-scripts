import requests
import json
import argparse
import sys
from requests.auth import HTTPBasicAuth

def get_all_items(base_url, endpoint, auth):
    """
    Fetches all items from a paginated Liferay Headless API endpoint.
    """
    items = []
    # If endpoint already has parameters, we might need to handle it carefully.
    # But for simplicity, we'll just append it to base_url.
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    while url:
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            data = response.json()
            
            items.extend(data.get('items', []))
            
            # Check for next page in 'actions'
            actions = data.get('actions', {})
            next_url = actions.get('next', {}).get('href')
            
            if next_url:
                url = next_url
            else:
                # Some Liferay versions/endpoints might use 'nextPageURL'
                url = data.get('nextPageURL')
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}", file=sys.stderr)
            break
            
    return items

def main():
    parser = argparse.ArgumentParser(description="Extract site user accounts from Liferay.")
    parser.add_argument("--url", required=True, help="Base URL of Liferay")
    parser.add_argument("--user", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--site-id", required=True, help="Site ID to extract user accounts from")
    parser.add_argument("--output", default="site_user_accounts.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    auth = HTTPBasicAuth(args.user, args.password)
    base_url = args.url
    site_id = args.site_id
    
    endpoint = f"/o/headless-admin-user/v1.0/sites/{site_id}/user-accounts?pageSize=100"
    
    print(f"Starting extraction for site ID: {site_id}...")
    all_users = get_all_items(base_url, endpoint, auth)
    
    # Filter items to keep specific fields
    filtered_users = []
    for user in all_users:
        filtered_user = {
            "alternateName": user.get("alternateName"),
            "externalReferenceCode": user.get("externalReferenceCode"),
            "name": user.get("name"),
            "givenName": user.get("givenName"),
            "familyName": user.get("familyName"),
            "jobTitle": user.get("jobTitle"),
            "emailAddress": user.get("emailAddress"),
            "siteBriefs": [
                {
                    "externalReferenceCode": "bks-fin-portail",
                    "descriptiveName":"BKS Fin Portail",
                    "name":"BKS Fin Portail"
                }
            ]
        }
        filtered_users.append(filtered_user)
            
    print(f"Writing {len(filtered_users)} user accounts to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(filtered_users, f, indent=4)
        
    print("Extraction complete.")

if __name__ == "__main__":
    main()

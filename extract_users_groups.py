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

def main():
    parser = argparse.ArgumentParser(description="Extract Liferay user-groups.")
    parser.add_argument("--url", required=True, help="Base URL of Liferay")
    parser.add_argument("--user", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--output", default="user_groups.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    auth = HTTPBasicAuth(args.user, args.password)
    base_url = args.url
    
    print("Fetching user groups...")
    # Updated endpoint to fetch user groups
    user_groups_data = get_all_items(base_url, "/o/headless-admin-user/v1.0/user-groups?pageSize=100", auth)
    
    # Keep only 'name' and 'description'
    filtered_groups = [
        {
            "name": group.get("name"),
            "externalReferenceCode": group.get("externalReferenceCode"),
            "description": group.get("description")
        }
        for group in user_groups_data
    ]
    
    print(f"Writing {len(filtered_groups)} user groups to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(filtered_groups, f, indent=4)
        
    print("Extraction complete.")

if __name__ == "__main__":
    main()

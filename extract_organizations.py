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
                url = None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}", file=sys.stderr)
            break
            
    return items

def fetch_flat_with_parent(base_url, auth, org_item, parent_snapshot=None):
    """
    Recursively fetches organizations and returns a flat list where each
    org includes its immediate parent's data.
    """
    org_id = org_item.get('id')
    print(f"Processing: {org_item.get('name')} (ID: {org_id})")

    # Current organization data
    current_org = {
        "externalReferenceCode": org_item.get("externalReferenceCode"),
        "name": org_item.get("name"),
        "location": org_item.get("location"),
        "parentOrganization": parent_snapshot
    }

    results = [current_org]

    # Snaphost of current org to pass as 'parent' to its children
#    current_snapshot = {
#        "externalReferenceCode": current_org["externalReferenceCode"],
#        "name": current_org["name"],
#        "location": current_org["location"]
#    }

    current_snapshot = {
        "externalReferenceCode": current_org["externalReferenceCode"]
    }

    # Fetch immediate children
    children_endpoint = f"/o/headless-admin-user/v1.0/organizations/{org_id}/child-organizations"
    children = get_all_items(base_url, children_endpoint, auth)
    
    # Recursively fetch children and add to the flat list
    for child in children:
        results.extend(fetch_flat_with_parent(base_url, auth, child, current_snapshot))
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Extract a flat list of Liferay organizations with parent references.")
    parser.add_argument("--url", required=True, help="Base URL of Liferay")
    parser.add_argument("--user", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--root-id", help="Start extraction from this specific organization ID")
    parser.add_argument("--output", default="organizations_with_parent.json", help="Output JSON file")
    
    args = parser.parse_args()
    
    auth = HTTPBasicAuth(args.user, args.password)
    base_url = args.url
    
    flat_list = []
    
    if args.root_id:
        try:
            print(f"Fetching root organization {args.root_id}...")
            resp = requests.get(f"{base_url.rstrip('/')}/o/headless-admin-user/v1.0/organizations/{args.root_id}", auth=auth)
            resp.raise_for_status()
            root_item = resp.json()
            flat_list.extend(fetch_flat_with_parent(base_url, auth, root_item))
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Fetching top-level organizations...")
        all_orgs = get_all_items(base_url, "/o/headless-admin-user/v1.0/organizations", auth)
        # Start from organizations that have no parentId
        top_level = [org for org in all_orgs if not org.get('parentId')]
        
        for org in top_level:
            flat_list.extend(fetch_flat_with_parent(base_url, auth, org))
            
    print(f"Writing {len(flat_list)} organizations to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(flat_list, f, indent=4)
        
    print("Extraction complete.")

if __name__ == "__main__":
    main()

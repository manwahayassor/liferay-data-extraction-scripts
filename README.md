# Liferay Data Extraction Scripts

A collection of Python scripts to extract data from Liferay using Headless APIs. These scripts are designed for migrations, audits, or data synchronization tasks.

## Prerequisites

- Python 3.x
- `requests` library

You can install the dependencies using pip:
```bash
pip install requests
```

## Available Scripts

| Script | Description | Default Output |
| :--- | :--- | :--- |
| `extract_organizations.py` | Extracts organizations including parent-child relationships. | `organizations_with_parent.json` |
| `extract_site_user_account.py` | Extracts user accounts associated with sites. | `site_user_accounts.json` |
| `extract_users_and_all_briefs.py` | Extracts users with all associated briefs (sites, organizations, roles, user groups). | `users_with_all_brefs.json` |
| `extract_users_and_permissions.py` | Extracts user accounts with detailed permissions. | `users_with_permissions.json` |
| `extract_users_groups.py` | Extracts user groups. | `user_groups.json` |

## Usage

Each script follows a similar command-line interface.

### Standard Arguments

- `--url`: The base URL of your Liferay instance (e.g., `http://localhost:8080`).
- `--user`: Admin username/email for authentication.
- `--password`: Admin password for authentication.
- `--output` (optional): Path to the output JSON file.

### Script-Specific Arguments

Some scripts require or support additional arguments:

- **`extract_site_user_account.py`**:
  - `--site-id` (required): The ID of the site to extract users from.
- **`extract_organizations.py`**:
  - `--root-id` (optional): Start extraction from a specific organization ID.

### Examples

#### Extract Organizations
```bash
python extract_organizations.py --url http://localhost:8080 --user test@liferay.com --password test
```

#### Extract Site User Accounts
```bash
python extract_site_user_account.py --url http://localhost:8080 --user test@liferay.com --password test --site-id 12345
```

#### Extract Users with All Briefs
```bash
python extract_users_and_all_briefs.py --url https://mysite.com --user admin --password "p=*12_3@45/6" --output my_users.json
```

## Troubleshooting

- **Permissions**: Ensure the user provided has administrative access to the Headless APIs.
- **API Versions**: These scripts are built for Liferay Headless Admin User v1.0. Ensure your Liferay version supports these endpoints.
- **Connectivity**: Verify the `--url` is accessible from your machine and does not have a trailing slash if the script handles it (though most scripts here use `.rstrip('/')`).

## Security Note

Ensure you handle admin credentials securely. Avoid sharing logs or command history that may contain plain-text passwords.

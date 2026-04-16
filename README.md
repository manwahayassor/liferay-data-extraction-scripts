# Liferay data extraction scripts
how to use

## Extract user Accounts and permissions
python extract_users_and_permissions.py --url <site-urls> --user <username> --password <passeword>
exemple : python extract_users_and_permissions.py --url http://localhost:8080 --user admin --password p=*12_3@45/6

## Extract Site User Accounts
python extract_site_user_account.py --url <site-urls> --user <username> --password <passeword>

## Extract Users Accounts with all briefs 
python extract_users_and_all_briefs.py --url <site-urls> --user <username> --password <passeword>

## Extract Users Groups 
python extract_users_groups.py --url <site-urls> --user <username> --password <passeword>

## Extract Organizations
python extract_organizations.py --url <site-urls> --user <username> --password <passeword>

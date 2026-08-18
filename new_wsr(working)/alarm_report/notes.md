1. PS C:\Users\2000107191\OneDrive - Hexaware Technologies\Desktop\alarm_reports\Alarm_Reports\Alarm_Reports> aws configure sso
2. SSO session name (Recommended): SR
3. SSO start URL [None]: https://mic-digital.awsapps.com/start/#/
4. SSO region [None]: us-east-1
5. SSO registration scopes [sso:account:access]:
Attempting to automatically open the SSO authorization page in your default browser.
If the browser does not open or you wish to use a different device to authorize this request, open the following URL:

https://oidc.us-east-1.amazonaws.com/authorize?response_type=code&client_id=j6rKbFZEy4A0SF36_wNf43VzLWVhc3QtMQ&redirect_uri=http%3A%2F%2F127.0.0.1%3A58101%2Foauth%2Fcallback&state=78982785-87ea-4832-971d-f4dc5edb6dbe&code_challenge_method=S256&scopes=sso%3Aaccount%3Aaccess&code_challenge=EQvxT1s9fBUscvn_EOYumL8ZUrZ6EXlKyLL3PPFg2hc
There are 4 AWS accounts available to you.
Using the account ID 403872143046
The only role available to you is: Paymentgateway_prod_L2
Using the role name "Paymentgateway_prod_L2"
Default client Region [None]: us-east-1
CLI default output format (json if not specified) [None]: json
Profile name [Paymentgateway_prod_L2-403872143046]: pg-prod
To use this profile, specify the profile name using --profile, as shown:

aws sts get-caller-identity --profile pg-prod

6. PS C:\Users\2000107191\OneDrive - Hexaware Technologies\Desktop\alarm_reports\Alarm_Reports\Alarm_Reports> python daily_alarm_report.py  
Available AWS profiles:
  1) pg-prod
Which profile do you want to log in with? (enter a number or the profile name): 1
Using AWS SSO profile: pg-prod
Authenticated as: arn:aws:sts::403872143046:assumed-role/AWSReservedSSO_Paymentgateway_prod_L2_fe692010134fbdab/SadhuR@hexaware.com\n
Could not read account alias, falling back to account ID: An error occurred (AccessDenied) when calling the ListAccountAliases operation: User: arn:aws:sts::403872143046:assumed-role/AWSReservedSSO_Paymentgateway_prod_L2_fe692010134fbdab/SadhuR@hexaware.com is not authorized to perform: iam:ListAccountAliases on resource: * because no identity-based policy allows the iam:ListAccountAliases action
Which timezone do you want the report in? (UTC/IST): IST
Using timezone: IST (UTC+5:30)
Do you want alarm history for TODAY, YESTERDAY, or the LAST 1 WEEK? (today/yesterday/week): yesterday
Total alarm triggers for yesterday (IST): 191

Fetching all alarms for the ok-inalarm sheet...
Total alarms found in account: 295
Report generated with 191 alarm triggers and 295 total alarms -> C:\Users\2000107191\OneDrive - Hexaware Technologies\Desktop\alarm_reports\Alarm_Reports\Alarm_Reports\reports\AlarmReport_403872143046_IST_Yesterday_2026-08-13.xlsx

7. aws configure list-profiles
8. notepad $env:USERPROFILE\.aws\config   (optional step if profiles are created and to delete)
9. If session expired: aws sso login --profile profile_name ex: aws sso login --profile pg-prod
10. aws sso logout  (This removes cached SSO sessions.)

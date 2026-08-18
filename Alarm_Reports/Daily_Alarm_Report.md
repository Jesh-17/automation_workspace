# Daily Alarm Report

Reads CloudWatch alarm history directly (no DynamoDB, no logger Lambda) and builds a daily/weekly Excel report with two sheets. You choose the **timezone** (UTC or IST) and the **period** (today, yesterday, or last 7 days) each time you run it — no need for separate UTC/IST scripts.

1. **`<Account> Alarm Report`** — every alarm that went **into `ALARM`** state during the period you choose (today, yesterday, or last 7 days), with Date/Time shown in the timezone you choose (UTC or IST).
2. **`ok-inalarm`** — **every** alarm in the account, with its current state (`OK`, `ALARM`, or `INSUFFICIENT_DATA`), regardless of whether it triggered during the period.

---

## 1. Install Python

If you don't already have Python installed:

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest Python 3 installer for your OS.
2. **Windows:** run the installer and make sure you check **"Add python.exe to PATH"** before clicking Install.
3. **Mac:** run the installer package, or use `brew install python3` if you have Homebrew.
4. Verify it worked by opening a terminal / PowerShell and running:
   ```bash
   python --version
   ```
   or on some systems:
   ```bash
   python3 --version
   ```
   You should see something like `Python 3.11.x`.

## 2. Install the required packages

```bash
pip install boto3 openpyxl
```

(If `pip` isn't recognized, try `python -m pip install boto3 openpyxl`.)

---

## 3. AWS SSO configuration (one-time setup)

If your organization uses AWS SSO (most do) and you haven't set up a profile yet:

1. Run:
   ```bash
   aws configure sso
   ```
   (This requires the AWS CLI to be installed — [download here](https://aws.amazon.com/cli/) if you don't have it.)
2. You'll be prompted for:
   - **SSO session name** — any name you like, e.g. `my-sso`.
   - **SSO start URL** — your organization's AWS SSO portal URL (ask your AWS admin if you don't know it — looks like `https://your-org.awsapps.com/start`).
   - **SSO Region** — the region your SSO instance is hosted in.
   - It then opens your browser to log in via SSO and lets you pick the AWS account + IAM role you want this profile to use.
   - **Default client Region** — set this to wherever your CloudWatch alarms actually live (e.g. `us-east-1`, `ap-south-1`).
   - **CLI default output format** — `json` is fine.
   - **Profile name** — give it something memorable, e.g. `tigo-prod`, `pg-nonprod`. **This is the name you'll pick when the script asks which profile to use.**
3. This creates an entry like this in `~/.aws/config` (or `C:\Users\<you>\.aws\config` on Windows):
   ```ini
   [profile tigo-prod]
   sso_start_url = https://your-org.awsapps.com/start
   sso_region = us-east-1
   sso_account_id = 123456789012
   sso_role_name = YourRoleName
   region = us-east-1
   ```
4. Repeat this for every account you need a profile for (e.g. one for prod, one for nonprod).
5. **Every time your session expires** (SSO sessions typically last 8–12 hours), log in again before running the script:
   ```bash
   aws sso login --profile tigo-prod
   ```

---

## 4. Selecting a profile when you run the script

You don't have to edit any code to switch accounts. Every time you run the script:

- **If the `AWS_PROFILE` environment variable is set**, it's used automatically and you won't be asked anything:
  ```bash
  export AWS_PROFILE=tigo-prod        # Mac/Linux
  $env:AWS_PROFILE="tigo-prod"        # Windows PowerShell
  ```
- **Otherwise**, the script lists every profile it finds in your AWS config and asks you to pick one:
  ```
  Available AWS profiles:
    1) tigo-prod
    2) pg-nonprod
  Which profile do you want to log in with? (enter a number or the profile name):
  ```
  Type either the **number** (e.g. `1`) or the **exact profile name** (e.g. `tigo-prod`).
- **If no profiles exist at all**, it asks you to type a profile name manually.

**Which profile should you pick?** Whichever AWS account holds the CloudWatch alarms you want reported on — e.g. pick `tigo-prod` for the Tigo production account's alarms, `pg-nonprod` for PG's nonprod account, and so on.

---

## 5. Running the script

1. Make sure you're logged in to SSO for the profile you plan to use:
   ```bash
   aws sso login --profile tigo-prod
   ```
2. Open a terminal and go to the folder where the script is saved:
   ```bash
   cd path/to/folder
   ```
3. Run it:
   ```bash
   python daily_alarm_report_final.py
   ```
   (Windows: if `python` isn't recognized, try `py daily_alarm_report_final.py`.)
4. Answer the prompts:
   ```
   Available AWS profiles:
     1) tigo-prod
     2) pg-nonprod
   Which profile do you want to log in with? (enter a number or the profile name): 1
   Using AWS SSO profile: tigo-prod
   Authenticated as: arn:aws:sts::123456789012:assumed-role/...

   Which timezone do you want the report in? (UTC/IST): IST
   Using timezone: IST (UTC+5:30)

   Do you want alarm history for TODAY, YESTERDAY, or the LAST 1 WEEK? (today/yesterday/week): yesterday
   ```
5. Example output:
   ```
   Total alarm triggers for yesterday (IST): 4

   Fetching all alarms for the ok-inalarm sheet...
   Total alarms found in account: 87
   Report generated with 4 alarm triggers and 87 total alarms -> /path/to/reports/AlarmReport_tigo-prod_IST_Yesterday_2026-07-26.xlsx
   ```
6. Open the generated `.xlsx` file (in the `reports` folder by default) — it will have two tabs: the alarm-trigger report, and the `ok-inalarm` sheet showing every alarm's current state.

### Timezone and period options

- **Timezone (UTC or IST):** Asked first, every run. This controls both:
  - The Date/Time columns in the "Alarm Report" sheet.
  - Where the "today"/"yesterday" calendar-day boundaries fall (so IST + "yesterday" gives you the IST calendar day, not the UTC one).
- **Period (today / yesterday / last 1 week):**
  - `today` — from midnight (in the chosen timezone) up to now.
  - `yesterday` — the full previous calendar day (in the chosen timezone) — use this for a "previous day's report" scheduled the next morning.
  - `week` — the last 7 calendar days up to now.

---

## How severity is determined

For every alarm, in this order:
1. An explicit `Severity` or `Priority` **tag** on the alarm — used as-is if present.
2. If no tag, a **keyword guess** from the alarm's name (looks for `critical`, `crit`, `high`, `medium`, `med`, `low` — first match wins).
3. If nothing matches, defaults to **Medium**.

---

## Environment variables (optional)

| Variable      | Default       | Description                                              |
|---------------|---------------|------------------------------------------------------------|
| `OUTPUT_DIR`  | `./reports`   | Local folder to save the generated report into             |
| `AWS_REGION`  | `us-east-1`   | Region to read CloudWatch alarms from                       |
| `AWS_PROFILE` | *(none)*      | AWS profile to use — skips the interactive prompt if set    |

---

## IAM permissions required

Whatever identity the selected profile resolves to needs:

- `cloudwatch:DescribeAlarmHistory`
- `cloudwatch:DescribeAlarms`
- `cloudwatch:ListTagsForResource`
- `sts:GetCallerIdentity`
- `iam:ListAccountAliases` *(optional — used for the account name in the sheet/file name; falls back to the raw account ID if not granted)*

---

## ⚠️ Important notes

> **Note:** The script asks you to pick a timezone (UTC or IST) each time it runs, and reports all alarm timings — plus the today/yesterday/week boundaries — in that timezone. There's no need to keep separate UTC and IST versions of the script anymore.

> **Severity accuracy — "Medium" and "Low" are fallback guesses, not confirmed values:**
> The script only assigns an *accurate* severity when an alarm has an explicit `Severity`/`Priority` **tag** in AWS, or its name contains an obvious keyword (`critical`, `high`, etc.). If neither is present, it defaults to **Medium** — this is a **placeholder, not a verified severity**. So any alarm showing **Medium** or **Low** in the report should be treated as "not yet classified" rather than confirmed low-priority. To get correct severities, either:
> - Add a `Severity`/`Priority` tag to the alarm in AWS directly (recommended, most reliable), or
> - Manually review and correct the severity in the generated Excel sheet before sharing/acting on it.

---

## Known limitations / things to be aware of

- Only alarms that transitioned **into `ALARM`** (from `OK` or `INSUFFICIENT_DATA`) appear on the "Alarm Report" sheet — recoveries (`ALARM → OK`) aren't listed there, though the current state of every alarm (including recovered ones) is always visible on the `ok-inalarm` sheet.
- Excel sheet names are capped at 31 characters and can't contain `[ ] : * ? / \` — long account names get truncated automatically.
- Severity is only as accurate as your tags or naming convention — an alarm with no tag and no matching keyword in its name defaults to Medium, which may not reflect its true priority.
- The alarm ARN used for tag lookups on the "Alarm Report" sheet is reconstructed manually from account ID + region + alarm name; this assumes standard alarm names without characters that need URL-encoding.
- If zero alarms triggered in the period **and** zero alarms exist in the account at all, no file is generated — this is expected, not a bug.

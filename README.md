# Blogfa login tests

Target: the `LOGIN_URL` value in your local `.env` file.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run:

```bash
git clone --branch main https://github.com/Triplem8360/blogfa-login-tests.git
cd blogfa-login-tests
uv python install 3.12
uv sync --locked
uv run playwright install chromium
```

On Linux, install missing browser libraries with
`uv run playwright install --with-deps chromium`.

## Run

Create a local `.env` file from `.env.example` and set `LOGIN_URL`.
Set the account values to your test credentials, or leave them empty to skip
the successful login test. The `.env` file is ignored by Git.

```bash
uv run --env-file .env pytest
uv run --env-file .env pytest --headed
uv run --env-file .env pytest -m smoke
uv run --env-file .env pytest -m login
```

Each test gets a fresh browser context. Tests run sequentially against the live
site and need internet access. The `login` tests make four form submissions
using empty values or randomly generated unknown usernames, plus one successful
login when test credentials are configured.

`smoke` selects five basic form checks without submitting credentials.
`login` selects five form submission cases. These are custom pytest markers;
`-m` selects tests by marker.

If the Chromium download is blocked and Google Chrome is installed, try
`uv run --env-file .env pytest --browser-channel=chrome --headed -v` or
`uv run --env-file .env pytest --browser=firefox --headed -v`.

## Test account

Set `BLOGFA_USERNAME` and `BLOGFA_PASSWORD` in `.env` to your test account
credentials. uv loads the file when `--env-file .env` is used:

```bash
uv run --env-file .env pytest -m login --headed -v
uv run --env-file .env pytest -k test_valid_credentials_open_dashboard --headed -v
```

The successful login test checks the dashboard URL and the new-post link.
It is skipped when either credential is missing; invalid credentials fail the
test. Exported environment variables can also be used without an `.env` file.

## Coverage

The suite has ten test cases:

- Login form fields and submit button.
- Password masking.
- Username and password length limits.
- Password recovery link visibility and destination.
- Empty username, with and without a password.
- Unknown username, with an empty or invalid password.
- Successful login with the configured test account.

Blogfa currently reloads the form without a warning when the username is empty.
Unknown usernames show a Persian error message. Wrong passwords for existing
accounts are outside this suite. The recovery link test does not request a
password reset.

## Reports

Every run writes a self-contained HTML report to `reports/report.html`.
Open the report on Linux with:

```bash
xdg-open reports/report.html
```

Failure screenshots are saved separately under `test-results/`.
These generated files are ignored by Git. Network and browser setup errors
remain test errors; they are not skipped or reported as passes.

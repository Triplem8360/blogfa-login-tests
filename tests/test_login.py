import os
import re
from uuid import uuid4

import pytest
from playwright.sync_api import Page, expect

# Blogfa's labels are not linked to their inputs, so use the form field names.
USERNAME = 'input[name="usrid"]'
PASSWORD = 'input[name="ups"]'
LOGIN_BUTTON = "ورود به بخش مدیریت وبلاگ"
INVALID_PASSWORD = "Invalid-Password1"


def submit_login(page: Page) -> None:
    login_url = page.url
    with page.expect_response(
        lambda response: response.url == login_url and response.request.method == "POST"
    ) as response:
        page.get_by_role("button", name=LOGIN_BUTTON, exact=True).click()

    assert response.value.ok, f"Login submission returned HTTP {response.value.status}"
    expect(page).to_have_url(login_url)
    expect(page.locator("#frmLogin")).to_be_visible()


@pytest.mark.smoke
def test_login_form_is_visible(login_page: Page) -> None:
    expect(login_page).to_have_title(re.compile("BLOGFA", re.IGNORECASE))
    expect(login_page.locator(USERNAME)).to_be_visible()
    expect(login_page.locator(USERNAME)).to_be_editable()
    expect(login_page.locator(PASSWORD)).to_be_visible()
    expect(login_page.locator(PASSWORD)).to_be_editable()
    expect(
        login_page.get_by_role("button", name=LOGIN_BUTTON, exact=True)
    ).to_be_enabled()


@pytest.mark.smoke
def test_password_is_masked(login_page: Page) -> None:
    password = login_page.locator(PASSWORD)
    password.fill(INVALID_PASSWORD)

    expect(password).to_have_attribute("type", "password")
    expect(password).to_have_value(INVALID_PASSWORD)


@pytest.mark.smoke
@pytest.mark.parametrize(
    ("selector", "limit"),
    [(USERNAME, 61), (PASSWORD, 20)],
    ids=["username", "password"],
)
def test_input_length_is_limited(login_page: Page, selector: str, limit: int) -> None:
    field = login_page.locator(selector)
    expect(field).to_have_attribute("maxlength", str(limit))

    field.fill("x" * (limit + 1))

    expect(field).to_have_value("x" * limit)


@pytest.mark.smoke
def test_password_recovery_link_is_available(login_page: Page) -> None:
    recovery_link = login_page.get_by_role(
        "link", name=re.compile("کلمه عبور را فراموش")
    )

    expect(recovery_link).to_be_visible()
    expect(recovery_link).to_have_attribute("href", "/r/forget-password/?")


@pytest.mark.login
@pytest.mark.parametrize(
    "password", ["", INVALID_PASSWORD], ids=["both-empty", "username-empty"]
)
def test_empty_username_keeps_login_form(login_page: Page, password: str) -> None:
    login_page.locator(PASSWORD).fill(password)

    submit_login(login_page)

    # An empty username currently reloads the form without a warning.
    expect(login_page.locator(USERNAME)).to_have_value("")
    expect(login_page.locator(PASSWORD)).to_have_value("")
    expect(login_page.locator(".warningfull")).to_have_count(0)


@pytest.mark.login
@pytest.mark.parametrize(
    "password", ["", INVALID_PASSWORD], ids=["password-empty", "invalid-credentials"]
)
def test_unknown_username_is_rejected(login_page: Page, password: str) -> None:
    login_page.locator(USERNAME).fill(f"qa-{uuid4().hex}")
    login_page.locator(PASSWORD).fill(password)

    submit_login(login_page)

    warning = login_page.locator(".warningfull")
    expect(warning).to_be_visible()
    expect(warning).to_have_text("نام کاربری را اشتباه وارد کرده اید")
    expect(login_page.locator(USERNAME)).to_have_value("")
    expect(login_page.locator(PASSWORD)).to_have_value("")


@pytest.mark.login
@pytest.mark.skipif(
    not os.getenv("BLOGFA_USERNAME") or not os.getenv("BLOGFA_PASSWORD"),
    reason="Set BLOGFA_USERNAME and BLOGFA_PASSWORD to test successful login",
)
def test_valid_credentials_open_dashboard(login_page: Page) -> None:
    login_page.locator(USERNAME).fill(os.environ["BLOGFA_USERNAME"])
    login_page.locator(PASSWORD).fill(os.environ["BLOGFA_PASSWORD"])

    login_page.get_by_role("button", name=LOGIN_BUTTON, exact=True).click()

    expect(login_page).to_have_url(
        re.compile(
            r"https://www\.blogfa\.com/desktop/home\.aspx(?:\?.*)?$", re.IGNORECASE
        )
    )
    expect(
        login_page.get_by_role("link", name="نوشته جدید", exact=True)
    ).to_be_visible()
    expect(login_page.locator("#frmLogin")).to_have_count(0)

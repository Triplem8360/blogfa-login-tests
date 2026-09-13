import os

import pytest
from playwright.sync_api import Page


@pytest.fixture
def login_page(page: Page) -> Page:
    login_url = os.getenv("LOGIN_URL")
    if not login_url:
        pytest.fail(
            "Set LOGIN_URL in .env and run: uv run --env-file .env pytest",
            pytrace=False,
        )

    response = page.goto(login_url, wait_until="domcontentloaded")
    assert response is not None, "The login page did not return a response"
    assert response.ok, f"The login page returned HTTP {response.status}"
    return page

"""Integrated browser, responsive, keyboard, and accessibility verification.

Targets the local dev server by default. Set TERRALENS_E2E_URL to verify a deployment, e.g.
TERRALENS_E2E_URL=https://krishn1301.github.io/terralens-ai/ python tests/e2e.py
"""

import json
import os
import re
from pathlib import Path
from tempfile import gettempdir

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).parents[1]
URL = os.environ.get("TERRALENS_E2E_URL", "http://127.0.0.1:5173")
REMOTE = not URL.startswith(("http://127.0.0.1", "http://localhost"))
# Free-tier hosting can take up to a minute to wake the API from sleep.
API_TIMEOUT = 90000 if REMOTE else 10000
AXE = ROOT / "frontend" / "node_modules" / "axe-core" / "axe.min.js"
ARTIFACTS = Path(gettempdir()) / "terralens-e2e"
ARTIFACTS.mkdir(exist_ok=True)


def assert_no_overflow(page, label: str) -> None:
    overflow = page.evaluate(
        """() => [...document.querySelectorAll('*')]
        .filter((el) => el.getBoundingClientRect().right > document.documentElement.clientWidth + 1)
        .slice(0, 8).map((el) => `${el.tagName}.${el.className}`)"""
    )
    assert not overflow, f"{label} horizontal overflow: {overflow}"


def assert_accessible(page, label: str) -> None:
    page.add_script_tag(path=AXE)
    audit = page.evaluate("async () => await axe.run()")
    serious = [
        (item["id"], item["impact"], len(item["nodes"]))
        for item in audit["violations"]
        if item["impact"] in {"serious", "critical"}
    ]
    if serious:
        for item in audit["violations"]:
            if item["impact"] in {"serious", "critical"}:
                print(item["id"], [(node["target"], node["failureSummary"]) for node in item["nodes"][:12]])
    assert not serious, f"{label} axe violations: {serious}"


def run() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = context.new_page()
        errors: list[str] = []
        failed_requests: list[str] = []
        chat_payloads: list[dict] = []
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: errors.append(f"uncaught: {error}"))
        page.on("requestfailed", lambda request: failed_requests.append(f"{request.url} {request.failure}"))
        page.on(
            "response",
            lambda response: failed_requests.append(f"{response.url} {response.status}")
            if response.status >= 400
            else None,
        )
        page.on(
            "request",
            lambda request: chat_payloads.append(json.loads(request.post_data or "{}"))
            if request.url.endswith("/api/chat") and request.method == "POST"
            else None,
        )

        page.goto(URL)
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", level=1)).to_contain_text("Read the land")
        expect(page.get_by_role("button", name="Semi-arid wheat farm")).to_be_visible(timeout=API_TIMEOUT)
        page.screenshot(path=ARTIFACTS / "desktop-first-use.png", full_page=True, animations="disabled")

        page.get_by_role("button", name="Semi-arid wheat farm").click()
        expect(page.get_by_label("Soil organic carbon")).to_have_value("0.3")
        page.get_by_role("button", name="Run grounded assessment").click()
        assessment = page.get_by_test_id("assessment")
        expect(assessment).to_be_visible(timeout=API_TIMEOUT)
        expect(page.get_by_text("Use low-density agroforestry as a water-and-carbon intervention")).to_be_visible()
        expect(page.get_by_role("link", name="AR6 WGII Chapter 5: Food, Fibre and Other Ecosystem Products")).to_be_visible()
        expect(assessment.get_by_text("Assessment confidence")).to_be_visible()
        expect(assessment.locator(".recommendation-meta").first).to_contain_text("term")
        expect(assessment.locator(".recommendation-meta").first).to_contain_text("% confidence")
        assert assessment.locator(".impact-list dd").count() > 0, "recommendations must list metric impacts"
        expect(page.get_by_role("heading", name="Field notes before implementation")).to_be_visible()
        assert page.locator(".caveats li").count() > 0, "caveats must be listed"
        page.get_by_text("Inspect the reasoning trace").click()
        assert page.locator(".reasoning-disclosure li").count() >= 4, "reasoning trace must show its stages"
        hrefs = page.locator("a[target=_blank]").evaluate_all("(links) => links.map((a) => a.href)")
        assert hrefs and all(href.startswith("https://") for href in hrefs), f"evidence links: {hrefs}"

        composer_position = page.locator(".composer").evaluate("(el) => getComputedStyle(el).position")
        assert composer_position == "static", "composer must not cover long assessment content"
        assert_no_overflow(page, "desktop")
        page.screenshot(path=ARTIFACTS / "desktop-assessment.png", full_page=True, animations="disabled")
        assert_accessible(page, "desktop assessment")

        focus_states = []
        page.keyboard.press("Home")
        for _ in range(18):
            page.keyboard.press("Tab")
            focus_states.append(
                page.evaluate(
                    """() => {
                      const el = document.activeElement;
                      const style = getComputedStyle(el);
                      return {tag: el.tagName, outline: style.outlineStyle, shadow: style.boxShadow};
                    }"""
                )
            )
        invisible = [state for state in focus_states if state["outline"] == "none" and state["shadow"] == "none"]
        assert not invisible, f"keyboard focus invisible: {invisible}"

        page.set_viewport_size({"width": 390, "height": 844})
        assert_no_overflow(page, "mobile")
        page.screenshot(path=ARTIFACTS / "mobile-assessment.png", full_page=True, animations="disabled")

        # Clarification, then a follow-up turn that continues the same conversation session.
        page.set_viewport_size({"width": 1440, "height": 900})
        page.get_by_role("button", name="New case").click()
        page.get_by_label("Land use").fill("monoculture wheat")
        page.get_by_label("What is changing on this land?").fill("Biodiversity is declining")
        page.get_by_role("button", name="Run grounded assessment").click()
        expect(page.get_by_text("More context needed")).to_be_visible(timeout=API_TIMEOUT)
        assert_accessible(page, "clarification")
        page.get_by_label(re.compile(r"^Soil organic carbon")).fill("0.3")
        page.get_by_label(re.compile(r"^Annual rainfall")).fill("420")
        page.get_by_label(re.compile(r"^Habitat diversity")).fill("2")
        page.get_by_role("button", name="Run grounded assessment").click()
        expect(page.get_by_test_id("assessment")).to_be_visible(timeout=API_TIMEOUT)
        clarification_turn, follow_up_turn = chat_payloads[-2], chat_payloads[-1]
        assert "session_id" not in clarification_turn, "new case must start a fresh session"
        assert follow_up_turn.get("session_id"), "follow-up must continue the clarification session"

        page.set_viewport_size({"width": 390, "height": 844})
        assert_no_overflow(page, "mobile follow-up")
        assert_accessible(page, "mobile follow-up")
        page.screenshot(path=ARTIFACTS / "mobile-follow-up.png", full_page=True, animations="disabled")
        assert not failed_requests, f"failed network requests: {failed_requests}"

        error_page = context.new_page()
        error_page.route("**/api/chat", lambda route: route.fulfill(status=503, body="Unavailable"))
        error_page.goto(URL)
        error_page.wait_for_load_state("networkidle")
        error_page.get_by_role("button", name="Semi-arid wheat farm").click(timeout=API_TIMEOUT)
        error_page.get_by_role("button", name="Run grounded assessment").click()
        expect(error_page.get_by_role("alert")).to_contain_text("Your inputs are still here")
        expect(error_page.get_by_label("Soil organic carbon")).to_have_value("0.3")

        offline_page = context.new_page()
        offline_page.goto(URL)
        offline_page.wait_for_load_state("networkidle")
        offline_page.get_by_role("button", name="Semi-arid wheat farm").click(timeout=API_TIMEOUT)
        offline_page.route("**/api/chat", lambda route: route.abort("connectionrefused"))
        offline_page.get_by_role("button", name="Run grounded assessment").click()
        expect(offline_page.get_by_role("alert")).to_contain_text("could not be reached")
        expect(offline_page.get_by_label("Soil organic carbon")).to_have_value("0.3")

        assert not errors, f"browser console errors: {errors}"
        browser.close()
        print(
            "E2E PASS: happy path, clarification and multi-turn session, evidence links, recovery "
            f"(HTTP 503 and unreachable API), axe, keyboard, desktop and mobile; url={URL}; artifacts={ARTIFACTS}"
        )


if __name__ == "__main__":
    run()

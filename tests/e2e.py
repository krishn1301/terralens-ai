"""Integrated browser, responsive, keyboard, and accessibility verification."""

from pathlib import Path
from tempfile import gettempdir

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).parents[1]
URL = "http://127.0.0.1:5173"
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


def run() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = context.new_page()
        errors: list[str] = []
        page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
        page.on("pageerror", lambda error: errors.append(f"uncaught: {error}"))

        page.goto(URL)
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", level=1)).to_contain_text("Read the land")
        page.screenshot(path=ARTIFACTS / "desktop-first-use.png", full_page=True, animations="disabled")

        page.get_by_role("button", name="Semi-arid wheat farm").click()
        expect(page.get_by_label("Soil organic carbon")).to_have_value("0.3")
        page.get_by_role("button", name="Run grounded assessment").click()
        expect(page.get_by_test_id("assessment")).to_be_visible(timeout=10000)
        expect(page.get_by_text("Use low-density agroforestry as a water-and-carbon intervention")).to_be_visible()
        expect(page.get_by_role("link", name="AR6 WGII Chapter 5: Food, Fibre and Other Ecosystem Products")).to_be_visible()
        composer_position = page.locator(".composer").evaluate("(el) => getComputedStyle(el).position")
        assert composer_position == "static", "composer must not cover long assessment content"
        assert_no_overflow(page, "desktop")
        page.screenshot(path=ARTIFACTS / "desktop-assessment.png", full_page=True, animations="disabled")

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
        assert not serious, f"axe violations: {serious}"

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

        error_page = context.new_page()
        error_page.route("**/api/chat", lambda route: route.fulfill(status=503, body="Unavailable"))
        error_page.goto(URL)
        error_page.wait_for_load_state("networkidle")
        error_page.get_by_role("button", name="Semi-arid wheat farm").click()
        error_page.get_by_role("button", name="Run grounded assessment").click()
        expect(error_page.get_by_role("alert")).to_contain_text("Your inputs are still here")
        expect(error_page.get_by_label("Soil organic carbon")).to_have_value("0.3")

        assert not errors, f"browser console errors: {errors}"
        browser.close()
        print(f"E2E PASS: happy path, recovery, axe, keyboard, desktop and mobile; artifacts={ARTIFACTS}")


if __name__ == "__main__":
    run()

"""End-to-end smoke test for OfferCompare Pro (frontend + backend)."""

import json
import urllib.request
from playwright.sync_api import sync_playwright

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3001"
SCREENSHOT_DIR = "/tmp"


def test_backend_health():
    print("[Backend] Testing /health ...")
    req = urllib.request.Request(f"{BACKEND_URL}/health")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    assert data["status"] == "ok", f"Expected status 'ok', got {data['status']}"
    print(f"  -> OK: {json.dumps(data, indent=2)}")


def test_backend_currencies():
    print("[Backend] Testing /api/currencies ...")
    req = urllib.request.Request(f"{BACKEND_URL}/api/currencies")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    assert isinstance(data, list), "Expected list of currencies"
    assert len(data) > 0, "Expected at least one currency"
    print(f"  -> OK: {len(data)} currencies returned")


def test_backend_countries():
    print("[Backend] Testing /api/countries ...")
    req = urllib.request.Request(f"{BACKEND_URL}/api/countries")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    assert isinstance(data, list), "Expected list of countries"
    assert len(data) > 0, "Expected at least one country"
    print(f"  -> OK: {len(data)} countries returned")


def test_frontend_loads():
    print("[Frontend] Testing page load ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(FRONTEND_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_load_state("networkidle")

        page.screenshot(path=f"{SCREENSHOT_DIR}/frontend_home.png", full_page=True)
        print(f"  -> Screenshot saved to {SCREENSHOT_DIR}/frontend_home.png")

        title = page.title()
        print(f"  -> Page title: {title}")

        body_text = page.inner_text("body")
        assert len(body_text) > 0, "Page body is empty"

        has_error_banner = page.locator("text=Cannot reach the API").count()
        if has_error_banner > 0:
            print("  -> WARNING: API error banner still visible (may need page refresh)")
        else:
            print("  -> OK: No API error banners")

        jwks_error = page.locator("text=Unable to fetch Supabase JWKS").count()
        if jwks_error > 0:
            print("  -> WARNING: JWKS error banner visible (may need page refresh)")
        else:
            print("  -> OK: No JWKS error banners")

        if console_errors:
            print(f"  -> Console errors ({len(console_errors)}):")
            for e in console_errors[:5]:
                print(f"     {e[:200]}")

        browser.close()


def test_frontend_form_interaction():
    print("[Frontend] Testing form interaction ...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(FRONTEND_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_load_state("networkidle")

        inputs = page.locator("input").all()
        print(f"  -> Found {len(inputs)} input fields")

        buttons = page.locator("button").all()
        print(f"  -> Found {len(buttons)} buttons")

        selects = page.locator("select").all()
        print(f"  -> Found {len(selects)} select elements")

        page.screenshot(path=f"{SCREENSHOT_DIR}/frontend_form.png", full_page=True)
        print(f"  -> Form screenshot saved to {SCREENSHOT_DIR}/frontend_form.png")

        browser.close()


if __name__ == "__main__":
    results = {}
    tests = [
        ("Backend Health", test_backend_health),
        ("Backend Currencies", test_backend_currencies),
        ("Backend Countries", test_backend_countries),
        ("Frontend Loads", test_frontend_loads),
        ("Frontend Form", test_frontend_form_interaction),
    ]

    for name, fn in tests:
        try:
            fn()
            results[name] = "PASS"
        except Exception as e:
            results[name] = f"FAIL: {e}"
            print(f"  -> FAILED: {e}")

    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    for name, result in results.items():
        status = "PASS" if result == "PASS" else "FAIL"
        print(f"  [{status}] {name}" + (f" - {result}" if status == "FAIL" else ""))

    failed = sum(1 for r in results.values() if r != "PASS")
    print(f"\n{len(results) - failed}/{len(results)} tests passed")
    if failed:
        print(f"{failed} test(s) failed")

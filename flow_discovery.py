#!/usr/bin/env python3
"""
GOOGLE FLOW API DISCOVERY & INTEGRATION ENGINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Bu script iki şey yapar:
  1. Playwright ile Flow'u açar, tüm ağ trafiğini yakalar → endpoint bulur
  2. Bulunan endpoint'i doğrudan kullanır (Playwright olmadan, hızlı)

Colab T4 GPU üzerinde çalışır.
"""

import json, os, base64, hashlib, time, re, sys

# ── Cookie yükleyici ──────────────────────────────────────────────────────────
COOKIE_RAW = (
    "SID=g.a000BAm6RP8BVfFrLk4KhHa6wFohLt61inBcsFQhfCTSWsHGI93hetB3XHDQh3fowK2ImGXI_"
    "AACgYKAaMSARcSFQHGX2MiRh3zzThOxCifpoBMkiYbPxoVAUF8yKqf672CKx4ob5V1fT88U5gW0076; "
    "HSID=AyYS-WnKWSkNHqfKC; SSID=A8m6nK2VkPbvcXrIG; "
    "APISID=Hpg9qAxDxm2RIJFB/AwxP0WPD2ubRiMYkw; "
    "SAPISID=qWqOVvUN-odagJUT/Ab9hJ841iXvIO2Sr6; "
    "__Secure-1PSID=g.a000BAm6RP8BVfFrLk4KhHa6wFohLt61inBcsFQhfCTSWsHGI93h2sIi_YYnj7"
    "L6u1g1MGWSVAACgYKAf0SARcSFQHGX2MipmcUi6Irq2F4UkeGu0VN7hoVAUF8yKoAomNCtu7RBEHP64RmcoDR0076; "
    "__Secure-3PSID=g.a000BAm6RP8BVfFrLk4KhHa6wFohLt61inBcsFQhfCTSWsHGI93h2mOckS6bBIhcO-"
    "cWooXy6QACgYKAXcSARcSFQHGX2MibNwdyj-bs4pwpMP5Q3KAjRoVAUF8yKohOLjKO_VEnrN6u-AjSjXx0076; "
    "__Secure-1PAPISID=qWqOVvUN-odagJUT/Ab9hJ841iXvIO2Sr6; "
    "__Secure-3PAPISID=qWqOVvUN-odagJUT/Ab9hJ841iXvIO2Sr6; "
    "SIDCC=AKEyXzVfKCTQOsY0_bBZK9mupiLMFAqUi4kPi0iit0LcFL2H-fFKSlslO3cqPoM6uJT-Y4Vb; "
    "NID=533=UNFAkZJbhF1ojRpnFiAaVq-jkE2cpwX-p1jat_WPc1bTNA0HS5ju0hj6kqUAckM_htvUcsD62B2Za3o"
    "K5KnWDnbVg7PBBL5Zc9Dp98t9qIRryG6XH-HGML4_wCRYAe7mE3PR8_c3nP5zT9DbmOmaFu35qV6eHGBoC-AKsZKlW0Ig"
    "Pfqf3m5TpeKjvgf49hAUfI9oLEgfm3aZCKsfefFOdDvTMmtxuMLqKWdW2CfRp7NRl4cG86PYo_AV35_bpmnIG4xDzYV2fz"
    "MzwhOvaIM5x8P9fsvAWaFsusEOZi5HxBS3Xa3kq7AVMGGJ_YMWtpTy7_rp8G0sPx5X_g0VNEkvyJKFqyMXrUZ8mxZUiW-Tuz"
    "dyzgkpK4ymTGt0ySCs2L1dzOEq8PSImydeFO-k27j1_IFq5YwDX-0rPorQG2GO8wmPs9EnHfuP-ggeXOY00YRQT_WVX-HSE9"
    "FPcw8UZxJkMMYk5yc2tVTGOcI0AZ5Y5flc35vSxCVcSr1Sfdsj1EmmuYA1aXQRglIJ-5DqzZrufYvnaR52nQ6SPlXL-RuX0"
    "FAnVsBfa9U_7uECslkaXK8GILZF1skyFwgRjANkuonqiH8Qp-tfYql_ZE7KC251UR46vKwLPAYDmrtzlf1Nl9a5"
)

SAPISID = "qWqOVvUN-odagJUT/Ab9hJ841iXvIO2Sr6"
FLOW_URL = "https://labs.google/fx/tools/flow"
ORIGIN   = "https://labs.google"


def make_sapisidhash(sapisid=SAPISID, origin=ORIGIN):
    ts = int(time.time())
    digest = hashlib.sha1(f"{ts} {sapisid} {origin}".encode()).hexdigest()
    return f"SAPISIDHASH {ts}_{digest}"


def parse_cookies_for_playwright():
    """Convert raw cookie string to Playwright cookie list."""
    cookies = []
    for part in COOKIE_RAW.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        name, _, value = part.partition("=")
        name = name.strip()
        value = value.strip()
        domain = ".google.com" if not name.startswith("__Secure") else ".labs.google" if "PSID" not in name else ".google.com"
        cookies.append({
            "name": name,
            "value": value,
            "domain": ".google.com",
            "path": "/",
            "secure": True,
            "httpOnly": False,
            "sameSite": "None",
        })
    # Also add for labs.google domain
    for part in COOKIE_RAW.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        name, _, value = part.partition("=")
        cookies.append({
            "name": name.strip(),
            "value": value.strip(),
            "domain": ".labs.google",
            "path": "/",
            "secure": True,
            "httpOnly": False,
            "sameSite": "None",
        })
    return cookies


# ── PHASE 1: Playwright Traffic Capture ──────────────────────────────────────

async def run_playwright_capture():
    """
    Open Google Flow with Playwright, intercept ALL network requests,
    try to click Generate, then dump every request to flow_requests.json.
    """
    from playwright.async_api import async_playwright
    import json
    import asyncio

    captured = []

    print("🚀 Playwright başlatılıyor (Async)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1280,900",
            ]
        )

        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        # Inject cookies
        await ctx.add_cookies(parse_cookies_for_playwright())
        print("🍪 Cookie'ler yüklendi")

        page = await ctx.new_page()

        # Intercept ALL requests
        def on_request(request):
            url = request.url
            # Capture anything that looks like an API call
            if any(kw in url for kw in [
                "googleapis.com", "aisandbox", "labs.google/fx/api",
                "generate", "predict", "veo", "imagen", "infer",
                "model", "session", "project",
            ]):
                entry = {
                    "url": url,
                    "method": request.method,
                    "headers": dict(request.headers),
                    "post_data": request.post_data,
                    "resource_type": request.resource_type,
                }
                captured.append(entry)
                print(f"  📡 [{request.method}] {url[:120]}")

        async def on_response(response):
            url = response.url
            if any(kw in url for kw in [
                "googleapis.com", "aisandbox", "labs.google/fx/api",
                "generate", "predict", "veo", "imagen",
            ]):
                try:
                    body = await response.body()
                    # Find matching captured request and add response
                    for entry in reversed(captured):
                        if entry["url"] == url:
                            entry["response_status"] = response.status
                            entry["response_body_preview"] = body[:500].decode(errors="replace")
                            break
                except Exception:
                    pass

        page.on("request", on_request)
        page.on("response", on_response)

        # Navigate to Flow
        print(f"🌐 Flow açılıyor: {FLOW_URL}")
        try:
            await page.goto(FLOW_URL, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"  ⚠️  Yükleme timeout (normal): {e}")

        # Screenshot
        await page.screenshot(path="flow_screenshot_1.png", full_page=False)
        print("📸 Ekran görüntüsü alındı: flow_screenshot_1.png")

        # Get page text to understand UI
        page_text = await page.inner_text("body")
        print("\n📄 Sayfa içeriği (ilk 1000 karakter):")
        print(page_text[:1000])

        # Collect all clickable elements
        buttons = await page.query_selector_all("button")
        inputs  = await page.query_selector_all("input, textarea")
        print(f"\n🔘 Bulunan butonlar: {len(buttons)}")
        print(f"✏️  Bulunan input'lar: {len(inputs)}")

        for i, btn in enumerate(buttons[:20]):
            try:
                txt = (await btn.inner_text()).strip()
                print(f"  Buton {i}: '{txt}'")
            except Exception:
                pass

        # Try to find and fill a prompt field
        prompt_text = "A cinematic dark psychological image, dramatic lighting, 4K"
        filled = False
        for inp in inputs:
            try:
                ph = (await inp.get_attribute("placeholder")) or ""
                label = (await inp.get_attribute("aria-label")) or ""
                if any(kw in (ph + label).lower() for kw in ["prompt", "describe", "write", "type", "enter"]):
                    await inp.click()
                    await inp.fill(prompt_text)
                    filled = True
                    print(f"✅ Prompt alanı dolduruldu: '{ph or label}'")
                    break
            except Exception:
                pass

        if not filled:
            print("⚠️  Prompt alanı bulunamadı, genel textarea deneniyor...")
            try:
                await page.keyboard.type(prompt_text)
            except Exception:
                pass

        # Try clicking Generate button
        generate_keywords = ["generate", "create", "run", "make", "go"]
        for btn in buttons:
            try:
                txt = (await btn.inner_text()).strip().lower()
                if any(kw in txt for kw in generate_keywords):
                    print(f"🖱️  Generate butonu bulundu ve tıklanıyor: '{txt}'")
                    await btn.click()
                    await page.wait_for_timeout(8000)  # Wait for generation
                    break
            except Exception:
                pass

        # Second screenshot after generation attempt
        await page.screenshot(path="flow_screenshot_2.png")
        print("📸 Üretim sonrası ekran görüntüsü: flow_screenshot_2.png")

        # Wait a bit more for async requests
        await page.wait_for_timeout(5000)

        await browser.close()

    # Save all captured requests
    with open("flow_requests.json", "w") as f:
        json.dump(captured, f, indent=2)

    print(f"\n✅ {len(captured)} istek yakalandı → flow_requests.json")
    return captured


# ── PHASE 2: Analyze captured requests ───────────────────────────────────────

def analyze_requests(captured):
    """Find the generation API endpoint from captured requests."""
    print("\n\n==============================")
    print("🔍 İSTEK ANALİZİ")
    print("==============================")

    generation_endpoints = []

    for entry in captured:
        url = entry["url"]
        method = entry["method"]
        pd = entry.get("post_data") or ""
        resp = entry.get("response_body_preview", "")

        # Score this entry — higher = more likely to be the generation API
        score = 0
        if method == "POST": score += 3
        if "generate" in url.lower(): score += 5
        if "veo" in url.lower(): score += 8
        if "imagen" in url.lower(): score += 8
        if "predict" in url.lower(): score += 5
        if "aisandbox" in url: score += 6
        if "googleapis.com" in url: score += 3
        if pd: score += 2
        if len(pd) > 100: score += 3  # Likely has a real payload

        if score >= 3:
            generation_endpoints.append((score, entry))

    generation_endpoints.sort(key=lambda x: -x[0])

    if generation_endpoints:
        print(f"\n🎯 En olası {min(5, len(generation_endpoints))} endpoint:")
        for score, entry in generation_endpoints[:5]:
            print(f"\n  Skor: {score}")
            print(f"  URL:  {entry['url']}")
            print(f"  Method: {entry['method']}")
            if entry.get("post_data"):
                print(f"  Payload (ilk 300): {entry['post_data'][:300]}")
            if entry.get("response_body_preview"):
                print(f"  Response (ilk 200): {entry['response_body_preview'][:200]}")

        # Save best endpoint for integration
        best = generation_endpoints[0][1]
        with open("flow_best_endpoint.json", "w") as f:
            json.dump(best, f, indent=2)
        print(f"\n✅ En iyi endpoint flow_best_endpoint.json'a kaydedildi")
        return best
    else:
        print("❌ Üretim endpoint'i bulunamadı. Manuel inceleme gerekli.")
        print("   flow_requests.json dosyasını inceleyin.")
        return None


# ── PHASE 3: Direct API call (after endpoint is known) ───────────────────────

def call_flow_api_direct(endpoint_info, prompt):
    """
    Call the Flow generation API directly using cookies.
    endpoint_info: dict with 'url', 'method', 'headers', 'post_data'
    """
    import requests as req_lib

    url = endpoint_info["url"]
    method = endpoint_info.get("method", "POST")

    headers = {
        "Cookie": COOKIE_RAW,
        "Authorization": make_sapisidhash(),
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Origin": ORIGIN,
        "Referer": FLOW_URL,
        "Content-Type": "application/json",
        "x-goog-authuser": "0",
    }

    # Inject prompt into the original payload structure
    original_payload = endpoint_info.get("post_data", "{}")
    try:
        payload = json.loads(original_payload)
    except Exception:
        payload = {}

    # Try to find and replace the prompt in the payload
    payload_str = json.dumps(payload)
    # Replace common prompt field names
    for field in ["prompt", "text", "description", "query", "input"]:
        if field in payload_str.lower():
            payload = _replace_prompt_in_dict(payload, prompt)
            break
    else:
        payload["prompt"] = prompt

    print(f"📡 Direkt API çağrısı: {url[:80]}")
    resp = req_lib.request(method, url, headers=headers, json=payload, timeout=120)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.text[:500]}")
    return resp


def _replace_prompt_in_dict(d, new_prompt):
    """Recursively replace prompt values in a dict."""
    if isinstance(d, dict):
        result = {}
        for k, v in d.items():
            if k.lower() in ["prompt", "text", "description"] and isinstance(v, str):
                result[k] = new_prompt
            else:
                result[k] = _replace_prompt_in_dict(v, new_prompt)
        return result
    elif isinstance(d, list):
        return [_replace_prompt_in_dict(item, new_prompt) for item in d]
    return d


# ── MAIN ─────────────────────────────────────────────────────────────────────

async def main():
    print("=" * 60)
    print("🔬 GOOGLE FLOW API DISCOVERY ENGINE")
    print("=" * 60)

    # Phase 1: Capture
    captured = await run_playwright_capture()

    # Show screenshots
    try:
        from IPython.display import display, Image as IPImage
        print("\n📸 Ekran görüntüleri:")
        for f in ["flow_screenshot_1.png", "flow_screenshot_2.png"]:
            if os.path.exists(f):
                display(IPImage(f))
    except Exception:
        pass

    # Phase 2: Analyze
    best = analyze_requests(captured)

    if best:
        print("\n" + "=" * 60)
        print("✅ ENDPOINT BULUNDU! Direkt kullanıma hazır.")
        print("   Bir sonraki adım: Bu endpoint'i engine.py'ye entegre etmek.")
        print("=" * 60)
    else:
        print("\n⚠️  Otomatik yakalama başarısız.")
        print("   flow_requests.json dosyasını manuel inceleyin.")
        print("   Network sekmesinden manuel yakalamayı deneyin.")

    return best

import asyncio
try:
    loop = asyncio.get_running_loop()
    # In Colab/Jupyter, we must use create_task or await directly, but since this is inside a cell:
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
except RuntimeError:
    asyncio.run(main())

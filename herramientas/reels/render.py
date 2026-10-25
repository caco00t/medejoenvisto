import sys, os
from playwright.sync_api import sync_playwright
html = os.path.abspath(sys.argv[1]); out = sys.argv[2]; mode = sys.argv[3]
os.makedirs(out, exist_ok=True)
FPS = 30
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + html); pg.wait_for_timeout(700)
    if mode == "keys":
        for t in [float(x) for x in sys.argv[4].split(",")]:
            pg.evaluate(f"render({t})"); pg.screenshot(path=f"{out}/k_{t:05.2f}.png")
    else:
        n = int(float(sys.argv[4]) * FPS)
        for i in range(n):
            pg.evaluate(f"render({i / FPS})")
            pg.screenshot(path=f"{out}/f_{i:04d}.jpg", type="jpeg", quality=92)
    b.close()

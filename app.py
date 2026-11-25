# A.R.T./New York "Drive for 55" email countdown GIF (Vercel Python function).
# Serves the GIF at any path, e.g. https://<project>.vercel.app/api/countdown
import io
import os
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

# End of Monday Nov 30, 2026 in New York = 12:00am Tue Dec 1 EST = 05:00 UTC.
DEADLINE = datetime(2026, 12, 1, 5, 0, 0, tzinfo=timezone.utc)

RED, MINT, WHITE = (237, 0, 56), (118, 228, 203), (255, 255, 255)
W, H, FRAMES = 600, 170, 60
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(ROOT, "fonts", "Montserrat.ttf")


def _font(size, weight=900):
    try:
        f = ImageFont.truetype(FONT_PATH, size)
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
        return f
    except Exception:
        return ImageFont.load_default(size)


NUM_FONT, LABEL_FONT = _font(84), _font(15, 800)
COLON_FONT, DONE_FONT = _font(60), _font(40)
LABELS = ["HOURS", "MINUTES", "SECONDS"]
COL_W = W // 3


def _frame(left):
    img = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(img)
    if left <= 0:
        d.text((W / 2, H / 2), "THANK YOU!", font=DONE_FONT, fill=WHITE, anchor="mm")
        return img
    hours, rem = divmod(left, 3600)
    mins, secs = divmod(rem, 60)
    for i, (v, label) in enumerate(zip([hours, mins, secs], LABELS)):
        cx = COL_W * i + COL_W / 2
        d.text((cx, 74), f"{v:02d}", font=NUM_FONT, fill=WHITE, anchor="mm")
        d.text((cx, 132), label, font=LABEL_FONT, fill=MINT, anchor="mm")
        if i < 2:
            d.text((COL_W * (i + 1), 68), ":", font=COLON_FONT, fill=MINT, anchor="mm")
    return img


def render(now=None):
    now = now or datetime.now(timezone.utc)
    start = int((DEADLINE - now).total_seconds())
    frames = [_frame(max(start - i, 0)) for i in range(FRAMES if start > 0 else 1)]
    p0 = frames[0].quantize(colors=32)
    pal = [p0] + [f.quantize(palette=p0, dither=Image.Dither.NONE) for f in frames[1:]]
    buf = io.BytesIO()
    pal[0].save(buf, format="GIF", save_all=True, append_images=pal[1:],
                duration=1000, optimize=True, disposal=1)
    return buf.getvalue()


def app(environ, start_response):
    """WSGI entrypoint that Vercel detects automatically."""
    body = render()
    start_response("200 OK", [
        ("Content-Type", "image/gif"),
        ("Content-Length", str(len(body))),
        ("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"),
        ("Pragma", "no-cache"),
        ("Expires", "0"),
    ])
    return [body]

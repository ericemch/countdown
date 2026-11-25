"""A.R.T./New York "Drive for 55" email countdown GIF.

Renders a 60-frame animated GIF (one frame per second) counting down from
the moment it is requested to the deadline. Each time an email is opened,
the email client requests the image, so the server renders a fresh GIF
starting from that moment.
"""
import io
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

# ---- Settings ---------------------------------------------------------------
# End of Monday, Nov 30, 2026 (midnight going into Tuesday, Dec 1), New York time.
DEADLINE = datetime(2026, 12, 1, 0, 0, 0, tzinfo=ZoneInfo("America/New_York"))

RED = (237, 0, 56)       # #ED0038, sampled from the Drive for 55 banner
MINT = (118, 228, 203)   # #76E4CB
WHITE = (255, 255, 255)

W, H = 600, 170          # standard email width
FRAMES = 60              # one minute of animation, then it holds
FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "Montserrat.ttf")
# -----------------------------------------------------------------------------


def _font(size, weight=900):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_axes([weight])  # Montserrat variable font -> Black
    except Exception:
        pass
    return f


NUM_FONT = _font(84, 900)
LABEL_FONT = _font(15, 800)
COLON_FONT = _font(60, 900)
DONE_FONT = _font(40, 900)

LABELS = ["HOURS", "MINUTES", "SECONDS"]
COL_W = W // 3


def _frame(seconds_left):
    img = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H - 8, W, H], fill=MINT)  # mint rule, like the banner

    if seconds_left <= 0:
        d.text((W / 2, (H - 8) / 2), "THANK YOU!", font=DONE_FONT, fill=WHITE, anchor="mm")
        return img

    hours, rem = divmod(seconds_left, 3600)   # total hours, no days column
    mins, secs = divmod(rem, 60)
    values = [hours, mins, secs]

    num_y, label_y = 70, 128
    for i, (v, label) in enumerate(zip(values, LABELS)):
        cx = COL_W * i + COL_W / 2
        d.text((cx, num_y), f"{v:02d}", font=NUM_FONT, fill=WHITE, anchor="mm")
        d.text((cx, label_y), label, font=LABEL_FONT, fill=MINT, anchor="mm")
        if i < 2:
            d.text((COL_W * (i + 1), num_y - 6), ":", font=COLON_FONT, fill=MINT, anchor="mm")
    return img


def render(now=None):
    now = now or datetime.now(timezone.utc)
    start = int((DEADLINE - now).total_seconds())
    frames = [_frame(max(start - i, 0)) for i in range(FRAMES if start > 0 else 1)]
    # Shared 3-colour-ish palette keeps the file small and colours exact.
    p0 = frames[0].quantize(colors=32, method=Image.Quantize.MEDIANCUT)
    pal = [p0] + [f.quantize(palette=p0, dither=Image.Dither.NONE) for f in frames[1:]]
    buf = io.BytesIO()
    pal[0].save(buf, format="GIF", save_all=True, append_images=pal[1:],
                duration=1000, optimize=True, disposal=1)
    return buf.getvalue()


if __name__ == "__main__":
    with open("drive55_countdown_preview.gif", "wb") as fh:
        fh.write(render())
    print("wrote drive55_countdown_preview.gif")

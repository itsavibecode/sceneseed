"""
SceneSeed — generate og-image.png (1200×630) and apple-touch-icon.png (180×180)
from the brand's line-art logo + wordmark.

  Usage:    python .scripts/build-og-image.py
  Requires: Pillow (`pip install Pillow`)

The line-art leaf is rendered by sampling points along the same quadratic
Bezier curves the SVG uses, so the PNG output stays in sync with favicon.svg
without needing a real SVG renderer.
"""
from PIL import Image, ImageDraw, ImageFont
import os
import sys

# ─── Brand palette ───────────────────────────────────────────────────
INK    = (15,  23,  42)   # #0f172a — primary
ACCENT = (101, 163, 13)   # #65a30d — accent green
MUTED  = (71,  85,  105)  # #475569 — body muted
FAINT  = (148, 163, 184)  # #94a3b8 — footer

# ─── Helpers ─────────────────────────────────────────────────────────

def find_font(candidates, size):
    """Try a list of font filenames; return the first one that loads."""
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    print(f"warning: none of {candidates} found, using PIL default")
    return ImageFont.load_default()

def quadratic_bezier(p0, p1, p2, steps=32):
    """Sample (steps+1) points along a quadratic Bezier curve."""
    out = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0]
        y = u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]
        out.append((x, y))
    return out

def transform(pts, scale, ox, oy):
    return [(scale * x + ox, scale * y + oy) for (x, y) in pts]

def draw_leaf_logo(draw, cx, cy, scale, color, line_width):
    """
    Replicates the SVG paths used everywhere else in the site:
      Leaf:  M 25 55 Q 35 30 60 25 Q 82 23 90 38 Q 88 56 70 60 Q 45 64 25 55 Z
      Stem:  M 25 55 Q 15 70 7 88
      Dots:  (50, 46) (62, 44) (74, 42) at r=5
    SVG viewBox is approximately 0–100 × 0–95.
    """
    # Center the visual bbox (which biases left+down because of the stem)
    # over the requested center point.
    bbox_w = 95 * scale
    bbox_h = 90 * scale
    # The leaf body itself sits roughly cols 25-90, rows 22-65 in the SVG.
    # Centre that, then let the stem extend below-left as a trailing flourish.
    leaf_cx = (25 + 90) / 2  # 57.5
    leaf_cy = (22 + 65) / 2  # 43.5
    ox = cx - leaf_cx * scale
    oy = cy - leaf_cy * scale

    # Leaf body — closed outline (no fill)
    leaf_pts = []
    leaf_pts += quadratic_bezier((25, 55), (35, 30), (60, 25))
    leaf_pts += quadratic_bezier((60, 25), (82, 23), (90, 38))
    leaf_pts += quadratic_bezier((90, 38), (88, 56), (70, 60))
    leaf_pts += quadratic_bezier((70, 60), (45, 64), (25, 55))
    leaf_pts = transform(leaf_pts, scale, ox, oy)
    draw.line(leaf_pts + [leaf_pts[0]], fill=color, width=line_width, joint='curve')

    # Stem-tail
    stem_pts = quadratic_bezier((25, 55), (15, 70), (7, 88))
    stem_pts = transform(stem_pts, scale, ox, oy)
    draw.line(stem_pts, fill=color, width=line_width, joint='curve')

    # Three dots
    for (px, py) in [(50, 46), (62, 44), (74, 42)]:
        x = scale * px + ox
        y = scale * py + oy
        r = 5 * scale
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

# ─── og-image (1200×630) ─────────────────────────────────────────────

def build_og_image(out_path):
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)

    # Fonts — try a few system possibilities so this runs on any platform
    title_font = find_font([
        'georgiab.ttf', 'Georgiab.ttf', 'Georgia Bold.ttf', 'georgia.ttf', 'Georgia.ttf',
        '/Library/Fonts/Georgia.ttf', '/System/Library/Fonts/Georgia.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
    ], 112)
    sub_font = find_font([
        'segoeui.ttf', 'SegoeUI.ttf', 'arial.ttf', 'Arial.ttf', 'Arial Unicode.ttf',
        '/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/Helvetica.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    ], 32)
    url_font = find_font([
        'segoeui.ttf', 'SegoeUI.ttf', 'arial.ttf', 'Arial.ttf',
        '/Library/Fonts/Helvetica.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    ], 22)

    # Logo on the left
    draw_leaf_logo(d, cx=240, cy=H/2, scale=2.8, color=INK, line_width=10)

    # Wordmark + subtitle on the right
    title = "SceneSeed"
    sub = "Audience suggestions for live improv shows."
    title_x = 450
    right_margin = 60

    title_box = d.textbbox((0, 0), title, font=title_font)
    sub_box = d.textbbox((0, 0), sub, font=sub_font)
    title_w = title_box[2] - title_box[0]
    sub_w = sub_box[2] - sub_box[0]

    # Defensive guard: if title_w exceeds available width, shrink the font.
    avail = W - title_x - right_margin
    if title_w > avail:
        ratio = avail / title_w * 0.98
        title_font = ImageFont.truetype(title_font.path, int(title_font.size * ratio))
        title_box = d.textbbox((0, 0), title, font=title_font)
        title_w = title_box[2] - title_box[0]

    title_h = title_box[3] - title_box[1]
    total_h = title_h + 24 + (sub_box[3] - sub_box[1])
    title_y = (H - total_h) / 2 - 28
    d.text((title_x, title_y), title, fill=INK, font=title_font)
    d.text((title_x, title_y + title_h + 24), sub, fill=MUTED, font=sub_font)

    # Footer URL bottom-left
    url = "itsavibecode.github.io/sceneseed"
    d.text((120, H - 60), url, fill=FAINT, font=url_font)

    img.save(out_path, 'PNG', optimize=True)
    print(f"wrote {out_path}  ({W}×{H})")

# ─── Square icon (any size; used for apple-touch-icon and PWA icons) ─

def build_square_icon(out_path, size, line_width=None):
    img = Image.new('RGB', (size, size), 'white')
    d = ImageDraw.Draw(img)
    # Scale the logo to fill ~80% of the canvas
    scale = (size / 100) * 0.8
    lw = line_width if line_width is not None else max(4, int(scale * 3))
    draw_leaf_logo(d, cx=size / 2, cy=size / 2, scale=scale, color=INK, line_width=lw)
    img.save(out_path, 'PNG', optimize=True)
    print(f"wrote {out_path}  ({size}×{size})")

# ─── Entry point ─────────────────────────────────────────────────────

if __name__ == '__main__':
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_og_image(os.path.join(here, 'og-image.png'))
    build_square_icon(os.path.join(here, 'apple-touch-icon.png'), 180)
    build_square_icon(os.path.join(here, 'icon-192.png'), 192)
    build_square_icon(os.path.join(here, 'icon-512.png'), 512)
    build_square_icon(os.path.join(here, 'icon-maskable-512.png'), 512, line_width=18)

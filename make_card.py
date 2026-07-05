#!/usr/bin/env python3
"""
LinkedIn code-card generator — Swift / iOS branded.
Renders at 2x and downscales for crisp output (final: 1200x1200).
Reusable: change TIP_NO, HEADLINE, FILENAME and CODE for each post.
"""
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------- content ----------------
TIP_NO   = "SWIFTUI TIP  ·  001"
HEADLINE = "Animate numbers\nwith one modifier"
FILENAME = "PriceView.swift"
CODE = '''// One modifier. Buttery-smooth digits.

struct PriceView: View {
    @State private var price = 99

    var body: some View {
        Text("$\\(price)")
            .font(.system(size: 48, weight: .bold))
            .contentTransition(.numericText())
            .onTapGesture {
                withAnimation(.snappy) { price = 149 }
            }
    }
}'''
AUTHOR  = "Erkin Azizi"
ROLE    = "iOS Developer"
HANDLE  = "linkedin.com/in/erkinazizi"

# ---------------- palette ----------------
S = 2  # supersampling factor
W = H = 1200 * S

BG_TOP    = (13, 14, 20)      # near-black indigo
BG_BOT    = (24, 25, 34)
ORANGE    = (240, 81, 56)     # Swift orange #F05138
ORANGE_HI = (255, 122, 89)
CARD_BG   = (30, 31, 39)      # code window
CARD_HDR  = (38, 39, 49)
STROKE    = (55, 57, 70)
WHITE     = (245, 246, 250)
MUTED     = (140, 145, 160)

# Xcode "Default (Dark)" token colors
C_PLAIN   = (255, 255, 255)
C_KEYWORD = (252, 95, 163)    # pink
C_TYPE    = (93, 216, 255)    # cyan
C_STRING  = (252, 106, 93)    # coral
C_NUMBER  = (208, 191, 105)   # yellow
C_COMMENT = (108, 121, 134)   # gray
C_ATTR    = (253, 143, 63)    # orange (@State etc.)
C_CALL    = (103, 183, 164)   # teal (methods / modifiers)

import os
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
def mono(size, weight="Regular"):
    return ImageFont.truetype(f"{FONT_DIR}/JetBrainsMono-{weight}.ttf", size)
def inter(size, wght=400):
    f = ImageFont.truetype(f"{FONT_DIR}/Inter-Regular.ttf", size)
    try:
        f.set_variation_by_axes([28, wght])  # opsz, wght
    except Exception:
        pass
    return f

# ---------------- tokenizer ----------------
KEYWORDS = {"struct","var","let","private","func","return","some","in","if","else"}
TYPES    = {"View","Text","State","Int","String"}

TOKEN_RE = re.compile(r'''
    (?P<comment>//.*$)
  | (?P<string>"(?:\\.|[^"\\])*")
  | (?P<attr>@\w+)
  | (?P<number>\b\d+(?:\.\d+)?\b)
  | (?P<call>\.\w+)
  | (?P<word>\b\w+\b)
  | (?P<other>.)
''', re.VERBOSE)

def tokenize(line):
    out = []
    for m in TOKEN_RE.finditer(line):
        kind, text = m.lastgroup, m.group()
        if kind == "comment": out.append((text, C_COMMENT))
        elif kind == "string": out.append((text, C_STRING))
        elif kind == "attr":   out.append((text, C_ATTR))
        elif kind == "number": out.append((text, C_NUMBER))
        elif kind == "call":
            out.append((".", C_PLAIN)); out.append((text[1:], C_CALL))
        elif kind == "word":
            if text in KEYWORDS:  out.append((text, C_KEYWORD))
            elif text in TYPES:   out.append((text, C_TYPE))
            else:                 out.append((text, C_PLAIN))
        else: out.append((text, C_PLAIN))
    return out

# ---------------- canvas ----------------
img = Image.new("RGB", (W, H), BG_TOP)
dr  = ImageDraw.Draw(img)

# vertical gradient
for y in range(H):
    t = y / H
    dr.line([(0, y), (W, y)], fill=tuple(
        int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOT)))

# soft orange glow, bottom-right
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([W*0.55, H*0.62, W*1.35, H*1.42], fill=(60, 18, 10))
gd.ellipse([-W*0.35, -H*0.40, W*0.35, H*0.30], fill=(16, 20, 34))
glow = glow.filter(ImageFilter.GaussianBlur(220*S/2))
img  = Image.blend(img, Image.composite(glow, img, Image.new("L",(W,H),255)), 0.0)
img  = Image.frombytes("RGB", (W,H), bytes(
    min(255, a + b) for a, b in zip(img.tobytes(), glow.tobytes())))
dr = ImageDraw.Draw(img)

# faint dot grid (craft detail)
for gx in range(0, W, 48*S):
    for gy in range(0, H, 48*S):
        dr.ellipse([gx, gy, gx+2*S, gy+2*S], fill=(255,255,255,8) if False else (34,36,46))

M = 84 * S  # outer margin

# ---- top row: badge + handle ----
badge_f = mono(17*S, "Medium")
bt = TIP_NO
bw = dr.textlength(bt, font=badge_f)
bx, by = M, M
pad_x, pad_y = 20*S, 11*S
dr.rounded_rectangle([bx, by, bx+bw+2*pad_x, by+17*S+2*pad_y],
                     radius=999, outline=ORANGE, width=2*S)
dr.text((bx+pad_x, by+pad_y), bt, font=badge_f, fill=ORANGE_HI)

hf = mono(17*S, "Regular")
hw = dr.textlength(HANDLE, font=hf)
dr.text((W - M - hw, by + pad_y), HANDLE, font=hf, fill=MUTED)

# ---- headline ----
head_f = inter(68*S, 750)
hy = by + 100*S
for i, line in enumerate(HEADLINE.split("\n")):
    dr.text((M, hy + i*80*S), line, font=head_f, fill=WHITE)

# ---- code window ----
cw_x0, cw_y0 = M, hy + 205*S
cw_x1, cw_y1 = W - M, H - 190*S
r = 22*S

# shadow
sh = Image.new("RGBA", (W, H), (0,0,0,0))
sd = ImageDraw.Draw(sh)
sd.rounded_rectangle([cw_x0, cw_y0+14*S, cw_x1, cw_y1+14*S], radius=r, fill=(0,0,0,150))
sh = sh.filter(ImageFilter.GaussianBlur(30*S))
img.paste(Image.new("RGB",(W,H),(0,0,0)), (0,0), sh)
dr = ImageDraw.Draw(img)

dr.rounded_rectangle([cw_x0, cw_y0, cw_x1, cw_y1], radius=r,
                     fill=CARD_BG, outline=STROKE, width=2*S)
# header bar
hdr_h = 64*S
dr.rounded_rectangle([cw_x0, cw_y0, cw_x1, cw_y0+hdr_h+r], radius=r, fill=CARD_HDR)
dr.rectangle([cw_x0, cw_y0+hdr_h, cw_x1, cw_y0+hdr_h+r], fill=CARD_BG)
dr.line([(cw_x0, cw_y0+hdr_h), (cw_x1, cw_y0+hdr_h)], fill=STROKE, width=2*S)

# traffic lights
for i, c in enumerate([(255,95,86), (255,189,46), (39,201,63)]):
    cx = cw_x0 + 30*S + i*34*S
    cy = cw_y0 + hdr_h//2
    dr.ellipse([cx-8*S, cy-8*S, cx+8*S, cy+8*S], fill=c)

# filename centered in header
fn_f = mono(17*S, "Regular")
fw = dr.textlength(FILENAME, font=fn_f)
dr.text(((cw_x0+cw_x1)//2 - fw//2, cw_y0 + hdr_h//2 - 10*S),
        FILENAME, font=fn_f, fill=MUTED)

# code text
code_f  = mono(21*S, "Regular")
line_h  = 34 * S
tx, ty  = cw_x0 + 44*S, cw_y0 + hdr_h + 30*S
ln_f    = mono(17*S, "Regular")
for i, line in enumerate(CODE.split("\n")):
    y = ty + i * line_h
    # line number
    dr.text((cw_x0 + 20*S, y + 4*S), f"{i+1:>2}", font=ln_f, fill=(80, 84, 98))
    x = tx + 20*S
    for text, color in tokenize(line):
        dr.text((x, y), text, font=code_f, fill=color)
        x += dr.textlength(text, font=code_f)

# ---- footer ----
fy = H - 140*S
dr.line([(M, fy - 6*S), (M + 56*S, fy - 6*S)], fill=ORANGE, width=5*S)
name_f = inter(31*S, 650)
role_f = inter(22*S, 420)
dr.text((M, fy + 14*S), AUTHOR, font=name_f, fill=WHITE)
dr.text((M, fy + 60*S), ROLE + "  ·  Swift & SwiftUI", font=role_f, fill=MUTED)

# swift-bird-inspired swoosh mark, bottom right (original, minimal)
sx, sy = W - M - 60*S, fy + 40*S
dr.arc([sx-46*S, sy-46*S, sx+46*S, sy+46*S], start=300, end=140, fill=ORANGE, width=9*S)
dr.ellipse([sx+24*S, sy-38*S, sx+40*S, sy-22*S], fill=ORANGE)

# ---------------- export ----------------
img = img.resize((1200, 1200), Image.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card.png")
img.save(out, "PNG")
print("saved", out)

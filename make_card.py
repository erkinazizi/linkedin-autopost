#!/usr/bin/env python3
"""
LinkedIn code-card generator — Swift / iOS branded.
Renders at 2x and downscales for crisp output (final: 1200x1200).
Reusable: change TIP_NO, HEADLINE, FILENAME and CODE for each post.
"""
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------- content ----------------
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

BG_TOP    = (209, 223, 230)   # powder blue — matches reference image
BG_BOT    = (225, 232, 238)
ORANGE    = (0, 122, 255)
ORANGE_HI = (0, 145, 255)
CARD_BG   = (255, 255, 255)
CARD_HDR  = (242, 244, 247)
STROKE    = (210, 215, 220)
INK       = (18,  18,  18)    # near-black for headlines & footer
MUTED     = (130, 142, 155)   # subtle labels

# Xcode "Default (Light)" inspired token colors
C_PLAIN   = (30, 30, 30)
C_KEYWORD = (180, 0, 150)
C_TYPE    = (40, 130, 140)
C_STRING  = (200, 30, 30)
C_NUMBER  = (30, 30, 200)
C_COMMENT = (100, 110, 120)
C_ATTR    = (150, 80, 0)
C_CALL    = (60, 110, 180)

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

M = 84 * S  # outer margin

# ---- centered vertical layout ----
# Calculate total content height first, then derive all Y positions.
_head_lines = HEADLINE.split("\n")
_n           = len(_head_lines)
HEAD_H  = (_n - 1) * 80*S + 68*S   # headline block height (line-spacing + last font height)
GAP_HC  = 60*S                      # headline → code window gap
CODE_H  = 600*S                     # fixed code window height
GAP_CF  = 55*S                      # code window → footer gap
FOOT_H  = 100*S                     # footer block height (separator + name + role)
TOTAL_H = HEAD_H + GAP_HC + CODE_H + GAP_CF + FOOT_H
hy      = (H - TOTAL_H) // 2        # vertically centered start

# ---- headline (centered) ----
head_f = inter(68*S, 750)
for i, line in enumerate(_head_lines):
    lw = dr.textlength(line, font=head_f)
    dr.text(((W - lw) // 2, hy + i*80*S), line, font=head_f, fill=INK)

# ---- code window ----
cw_x0 = M
cw_y0 = hy + HEAD_H + GAP_HC
cw_x1 = W - M
cw_y1 = cw_y0 + CODE_H
r = 22*S

# shadow
sh = Image.new("RGBA", (W, H), (0,0,0,0))
sd = ImageDraw.Draw(sh)
sd.rounded_rectangle([cw_x0, cw_y0+14*S, cw_x1, cw_y1+14*S], radius=r, fill=(0,0,0,20))
sh = sh.filter(ImageFilter.GaussianBlur(30*S))
img.paste(Image.new("RGB",(W,H),BG_TOP), (0,0), sh)
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
    dr.text((cw_x0 + 20*S, y + 4*S), f"{i+1:>2}", font=ln_f, fill=(180, 180, 180))
    x = tx + 20*S
    for text, color in tokenize(line):
        dr.text((x, y), text, font=code_f, fill=color)
        x += dr.textlength(text, font=code_f)

# ---- footer (centered, relative to code window) ----
fy = cw_y1 + GAP_CF
name_f = inter(31*S, 650)
role_f = inter(22*S, 420)
nw = dr.textlength(AUTHOR, font=name_f)
role_str = ROLE + "  ·  Swift & SwiftUI"
rw = dr.textlength(role_str, font=role_f)
# thin separator line centered
line_len = 48*S
dr.line([(W//2 - line_len//2, fy - 6*S), (W//2 + line_len//2, fy - 6*S)], fill=INK, width=4*S)
dr.text(((W - nw) // 2, fy + 14*S), AUTHOR, font=name_f, fill=INK)
dr.text(((W - rw) // 2, fy + 60*S), role_str, font=role_f, fill=MUTED)


# ---------------- export ----------------
img = img.resize((1200, 1200), Image.LANCZOS)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "card.png")
img.save(out, "PNG")
print("saved", out)

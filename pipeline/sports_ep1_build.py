#!/usr/bin/env python3
"""Sports Trivia Ep. 1 — long-form video builder
30 questions across 8 sport categories, ~10 min
"""
import sys, os, math, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from da_lib import W, H, FPS, SR, fb, fc, band, brand, center, block, fit, wrap
from da_lib import tick, ding, correct, whoosh, pop, music
from piper_voice import say as piper_say
from sports_ep1_content import CATEGORIES

DIR = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/claude/Composiouploads/sports_ep1.mp4"

TIMER = 3  # seconds to answer
INTRO_DUR = 4.0
CAT_DUR = 3.5
OUTRO_DUR = 4.0

# ─── Scene helpers ────────────────────────────────────────────────────────────

def r_intro(t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")
    band(d, 0, 0, W, H, (10, 14, 40), (26, 32, 80))
    brand(d)
    # Big trophy icon area
    d.ellipse([W//2-180, 340, W//2+180, 700], fill=(255, 200, 0, 40))
    center(d, "🏆", W//2, 370, fb(180), (255, 220, 60))
    center(d, "SPORTS TRIVIA", W//2, 650, fc(96), (255, 220, 60), sw=4)
    center(d, "30 Questions", W//2, 790, fc(72), (255, 255, 255), sw=3)
    # Sport emojis
    emojis = ["⚽", "🏀", "🎾", "🏊", "⚾", "🥊", "🏃", "🏆"]
    xs = [W//2 - 320 + i*90 for i in range(8)]
    for i, (em, x) in enumerate(zip(emojis, xs)):
        center(d, em, x, 950, fb(54), (255, 255, 255))
    center(d, "How many can YOU get right?", W//2, 1080, fc(54), (200, 200, 255), sw=3)
    center(d, "You have 3 seconds per question!", W//2, 1180, fc(46), (180, 180, 220), sw=2)
    return img

def r_category(cat, t, dur):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")
    ct, cb = cat["color_top"], cat["color_bot"]
    band(d, 0, 0, W, H, ct, cb)
    brand(d)
    slide = min(1.0, t / 0.4)
    alpha = int(255 * slide)
    oy = int((1 - slide) * 60)
    center(d, cat["emoji"], W//2, 560 + oy, fb(240), (255, 255, 255, alpha))
    center(d, cat["name"].upper(), W//2, 880 + oy, fc(130), (255, 255, 255, alpha), sw=5)
    nq = len(cat["questions"])
    center(d, f"{nq} Questions", W//2, 1050 + oy, fc(64), (255, 255, 200, alpha), sw=3)
    return img

def r_question(qdata, t):
    """Render one question frame. qdata has: q, opts, ci, color_top, color_bot,
       q_start, think, reveal, end, q_num, total_q"""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")
    ct, cb = qdata["color_top"], qdata["color_bot"]
    rev = t >= qdata["reveal"]
    # Darken on reveal for contrast
    if rev:
        dark = tuple(max(0, c - 30) for c in ct)
        darkb = tuple(max(0, c - 30) for c in cb)
        band(d, 0, 0, W, H, dark, darkb)
    else:
        band(d, 0, 0, W, H, ct, cb)
    brand(d)

    # Q number badge
    q_num = qdata["q_num"]
    total_q = qdata["total_q"]
    d.rounded_rectangle([W//2 - 110, 130, W//2 + 110, 208], 38, fill=(0, 0, 0, 140))
    center(d, f"Q{q_num} / {total_q}", W//2, 142, fc(50), (255, 220, 60))

    # Category emoji small
    center(d, qdata["emoji"], W - 80, 150, fb(50), (255, 255, 255, 180))

    # Question text
    f_q = fit(d, qdata["q"], W - 140, 74)
    block(d, qdata["q"], W//2, 460, f_q, (255, 255, 255), sw=4)

    # Answer options
    oy = 760; ow = W - 160; ox = 80
    for k, opt in enumerate(qdata["opts"]):
        yy = oy + k * 168
        if rev and k == qdata["ci"]:
            fill_c = (60, 220, 130)
        elif rev:
            fill_c = (255, 255, 255, 14)
        else:
            fill_c = (255, 255, 255, 28)
        d.rounded_rectangle([ox, yy, ox + ow, yy + 148], 24, fill=fill_c)
        d.ellipse([ox + 24, yy + 32, ox + 100, yy + 116], fill=(255, 220, 60))
        center(d, chr(65 + k), ox + 62, yy + 48, fc(60), (30, 20, 10))
        tc = (20, 40, 28) if (rev and k == qdata["ci"]) else (255, 255, 255)
        sw_val = 0 if (rev and k == qdata["ci"]) else 4
        f_opt = fit(d, opt, ow - 200, 64)
        d.text((ox + 140, yy + 38), opt, font=f_opt, fill=tc,
               stroke_width=sw_val, stroke_fill=(0, 0, 0))

    # Timer circle
    cx, cy, r = W//2, 1600, 80
    if not rev and t >= qdata["think"]:
        fr = (t - qdata["think"]) / TIMER
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255))
        d.arc([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
              -90, -90 + 360 * (1 - fr), fill=(230, 120, 60), width=13)
        secs_left = max(1, int(math.ceil(TIMER - (t - qdata["think"]))))
        center(d, str(secs_left), cx, cy - 44, fc(80), (30, 30, 40))
    elif not rev:
        center(d, "?", cx, cy - 50, fc(90), (255, 255, 255), sw=4)

    return img

def r_outro(t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")
    band(d, 0, 0, W, H, (10, 14, 40), (26, 32, 80))
    brand(d)
    center(d, "🏆", W//2, 400, fb(160), (255, 220, 60))
    center(d, "THAT'S ALL 30!", W//2, 690, fc(100), (255, 220, 60), sw=4)
    center(d, "How many did you get?", W//2, 840, fc(64), (255, 255, 255), sw=3)
    center(d, "Comment your score below 👇", W//2, 960, fc(54), (200, 200, 255), sw=3)
    center(d, "🔔 Subscribe for more trivia!", W//2, 1100, fc(58), (255, 220, 60), sw=3)
    return img

# ─── Scene scheduler ──────────────────────────────────────────────────────────

class Scene:
    def __init__(self, dur, render_fn, voice_events=None, sfx_events=None):
        self.dur = dur
        self.render_fn = render_fn     # fn(local_t) → PIL Image
        self.voice_events = voice_events or []   # [(audio, local_t), ...]
        self.sfx_events = sfx_events or []

def build_question_scene(qdata):
    """Build one question scene with audio."""
    va_q = piper_say(qdata["q"])
    q_start = 0.5
    think = q_start + len(va_q) / SR + 0.35
    reveal = think + TIMER
    va_ans = piper_say(f"The answer is {qdata['opts'][qdata['ci']]}.")
    end = reveal + max(len(va_ans) / SR + 0.6, 3.5)

    qdata["q_start"] = q_start
    qdata["think"] = think
    qdata["reveal"] = reveal
    qdata["end"] = end

    ve = [(va_q, q_start), (va_ans, reveal + 0.2)]
    se = [(pop(), 0.2)]
    for k in range(3):
        se.append((tick(), think + k))
    se.append((correct(), reveal))

    return Scene(end, lambda t, q=qdata: r_question(q, t), ve, se), end

def build_all_scenes():
    scenes = []
    q_num = 1
    total_q = sum(len(cat["questions"]) for cat in CATEGORIES)

    # Intro
    va_intro = piper_say(
        "Welcome to Sports Trivia! 30 questions across 8 sports. "
        "You have 3 seconds per question. Let's go!"
    )
    scenes.append(Scene(
        INTRO_DUR,
        r_intro,
        voice_events=[(va_intro, 0.4)],
        sfx_events=[(whoosh(), 0.2), (ding(), 3.5)]
    ))

    # Categories
    for cat in CATEGORIES:
        # Category title card
        va_cat = piper_say(f"{cat['name']}!")
        cat_scene = Scene(
            CAT_DUR,
            lambda t, c=cat: r_category(c, t, CAT_DUR),
            voice_events=[(va_cat, 0.5)],
            sfx_events=[(whoosh(), 0.1)]
        )
        scenes.append(cat_scene)

        # Questions
        for q_tuple in cat["questions"]:
            qdata = {
                "category": cat["name"],
                "emoji": cat["emoji"],
                "q": q_tuple[0],
                "opts": q_tuple[1],
                "ci": q_tuple[2],
                "color_top": cat["color_top"],
                "color_bot": cat["color_bot"],
                "q_num": q_num,
                "total_q": total_q,
            }
            sc, _ = build_question_scene(qdata)
            scenes.append(sc)
            q_num += 1

    # Outro
    va_outro = piper_say(
        "That's all 30 questions! Comment your score below. "
        "Subscribe for more trivia every day!"
    )
    scenes.append(Scene(
        OUTRO_DUR,
        r_outro,
        voice_events=[(va_outro, 0.4)],
        sfx_events=[(ding(), 0.2), (correct(), 3.2)]
    ))

    return scenes

# ─── Chapter timestamps generator ─────────────────────────────────────────────

def build_chapters(scenes):
    """Return YouTube chapter description lines."""
    lines = []
    t = 0.0

    def ts(sec):
        s = int(sec)
        return f"{s//60}:{s%60:02d}"

    q_num = 1
    for sc in scenes:
        rf = sc.render_fn
        # Identify scene type by duration pattern
        if sc.dur == INTRO_DUR and q_num == 1:
            lines.append(f"{ts(t)} 🏆 Intro")
        elif sc.dur == CAT_DUR:
            # figure out which category by looking at render_fn closure
            # we tag scenes via a label attribute
            label = getattr(sc, "label", None)
            if label:
                lines.append(f"{ts(t)} {label}")
        elif sc.dur == OUTRO_DUR:
            lines.append(f"{ts(t)} 🏆 Final Score!")
        else:
            lines.append(f"{ts(t)} Q{q_num}")
            q_num += 1
        t += sc.dur

    return lines

# ─── Encoder ──────────────────────────────────────────────────────────────────

def encode_all(scenes, out_path):
    total = sum(sc.dur for sc in scenes)
    print(f"Total duration: {total:.1f}s ({total/60:.1f} min), {int(total*FPS)} frames")

    # Build combined audio
    n = int(total * SR)
    voice_mix = np.zeros(n + SR, np.float32)
    sfx_mix = np.zeros(n + SR, np.float32)
    offset = 0.0
    for sc in scenes:
        for a, at in sc.voice_events:
            i = int((offset + at) * SR)
            if i < len(voice_mix):
                end_i = min(i + len(a), len(voice_mix))
                voice_mix[i:end_i] += a[:end_i - i]
        for s, at in sc.sfx_events:
            i = int((offset + at) * SR)
            if i < len(sfx_mix):
                end_i = min(i + len(s), len(sfx_mix))
                sfx_mix[i:end_i] += s[:end_i - i]
        offset += sc.dur

    combined = voice_mix[:n] + sfx_mix[:n]
    pk = float(np.max(np.abs(combined)))
    if pk > 0:
        combined = (combined / pk) * 0.85
    mus = music(total) * 0.28
    sf.write(f"{DIR}/_voice.wav", combined, SR)
    sf.write(f"{DIR}/_music.wav", mus, SR)
    print("Audio written.")

    # Encode video
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "fast", "-crf", "20",
         "-pix_fmt", "yuv420p", f"{DIR}/_video.mp4"],
        stdin=subprocess.PIPE,
        stdout=open(f"{DIR}/_ff.log", "w"), stderr=subprocess.STDOUT
    )

    offset = 0.0
    frame_count = 0
    for sc in scenes:
        sc_frames = int(sc.dur * FPS)
        for fi in range(sc_frames):
            t_local = fi / FPS
            img = sc.render_fn(t_local)
            proc.stdin.write(img.tobytes())
            frame_count += 1
        offset += sc.dur
        if frame_count % (FPS * 10) == 0:
            print(f"  {frame_count} frames ({offset:.1f}s / {total:.1f}s)...")

    proc.stdin.close()
    proc.wait()
    print(f"Video encoded ({frame_count} frames). Muxing audio...")

    subprocess.run(
        ["ffmpeg", "-y", "-i", f"{DIR}/_video.mp4",
         "-i", f"{DIR}/_voice.wav", "-i", f"{DIR}/_music.wav",
         "-filter_complex",
         "[1:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]",
         "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
         out_path],
        stdout=open(f"{DIR}/_mux.log", "w"), stderr=subprocess.STDOUT
    )
    print(f"Done! → {out_path}")
    return out_path

# ─── Chapter description helper ───────────────────────────────────────────────

def print_chapters(scenes):
    t = 0.0
    q_num = 0
    intro_done = False
    outro_done = False
    cat_index = 0
    cat_q_index = 0
    total_q = sum(len(cat["questions"]) for cat in CATEGORIES)

    # Reconstruct timeline
    cat_labels = []
    for cat in CATEGORIES:
        cat_labels.append((cat["name"], cat["emoji"], len(cat["questions"])))

    cat_i = 0
    cat_q_remaining = 0
    scene_type_list = ["intro"]
    for cat in CATEGORIES:
        scene_type_list.append(f"cat:{cat['name']}:{cat['emoji']}")
        for _ in cat["questions"]:
            scene_type_list.append("question")
    scene_type_list.append("outro")

    print("\n=== YouTube Chapters ===")
    for i, (sc, stype) in enumerate(zip(scenes, scene_type_list)):
        s = int(t)
        ts_str = f"{s//60}:{s%60:02d}"
        if stype == "intro":
            print(f"{ts_str} 🏆 Intro")
        elif stype.startswith("cat:"):
            _, name, emoji = stype.split(":")
            print(f"{ts_str} {emoji} {name}")
        elif stype == "question":
            q_num += 1
            print(f"{ts_str} Q{q_num}")
        elif stype == "outro":
            print(f"{ts_str} 🏆 Final Score!")
        t += sc.dur

    total = sum(sc.dur for sc in scenes)
    print(f"\nTotal: {total:.1f}s = {total/60:.1f} min")

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Building Sports Trivia Ep. 1...")
    print("Generating TTS for all questions (this takes a while)...")
    scenes = build_all_scenes()
    print(f"Scenes: {len(scenes)}")
    print_chapters(scenes)
    print("\nEncoding video...")
    encode_all(scenes, OUT)
    print(f"\nOutput: {OUT}")
    sz = os.path.getsize(OUT) // (1024 * 1024)
    print(f"Size: {sz}MB")

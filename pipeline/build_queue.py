"""Build queue.json: ordered upload plan for Months 7-11 Shorts + Sports Ep. 2.

Order (6 Shorts/day at the data-driven best slots):
  M7 Science & Nature -> M8 History & Culture -> M11 Christmas -> M9 90s -> M10 Geography
Christmas is placed so it lands in December.
"""
import json, importlib, sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SLOTS = [1, 5, 9, 13, 16, 20]          # UTC hours
START = dt.datetime(2026, 11, 5, 9, tzinfo=dt.timezone.utc)   # first slot after quota reset
ORDER = [(7, "Science & Nature"), (8, "History & Culture"), (11, "Christmas & Holidays"),
         (9, "90s Nostalgia"), (10, "Geography & World")]
LONG_FORM = [  # cross-promo rotation
    ("Sports Trivia Ep. 1", "https://youtu.be/H3vez8PVGX0"),
    ("Science & Biology Trivia Ep. 1", "https://youtu.be/w-FWTBTNJHg"),
    ("General Trivia Ep. 1", "https://youtu.be/vOUs4qeYOTs"),
    ("Movies & Series Trivia Ep. 1", "https://youtu.be/-tem5EZbavM"),
    ("Songs & Pop Culture Ep. 1", "https://youtu.be/0PKYTSpiX8o"),
    ("Disney & Pixar Trivia Ep. 1", "https://youtu.be/jsm3yWgv9mQ"),
]
BASE_TAGS = ["shorts", "trivia", "quiz", "brain teaser", "thedailybrainy", "general knowledge"]
THEME_TAGS = {7: ["science", "nature", "science facts"], 8: ["history", "culture", "history facts"],
              9: ["90s", "90s nostalgia", "throwback"], 10: ["geography", "world facts", "countries"],
              11: ["christmas", "christmas trivia", "holiday quiz"]}

def clip(s, n=100):
    """Trim to YouTube's 100-char limit WITHOUT losing the trailing '#Shorts' tag.
    (Nov 2026: WYR titles were cut mid-sentence and lost #Shorts; most got 0 views.)"""
    if len(s) <= n:
        return s
    tag = " #Shorts" if s.endswith("#Shorts") else ""
    body = s[: len(s) - len(tag)] if tag else s
    return body[: n - len(tag) - 1].rstrip() + "…" + tag

def slots():
    t = START
    while True:
        for h in SLOTS:
            c = t.replace(hour=h)
            if c >= START:
                yield c
        t = (t + dt.timedelta(days=1)).replace(hour=0)

def meta(month, theme, typ, item, k):
    lf_name, lf_url = LONG_FORM[k % len(LONG_FORM)]
    promo = f"\n\n🎬 Full trivia episode: {lf_name} → {lf_url}\n🔔 Subscribe for a new brain challenge every day!"
    if typ == "fof":
        s, f, e = item
        title = clip(f"Fact or Fake: {s} 🤔 #Shorts")
        desc = f"Fact or Fake? {s}\n\nAnswer: {'FACT' if f else 'FAKE'} — {e}\n\nComment if you got it right!"
    elif typ == "quiz":
        q, opts, ci = item
        title = clip(f"Quiz: {q} 🧠 #Shorts")
        desc = q + "\n" + "\n".join(f"{chr(65+i)}) {o}" for i, o in enumerate(opts)) + \
               "\n\nYou have 3 seconds! Comment your answer 👇"
    else:
        a, b = item
        a1, b1 = a.replace("\n", " "), b.replace("\n", " ")
        title = clip(f"Would You Rather: {a1} OR {b1}? #Shorts")
        desc = f"Would you rather {a1}, or {b1}?\n\nA or B — comment your pick 👇"
    desc += promo + f"\n\n#shorts #trivia #quiz #{theme.split()[0].lower().strip('&')}"
    return title, desc, BASE_TAGS + THEME_TAGS[month]

def main():
    q, gen, k = [], slots(), 0
    for month, theme in ORDER:
        c = importlib.import_module(f"month{month}_content")
        banks = {"fof": c.FACT_OR_FAKE, "quiz": c.QUIZZES, "wyr": c.WYR}
        for day in range(1, 31):
            for typ in ("fof", "quiz", "wyr"):
                title, desc, tags = meta(month, theme, typ, banks[typ][day - 1], k)
                q.append(dict(key=f"m{month}_d{day:02d}_{typ}", file=f"m{month}_d{day:02d}_{typ}.mp4",
                              title=title, description=desc, tags=tags, categoryId="27",
                              planned_publish=next(gen).strftime("%Y-%m-%dT%H:%M:%SZ"),
                              status="pending", video_id=None))
                k += 1
    # Sports Ep. 2 long-form goes first, publishing Nov 6 18:00 UTC (8pm Cairo)
    ch = open(os.path.join(os.path.dirname(__file__), "sports_ep2_chapters.txt")).read().strip() \
        if os.path.exists(os.path.join(os.path.dirname(__file__), "sports_ep2_chapters.txt")) else ""
    q.insert(0, dict(key="sports_ep2", file="sports_ep2.mp4",
        title="Sports Trivia Ep. 2 — 30 Questions Across 8 Sports! ⚽🏀🎾 How Many Can You Get?",
        description=("You asked for it — Sports Trivia is back! 30 questions across Football, Basketball, Tennis, "
                     "Swimming, Baseball, Boxing, Athletics and the Olympics. 3 seconds per question — keep score "
                     "and comment your total!\n\nMissed Ep. 1? → https://youtu.be/H3vez8PVGX0\n\n" + ch +
                     "\n\n#sportstrivia #sportsquiz #trivia"),
        tags=["sports trivia", "sports quiz", "trivia", "quiz", "thedailybrainy", "football quiz",
              "basketball trivia", "tennis quiz", "olympics trivia", "general knowledge", "brain challenge"],
        categoryId="17", planned_publish="2026-11-06T18:00:00Z", status="pending", video_id=None))
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "queue.json")
    json.dump(q, open(out, "w"), indent=1, ensure_ascii=False)
    print(len(q), "items;", q[1]["planned_publish"], "->", q[-1]["planned_publish"])
    for month, _ in ORDER:
        its = [x for x in q if x["key"].startswith(f"m{month}_")]
        print(f"M{month}: {its[0]['planned_publish'][:10]} → {its[-1]['planned_publish'][:10]}")

if __name__ == "__main__":
    main()

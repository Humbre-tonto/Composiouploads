# The Daily Brainy — Handover to Hermes

*Written Nov 13, 2026. Read this whole document before touching the channel.*

---

## 1. What this project is

**The Daily Brainy** (`@thedailybrainy`, channel ID `UC5tO4ZljncAqK15KAxjU-hA`) is a faceless YouTube trivia channel. It belongs to the **"Money Turbo"** project: a set of faceless YouTube channels, each in its own niche, that post Shorts to grow views and reach monetization (YouTube Partner Program).

The channel has two content tracks:

- **Shorts** (1080×1920, 11–18 s each, 6 per day). There are three formats:
  - **Fact or Fake.** A statement, a 3-second countdown, then a FACT/FAKE reveal with an explanation.
  - **Quiz.** A question with three options (A/B/C), a 3-second countdown, then the correct option turns green.
  - **Would You Rather (WYR).** A split screen with option A on top and B below, a 2-second countdown, then a "Comment your pick" card.

  All Shorts have narration (Piper TTS), synthesized background music and sound effects, and a "▶ Full episode — link in description" line on the end card.
- **Long-form "trivia episodes"** (5–9 min) with chapters. Each Short's description links to one of these episodes in rotation.

**Channel stats (Nov 4, 2026):** about 100 subscribers, about 277k lifetime views, 659 videos before this batch. Quiz and Fact-or-Fake Shorts typically get 50–1,000 views each.

---

## 2. Current state (Nov 13, 2026)

### Everything is uploaded and scheduled through Jan 18, 2027

All **451 items** in the current queue are on the channel:

| Content | Publishing window | Status |
|---|---|---|
| Sports Trivia Ep. 2 (long-form, `2LBzT4MxPPA`) | Nov 6 | Live |
| Month 7: Science & Nature (90 Shorts) | Nov 5 – ~Nov 19 | Scheduled / partly live |
| Month 8: History & Culture (90) | ~Nov 19 – Dec 4 | Scheduled |
| Month 11: Christmas & Holidays (90) | ~Dec 4 – Dec 19 | Scheduled |
| Month 9: 90s Nostalgia (90) | Dec 19 – Jan 3 | Scheduled |
| Month 10: Geography & World (90) | Jan 3 – **Jan 18** | Scheduled |

- **Slots:** 6 Shorts per day at **01:00, 05:00, 09:00, 13:00, 16:00, 20:00 UTC**. Nov 8–13 have 4–5 per day because of an early scheduling gap; every other day has 6.
- **Already public before this batch:** 16 Month 7 Fact-or-Fake Shorts went up in an earlier session, so they were not re-uploaded.
- **Last audit (Nov 9):** all 420 video IDs on record exist. Each is either public or private with a `publishAt`; none is missing or unscheduled.

### Long-form episodes (cross-promo rotation)

| Episode | Video ID |
|---|---|
| Movies & Series Trivia Ep. 1 | `-tem5EZbavM` |
| General Trivia Ep. 1 | `vOUs4qeYOTs` |
| Songs & Pop Culture Ep. 1 | `0PKYTSpiX8o` |
| Disney & Pixar Trivia Ep. 1 | `jsm3yWgv9mQ` |
| Science & Biology Trivia Ep. 1 | `w-FWTBTNJHg` |
| Sports Trivia Ep. 1 | `H3vez8PVGX0` |
| Sports Trivia Ep. 2 (8 sports, 30 Qs; subscriber poll winner) | `2LBzT4MxPPA` |

Sports Ep. 2 is **not yet** in the Shorts description rotation (`LONG_FORM` in `pipeline/build_queue.py`). Add it for the next batch.

---

## 3. Open items, in priority order

1. **Next Shorts batch due before Jan 18, 2027.** Months 7–11 are used up. Write Month 12 and later. Content must be fact-checked; see §7. Render it, then upload it. One 90-Short month takes about 1 daily upload run. Start by early January at the latest.
2. **Would You Rather Shorts were getting about 0 views.**
   - **Finding:** Nov 5–8 analytics showed WYR at a median of 5 views, against about 110 for Quiz and 70 for Fact-or-Fake. The one WYR Short that YouTube did show (199 views) had retention as good as the best Quiz. So the problem is distribution, not the format.
   - **Settings ruled out:** the zero-view WYRs are public, processed and not made-for-kids, the same as the Quizzes that get views.
   - **Likely cause:** 106 of 150 WYR titles exceeded 100 characters and were cut off, losing `#Shorts`.
   - **Fix applied Nov 12 (owner approved):** 164 of 171 titles were shortened, keeping `#Shorts`. Max length is now 89 characters, e.g. *"Would You Rather: Cat night vision or bat hearing? 🤔 #Shorts"*.
   - **Still pending:** 7 WYR titles (`m7_d26–30_wyr`, `m8_d14_wyr`, `m8_d15_wyr`). Their IDs were never recorded, and search can't see them while they're private. They go public around Nov 17–26. The new titles are in `title_fix_done.json` → `pending_until_public`.
   - **To do around Nov 27:** find those 7 (search by old title, filtered by channel ID), update their titles, then compare WYR views before and after Nov 12. A check-in for this was scheduled in Claude's session for Nov 27 08:05 UTC. If you take over, either let it run or tell the owner you're handling it, so it isn't done twice.
   - **If WYR still lags:** try a stronger first-second hook, a visible "result" or poll reveal at the end, or fewer WYR per day.
3. **Owner housekeeping. Don't do these yourself without asking.**
   - 12 duplicate WYR/Fact-or-Fake copies from Nov 7 are private with no publish date and will never go live. Their IDs are in `uploaded.json` → `duplicates_unscheduled`. Delete only with the owner's explicit yes; deletion is permanent.
   - A GitHub personal access token used in an earlier session was meant to be **revoked** once uploads finished. Remind the owner. Never ask for it, store it or commit it.
4. **Long-form ideas from the backlog:** 90s Nostalgia Trivia (episode), Holiday Trivia Special (ideally live by about Dec 20), Geography Trivia.

---

## 4. Access and tools

| What | How |
|---|---|
| YouTube | **Composio** YouTube connection, alias "The daily brainy" (account ID `youtube_nod-jobbet`). Uploads use `YOUTUBE_MULTIPART_UPLOAD_VIDEO`. Title/metadata edits use `YOUTUBE_UPDATE_VIDEO`. Scheduling uses `proxy_execute("PUT", "/videos", "youtube", query_params={"part":"status"}, body=…)`. Analytics uses `YOUTUBE_QUERY_ANALYTICS`. |
| File staging | GitHub repo **`Humbre-tonto/Composiouploads`** (public). The render sandbox pushes MP4s there; the Composio workbench downloads them from `raw.githubusercontent.com`. |
| Rendering | Any Linux sandbox with Python 3, ffmpeg, DejaVu fonts, `numpy pillow soundfile piper-tts`. The Piper voice model is in the repo (`piper_en-us-lessac-medium.onnx` + `.json`). |
| Notes | The project doc `daily-brainy-upload-plan.md` (Money Turbo project) mirrors this handover. Keep it updated. |

**Before any YouTube write, verify the channel:**
```python
r, e = run_composio_tool("YOUTUBE_GET_CHANNEL_STATISTICS", {"mine": True, "part": "snippet"})
# assert the channel id == "UC5tO4ZljncAqK15KAxjU-hA"
```
The connection has pointed at the wrong channel in the past (a personal channel, and one called "Mint Briefy"). If the ID doesn't match, stop and tell the owner.

**The repo is public. Never commit secrets** (tokens, keys, passwords). Git history is permanent.

---

## 5. Repo layout (`Humbre-tonto/Composiouploads`)

| Path | Purpose |
|---|---|
| `queue.json` | Ordered upload plan: `key`, `file`, `title`, `description`, `tags`, `categoryId`. Built by `pipeline/build_queue.py`. |
| `uploaded.json` | **Source of truth for what's uploaded.** Fields: `videos` (key → video ID; 27 old entries say `id-not-listed-by-api`), `scheduled_through` (last Shorts slot used, currently `2027-01-18T09:00:00Z`), `slot_override`, `rejected_uploads`, `duplicates_unscheduled`. |
| `title_fix_plan.json`, `title_fix_done.json`, `wyr_titles_v2.json`, `other_titles_v2.json` | The Nov 12 title fix and its 7 pending items. |
| `m{7..11}_d{01..30}_{fof,quiz,wyr}.mp4` | Rendered Shorts for the current batch. |
| `sports_ep2.mp4`, `*_trivia_ep1.mp4`, etc. | Long-form renders. |
| `manifest.json`, `month2_content.json`, `months3-6_content.json`, `months7-11_content.json` | Older records and content banks. Use them for duplicate checks when writing new content. |
| `pipeline/da_lib.py` | Shared render helpers: canvas 1080×1920 @ 24 fps, audio 24 kHz, music/SFX synthesis, text layout, `crosspromo()`, ffmpeg encode and mux. |
| `pipeline/piper_voice.py` | Piper TTS wrapper. Auto-downloads the voice model from the repo, and repairs NaN and clipped samples on every call. |
| `pipeline/month{N}_content.py` | Content banks: `FACT_OR_FAKE` (statement, bool, explanation), `QUIZZES` (question, [3 options], correct index), `WYR` (A, B). 30 of each per month. |
| `pipeline/month_batch.py` | Generic renderer: `MONTH=12 python3 pipeline/month_batch.py 1 30`. Skips files that already exist, and is safe to run two months in parallel. |
| `pipeline/build_queue.py` | Builds `queue.json` (titles, descriptions, tags, cross-promo rotation). `clip()` keeps `#Shorts` when trimming to 100 characters. |
| `pipeline/yt_uploader.py` | Uploader that runs inside the Composio workbench (see §6). |
| `pipeline/merge_progress.py` | Merges a session's new uploads into `uploaded.json`. |
| `pipeline/sports_ep2_build.py`, `sports_ep2_content.py` | Scene-based long-form builder: intro, category cards, questions, outro, plus chapter generation. A template for future episodes. |
| `HANDOVER.md` | Older handover (Aug–Oct). Parts of it are outdated; for example it says TTS was abandoned, but Piper TTS is in use now. This document supersedes it. |

**Cloning without the ~800 MB of videos:**
```bash
git clone --filter=blob:none --no-checkout https://github.com/Humbre-tonto/Composiouploads.git
cd Composiouploads && git sparse-checkout set --no-cone '/*.json' '/pipeline/*.py' '/.gitignore' && git checkout main
```

---

## 6. Runbook: shipping a new month of Shorts

1. **Write content:** create `pipeline/month12_content.py` with 30 Fact-or-Fake, 30 Quiz and 30 WYR items. Then:
   - Fact-check every item (see §7) and check for duplicates against the earlier content banks.
   - Keep WYR options short. The title format is `Would You Rather: {A} or {B}? 🤔 #Shorts` and must stay at or under 100 characters.
2. **Render:**
   - Run `MONTH=12 python3 pipeline/month_batch.py 1 30`. It takes about 20 s per Short, so about 30 min for 90 on 2 CPUs.
   - Spot-check frames with `ffmpeg -ss 9 -i file.mp4 -frames:v 1 out.png`: text must not overlap the badge, and there must be no blank boxes where emoji were.
   - Check audio with `ffmpeg -af volumedetect`: max around −0.5 dB, mean around −19 dB.
3. **Queue:**
   - Add the month to `ORDER` in `build_queue.py` and run it.
   - Better: append only the new items, so existing keys stay untouched.
   - Confirm every title is ≤100 characters and ends with `#Shorts`.
4. **Push** the MP4s and `queue.json` to GitHub.
5. **Upload.** Run **right after the quota reset, at 08:05 UTC**. In the Composio workbench:
   ```python
   import requests, time, contextlib, io
   src = requests.get(f"https://raw.githubusercontent.com/Humbre-tonto/Composiouploads/main/pipeline/yt_uploader.py?t={int(time.time())}").text
   exec(src)
   s = load_state(); s["new"] = {}; save_state(s)        # start a clean session log
   with contextlib.redirect_stdout(io.StringIO()):
       res = run(max_uploads=40, time_budget=155)        # repeat in new cells until a quota error or remaining == 0
   ```
   `run()` skips keys already in `uploaded.json` and schedules each upload into the next free slot after `scheduled_through`. It stops cleanly on quota errors.
6. **Verify** every new upload by ID with `YOUTUBE_GET_VIDEO_DETAILS_BATCH` (`privacyStatus == "private"` and `publishAt` set). Re-run `set_schedule()` for any missing `publishAt`. If an ID doesn't exist, remove its key so it gets re-uploaded; use `slot_override` to put it back in its original slot.
7. **Record:**
   - Run `python3 pipeline/merge_progress.py '<json of load_state()["new"]>'`, then commit and push `uploaded.json`. Do this **every session**.
   - The workbench sandbox is wiped between days; only the repo persists.
8. **Repeat daily** until `remaining == 0`. Each day gets about 100 uploads.

---

## 7. Hard-won lessons. Don't repeat these mistakes.

**Quotas and limits**
- Composio's YouTube connection uses **one Google API quota shared by all Composio users**. It's drained most of the day: even a 1-unit read returns `403 quotaExceeded`.
- The quota resets at **midnight Pacific = 08:00 UTC** during US standard time (Nov–Mar), or **07:00 UTC** during daylight time. Do all Data API work right after the reset.
- Upload caps hit during a run:
  - About **100 uploads/day per channel**: "user has exceeded the number of videos they may upload".
  - Once, Composio's project-wide "Video Uploads per day" limit (429).
  - On either one, stop cleanly. Don't retry in a loop.
- **YouTube Analytics** (`YOUTUBE_QUERY_ANALYTICS`) has its **own quota** and works while the Data API is drained.
  - Its data lags **2–3 days**.
  - `dimensions=video` returns only the top 200 videos unless you filter with `filters="video==id1,id2,…"` (≤200 IDs per call).
  - Useful metrics: `views, averageViewDuration, averageViewPercentage`, `elapsedVideoTimeRatio` + `audienceWatchRatio` (retention), and `insightTrafficSourceType` (SHORTS = Shorts feed).

**Never infer upload state from YouTube's listing**
- The uploads-playlist API (`UU5tO4ZljncAqK15KAxjU-hA`) **hides about 100 private scheduled videos**: it returns repeated rows (900 rows, 792 unique). Trusting it caused **12 duplicate uploads** on Nov 7.
- `uploaded.json` in the repo is the only source of truth.
- `YOUTUBE_SEARCH_YOU_TUBE` ignores `forMine` and only finds **public** videos. Filter results by `channelId` and confirm an exact title match.

**Uploads can be silently rejected**
- When a daily cap hits mid-upload, YouTube can return a video ID and then drop the video. This happened twice on Nov 7.
- Always re-verify each day's uploads by ID, ideally the next day as well.

**API details**
- The upload response ID is at `data["video"]["id"]`, not `data["id"]`.
- `videoFile` must be `{"s3key": ..., "name": "file.mp4", "mimetype": "video/mp4"}`; stage it with `upload_local_file(path)`.
- `YOUTUBE_UPDATE_VIDEO` with only `video_id` + `title` changes **only the title**; description, tags, category, privacy and schedule are verified untouched.
- Scheduling: `status = {"privacyStatus": "private", "publishAt": "<ISO UTC>", "selfDeclaredMadeForKids": False}`. Sending the same body without `publishAt` unschedules a video.
- The long-form episode must not anchor the Shorts slot sequence. `run()` ignores `sports*` keys when computing `scheduled_through`.

**Sandboxes reset**
- The Composio workbench (`/mnt/files`, Python state) is wiped between days.
- The render container can also be replaced; this happened mid-render once.
- Background jobs die with the container. The renderer skips files that already exist, so check for truncated MP4s with `ffprobe` and re-run.

**Content quality**
- **Fact-check everything before rendering.** About 65 of 450 items in Months 7–11 were wrong, outdated, duplicated or ambiguous. Examples:
  - "Iceland mostly ice / Greenland mostly green" was marked True.
  - "Tokyo > Canada population" is outdated.
  - "Gutenberg Bible was the first printed book" is wrong; the Diamond Sutra came earlier.
  - Some quizzes had two correct options (mitosis/meiosis; France/Corsica).
- Prefer stable, well-documented facts. Avoid "first ever", "only", "most" claims unless they're solid. Make sure the explanation agrees with the verdict.
- **Titles:** ≤100 characters, always ending in `#Shorts`. Long WYR titles that lost `#Shorts` correlated with zero distribution.

**Visual and audio**
- DejaVu fonts have **no emoji**: 🎬 and 👇 rendered as blank boxes. Use symbols like `▶` on-screen. Emoji are fine in titles and descriptions.
- Long quiz questions overlapped the "QUIZ" badge. `month_batch.py` now shrinks the font to fit above the options.
- YouTube **ignores all chapters if any single chapter is under 10 s.** Sports Ep. 2 uses one chapter per sport for that reason.
- **Old KittenTTS** (in the old handover) produced corrupted audio; Piper replaced it. Keep Piper's per-call NaN/clip repair.

**Safety and etiquette**
- Ask the owner before anything irreversible: deleting videos, mass edits not yet agreed, or changes to channel settings.
- Report mistakes plainly (the Nov 7 duplicates were reported the same day).
- Keep the Money Turbo project doc in sync after each session.

---

## 8. Quick reference

| Item | Value |
|---|---|
| Channel | The Daily Brainy · `@thedailybrainy` · `UC5tO4ZljncAqK15KAxjU-hA` |
| Uploads playlist | `UU5tO4ZljncAqK15KAxjU-hA` (unreliable for private videos) |
| Repo | `Humbre-tonto/Composiouploads` (public) |
| Posting slots (UTC) | 01:00, 05:00, 09:00, 13:00, 16:00, 20:00 |
| Shorts category | 27 (Education); long-form Sports: 17 |
| Run uploads at | 08:05 UTC (US standard time) / 07:05 UTC (US daylight time) |
| Scheduled through | 2027-01-18 09:00 UTC |
| Next batch needed by | ~Jan 18, 2027 (start by early Jan) |
| Pending | 7 WYR title updates (~Nov 27); WYR performance review; Month 12+ content |

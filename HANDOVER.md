# The Daily Brainy — Channel Handover

## ⚡ QUICKSTART (read this first)

**Channel:** `@thedailybrainy` | **ID:** `UC5tO4ZljncAqK15KAxjU-hA`
**Owner account:** mheldinm93@gmail.com
**Repo:** `Humbre-tonto/Composiouploads` (staging bridge — not a permanent archive)

### Session checklist (do in this order every time)

1. **Verify channel** before touching YouTube — always run this first:
   ```python
   run_composio_tool("YOUTUBE_GET_CHANNEL_STATISTICS", {"mine": True, "part": "snippet"})
   # assert title == "The Daily Brainy"
   ```
   The connection has silently pointed at wrong channels before. If it's not The Daily Brainy, stop and tell the human.

2. **Check manifest.json** (fetch from repo raw URL) to know what's already uploaded — don't re-upload what's already there.

3. **Check pending count** before scheduling — query the channel's uploads playlist filtered by `privacyStatus=private`. Best posting slots: **01:00, 05:00, 09:00, 13:00, 16:00, 20:00 UTC** (data-driven from 122-video analysis — see Section 8).

4. **Rendering** — pipeline lives in `pipeline/` subfolder of this repo. Download to sandbox, install deps, go:
   ```bash
   pip install soundfile piper-tts --break-system-packages
   # voice model auto-downloads from this repo on first use (piper_voice.py)
   python3 pipeline/month3_batch.py 1 30   # renders month3, days 1-30
   ```
   Check renders with: `ls /mnt/user-data/outputs/month3/*.mp4 | wc -l` (should be 90)

5. **Pushing to GitHub** — use `git clone` + `git push` with the token as basic-auth in the remote URL for any file >5MB. The REST API (`PUT /contents/{name}`) works for small files but errors on large ones.

6. **Uploading to YouTube** — stage via `upload_local_file(path)` → `s3key` → `YOUTUBE_MULTIPART_UPLOAD_VIDEO`. Schedule via `proxy_execute("PUT", "/videos", "youtube", ...)`. YouTube's daily upload quota is ~14–18 videos; stop cleanly on quota errors, don't retry-loop.

7. **Update manifest.json** after every successful upload session — push it back to the repo.

### Key files in this repo
| File | Purpose |
|------|---------|
| `manifest.json` | Source of truth for what's uploaded (544 entries: 540 shorts + 4 long-form) |
| `months3-6_content.json` | Fact-or-Fake, Quiz, WYR content banks for months 3–6 |
| `month2_content.json` | Month 2 content bank |
| `pipeline/da_lib.py` | Shared visual/audio rendering helpers |
| `pipeline/piper_voice.py` | Piper TTS wrapper (auto-downloads voice model from this repo) |
| `pipeline/month3_batch.py` | Month 3 renderer (Fact-or-Fake + Quiz + WYR) |
| `pipeline/month4_batch.py` | Month 4 renderer |
| `pipeline/month5_batch.py` | Month 5 renderer |
| `pipeline/month6_batch.py` | Month 6 renderer |
| `piper_en-us-lessac-medium.onnx` | Piper voice model (~60MB) |
| `piper_en-us-lessac-medium.onnx.json` | Piper voice model config |
| `HANDOVER.md` | This document |

### Current content state (as of last update)
- **Months 1–6** — all 540 Shorts uploaded and scheduled, Aug 6–22 cadence
- **Long-form episodes live:**
  - Movies & Series Trivia Ep. 1 → `youtu.be/-tem5EZbavM`
  - General Trivia Ep. 1 → `youtu.be/vOUs4qeYOTs`
  - Songs & Pop Culture Ep. 1 → `youtu.be/0PKYTSpiX8o`
  - Disney & Pixar Trivia Ep. 1 → `youtu.be/jsm3yWgv9mQ`
- **Next to build:** Month 7+ content (new riddles/quiz/WYR verified against all prior months), or Sports / Science & Biology / 90s Nostalgia long-form episodes

### Immediate next actions
1. Push Months 4–6 MP4s to GitHub (Month 3 and all long-form already pushed)
2. Upload and schedule Months 4, 5, 6 to YouTube (one month per quota session)
3. Add new episode video IDs to `LONG_FORM_EPISODES` rotation in `pipeline/da_lib.py`
4. Plan Month 7 content (use `months3-6_content.json` as the duplicate-check reference)

---


**Channel:** The Daily Brainy — `@thedailybrainy`
**Channel ID:** `UC5tO4ZljncAqK15KAxjU-hA`
**Owner:** mheldinm93@gmail.com (Google account) — verify with the human before any upload, channel identity has flipped unexpectedly before (see Known Issues).
**Platform:** YouTube, via Composio's YouTube MCP connector + GitHub as a file-staging bridge.

This doc is the full context another agent (or a future session of this one) needs to keep running the channel without re-learning everything the hard way.

---

## 1. What this channel is

A faceless trivia/brain-teaser channel with two content tracks:

1. **Shorts** (vertical, 10–15s): Riddles, Quizzes, Would You Rather — posted on a rotating daily cadence.
2. **Long-form** (16:9 landscape, 8+ min): "Game Night Trivia" style episodes, themed per series (General Trivia, Movies & Series, Sports, Science & Biology, Songs & Pop Culture, 90s Nostalgia — the last one hand-written since there's no source API for decade-specific trivia).

Monetization goal: YouTube Partner Program. Two paths — 1,000 subs + 4,000 watch hours (long-form-driven) OR 1,000 subs + 10M Shorts views in 90 days. Long-form is the better watch-hour lever; Shorts are the discovery/reach engine. Both formats reinforce each other per YouTube's own hybrid-creator data, hence running both.

---

## 2. Repo layout (this repo: `Humbre-tonto/Composiouploads`)

This repo is used purely as a **file-staging bridge** — the code sandbox that renders videos can't host public URLs, but it can push to GitHub, and Composio's remote workbench can pull from `raw.githubusercontent.com`. It is **not** a permanent archive — videos get deleted/replaced here routinely. Treat it as scratch space, not history.

Naming convention: `d{DD}_{type}.mp4` where `DD` is a 1-based day index (01–30) and `type` is `riddle`, `quiz`, or `wyr`. Long-form episodes use descriptive names, e.g. `movies_series_trivia_ep1.mp4`.

---

## 3. The render pipeline (lives in the code sandbox, NOT this repo — rebuild from this doc if missing)

The sandbox's `/home/claude` directory has been observed to **partially reset between sessions** — sometimes a subdirectory vanishes while others survive. Always check `ls /home/claude/studio` before assuming the pipeline exists; if it's gone, the full source is reconstructable from this doc's description below (or from conversation history if available).

### Shorts pipeline — `/home/claude/studio/`
- `da_lib.py` — shared helpers: audio synthesis (music + SFX, **no voice**), PIL rendering primitives, ffmpeg encode/mux wrapper. Includes `crosspromo(d)` which draws the "🎬 Full trivia episodes on this channel" CTA — this is baked into every Short's reveal/outro frame.
- `month_batch.py` — content banks (30 riddles, 30×3 quiz questions flattened to `QUIZ_FLAT`, 30×2 WYR dilemmas flattened to `WYR_FLAT`) + per-format builders/renderers + CLI driver (`python3 month_batch.py <start_day> <end_day>`). Renders skip any file that already exists, so it's safely re-runnable.
- `seo_meta.py` — generates SEO-real titles/descriptions from the actual question text (e.g. "Riddle: What gets bigger the more you take away? 🧠 Brain Teaser #Shorts") instead of generic "Daily Riddle #12" labels. Every description includes the cross-promo line pointing to long-form episodes.

**Format specs:** 1080×1920, 24fps, ~10–15s each. Riddle: card → 3s think countdown → green reveal card + CTA. Quiz: question → 4 options → 3s countdown → reveal + CTA. WYR: split-screen A/B → 2s countdown → ding → outro + CTA. Audio: synthesized chiptune-ish loop + tick/ding/whoosh/correct SFX, verified RMS ~0.13, no clipping.

### Long-form pipeline — `/home/claude/gamenight/` and `/home/claude/moviesseries/`
Each episode is its own folder with `questions.json` (real OpenTDB-sourced + hand-written in matching style, clearly should stay factually distinct even though visually identical) and a `render.py` copied from the gamenight original.

**Rendering at this scale is slow** (an 8-min 1920×1080 episode ≈ 11,700+ frames) and will not finish in one sandbox call. Use the **segment approach**: render PNG frames in chunks (`python3 render.py range START END`), then `python3 render.py seg START END IDX` to encode each chunk to its own small MP4, then `python3 render.py concat N` to stitch, then `python3 render.py mux` for final audio mux. Do NOT try a single long-running background process — background jobs do **not** survive between tool calls in this environment.

**Content sourcing:** Open Trivia DB (`opentdb.com/api.php`) is free, no key. **Known limitation:** the web_fetch tool caches by base path and ignores query params — repeated calls with different `category`/`amount` params can return identical cached results. Only trust genuinely new data from a fresh, never-before-fetched URL. Pad out episodes to 25–30 questions by writing additional questions in matching style/difficulty using only well-known, verifiable facts — never invent specific stats or dates.

---

## 4. Critical lessons learned (do not repeat these mistakes)

### TTS is abandoned — do not re-enable voice without extreme caution
KittenTTS (`kitten_tts_nano_v0_2.onnx`) produces **random per-call garbage samples** (NaN and ~1e38-magnitude spikes) that cause audible clicks/distortion even after mixing-stage clipping hides the aggregate stats. This is **non-deterministic** — identical repeated calls to the same text produce different corruption each time. A numpy/onnxruntime version mismatch (numpy 2.x + newer onnxruntime) made it catastrophically worse, but even after pinning `numpy==1.26.4` + `onnxruntime==1.18.1`, the underlying corruption did not fully go away — it just became less severe. **Current decision: run all Shorts and long-form audio as music+SFX only, no narration.** If a future agent wants to revisit voice, the fix must repair (nan_to_num + interpolate over `|x|>1.0` samples) **every individual TTS call's output immediately**, before any mixing — checking only the final mixed/aggregate stats is not sufficient, since clipping can hide per-call corruption as an audible click rather than a visible level change. Always render a short sample and have the human confirm it sounds right before mass-producing anything with voice.

### The YouTube connection is unstable across sessions — always verify the channel
Across this project, the Composio YouTube connection has pointed at **three different channels** at different times: a personal channel (`@mohamedhossameldin628`), a channel called "Mint Briefy" that appeared unexpectedly, and the correct one, The Daily Brainy. **Before every single upload or batch of uploads**, call:
```python
run_composio_tool("YOUTUBE_GET_CHANNEL_STATISTICS", {"mine": True, "part": "snippet"})
```
and assert the title is exactly `"The Daily Brainy"`. If it's anything else, **stop immediately** — do not upload — and if something already went out to the wrong channel, delete it right away (see cleanup pattern below). This check takes one call and has caught real near-misses.

### YouTube upload limits — one confirmed mechanism, one disproven theory
**Confirmed:** there is a **daily raw upload count limit**, observed anywhere from ~11 to ~43 successful uploads before hitting `"YouTube upload quota exceeded... daily video upload limit... wait 24 hours"`. It appears to reset on a real calendar-day-ish cycle, not a rolling 24h-since-last-upload window (sessions run back-to-back sometimes still hit it immediately, other times get a much bigger allowance). **There is no reliable way to predict the exact number in advance** — just attempt uploads and stop cleanly the moment this specific error string appears.

**Disproven:** an earlier theory held that there was *also* a hard cap of ~19 videos simultaneously `private` with a future `publishAt` ("pending"). This was later directly disproven — a batch of 31 uploads succeeded in one pass even with 40 videos already pending. **Do not design around a pending-count cap; it does not appear to be real.** (It's possible the two mechanisms were confused with each other during an earlier debugging session — the daily count cap was likely the whole explanation all along.)

**Practical workflow every session:** just attempt uploads in batches, verify channel identity before starting, watch for the quota error string, and stop cleanly when it appears (with retries/backoff already handled automatically by Composio's rate-limit handling — don't add your own retry loop on top of it, since that just wastes calls hitting an already-known wall). Update `manifest.json` with every success before ending the session, in case the session ends abruptly.

### Sandbox environments are not persistent/stable — plan accordingly
- The code sandbox's `/home/claude` can partially reset between turns.
- Composio's remote workbench sandbox **rotates its container** between sessions (observable via a changing `sandbox_id_suffix`), wiping `/mnt/files` and any Python kernel state (`state` dict, downloaded files in `/home/user/...`). **Always redefine helper functions and re-download files at the start of a new session** — do not assume persistence.
- Background processes (`nohup ... &`) started in one bash tool call **do not survive** into the next call. For long-running renders, use the resumable-chunks-of-frames pattern instead, or run one bounded operation per call.
- If a Python cell's stdout gets redirected (e.g. via `contextlib.redirect_stdout` inside a `ThreadPoolExecutor`) and the cell times out mid-execution, the redirect can be left dangling, silencing all future `print()` output. Always persist important state to a file (`json.dump` to a path under `/mnt/files/`) rather than relying only on printed output, in case a cell times out.

### GitHub token permissions
Fine-grained tokens default to read-only unless **Contents: Read and write** is explicitly granted at creation. If pushes return `403 Resource not accessible by personal access token`, this is almost always the cause — check the token's repo permissions before assuming a code bug.

### Never commit secrets to this repo
This repo is **public**. Never write a live API key, access token, or credential into any file pushed here — git history is permanent even after a file is edited or deleted. Tokens should be passed to the sandbox via environment variables at runtime only, never committed.

---

## 5. Current channel state (as of this handover — UPDATED after Month 2)

- **Month 1 (90 videos, no voice):** Fully uploaded and scheduled, Jul 19 – Aug 6 area. Uses `d01`–`d30` filename prefix.
- **Month 2 (90 videos, Piper-narrated):** Fully uploaded and scheduled, **Aug 6 – Aug 21**, 6/day cadence. Uses `m2_d01`–`m2_d30` filename prefix — a **different prefix on purpose**, so manifest keys never collide with Month 1 even though both cover "day 1–30."
- **`manifest.json`** in the repo is the source of truth for what's been uploaded — 180 entries (90 Month 1 + 90 Month 2), all marked `"uploaded"`. **Do not rely on parsing video titles to track upload state** — see the SEO-title lesson below.
- **Long-form:** 1 episode live — "Movies & Series Trivia Ep. 1" (video ID `-tem5EZbavM`). Every Month 2 Short's description includes a clickable link to it (`🎬 Watch the full episode...`) to cross-promote and build long-form watch hours. This is implemented via a `LONG_FORM_EPISODES`-style rotating list in the metadata generator — add new episode IDs there as they go live so future Shorts round-robin across all available episodes instead of just Episode 1.
- **Narration is back, using Piper TTS (not KittenTTS)** — see section 7 below for the full story.

### Lesson: SEO titles broke the old tracking method
Early in Month 2 I made titles more SEO-real (e.g. "Riddle: What gets bigger the more you take away? 🧠 Brain Teaser #Shorts" instead of "Daily Riddle #12"), which is good for discovery but **removed the "#N" day-number pattern** that a title-parsing regex had relied on to track what's already uploaded. This caused a real undercount/confusion mid-session. **Fix: always track upload state via `manifest.json` in the repo, never by parsing video titles.** Keys are `{prefix}_d{DD}_{type}` (e.g. `m2_d14_quiz`). Update and push the manifest immediately after any successful upload batch — don't wait until the very end, in case a session ends abruptly.

### Lesson: unrelated files can appear in the repo — verify before assuming problems
At one point the repo contained `README.md` and `seo_batch.json` that weren't immediately recognized. Investigation showed both were benign (`README.md` is GitHub's own default file from repo creation; `seo_batch.json` turned out to be legitimate metadata this pipeline had generated earlier). **Before assuming repo contents are wrong, foreign, or a sign of compromise, actually fetch and read them** — don't guess. Same applies to files that seem to exist "unexpectedly" in the code sandbox (see next lesson).

### Lesson: the code sandbox can contain unlogged prior work — verify before trusting OR discarding it
More than once, a fresh sandbox session revealed files (`month2_batch.py`, a partial no-voice render of days 1–10, etc.) that weren't explicitly logged as created in the visible conversation. These turned out to be legitimate leftover work from earlier in the same session (likely generated during a period whose logs weren't visible due to context summarization), not corruption or foreign content. **Don't blindly delete unexplained files, but don't blindly trust their content either** — in this case a "found" content bank of riddles/quiz questions/WYR dilemmas had to be independently re-verified for zero duplication against Month 1 before use, exactly like freshly-written content would be. It checked out clean, and became the actual Month 2 content bank.

---

## 6. Recommended immediate next steps for the next agent

1. Re-verify channel identity before touching anything.
2. Month 1 and Month 2 (180 videos) are both fully scheduled through ~Aug 21. **Month 3 content needs to be planned before then** — write fresh riddles/quiz questions/WYR dilemmas, verify zero duplication against **both** Month 1 (`month1_banks.py`-equivalent, reconstructable from RIDDLES/QUIZZES/WYR literals in this doc's history or from the manifest + re-fetching video descriptions) and Month 2 (`month2_content.json` in the repo has the full Month 2 bank in machine-readable form — fetch and diff against it).
3. Use a **new filename prefix** for Month 3 (e.g. `m3_`) to keep manifest keys distinct, same reasoning as Month 2.
4. Decide whether Month 3 keeps narration (Piper) or not — it worked well in Month 2, no corruption found in spot-checks across all 90 videos.
5. Build out more long-form episodes (General Trivia is the most scaffolded from earlier work; Sports, Science & Biology, Songs & Pop Culture, and a hand-written 90s Nostalgia series are all planned but not yet built) — and add each new episode's video ID to the `LONG_FORM_EPISODES` rotation list so Shorts cross-promote across all of them, not just Episode 1.
6. Once YPP-eligible, pull analytics via the YouTube Data API to see which Shorts/hooks retain viewers best.
7. Consider manually setting YouTube's native **"Related Video"** field (Studio → edit a Short → Related Video) on newer/trending Shorts — this is a real, better-converting feature than a description link, but **it is not exposed via the API** (confirmed via search — third-party creator tools have explicitly requested this and it doesn't exist), so it must be done by hand in the Studio app. The channel owner already has "advanced feature access" enabled for this.

---

## 7. Piper TTS — narration is back (replacing KittenTTS)

After KittenTTS proved unfixably unreliable (see section 4's TTS warning — still accurate, keep it), the channel owner asked for a better offline TTS. **Piper TTS** (`pip install piper-tts`) was substituted in and is working well.

**Why Piper is different/better:** stress-tested with 15 repeated calls across 5 varied lines — **zero corrupted samples across 823,040 total audio samples**, versus KittenTTS's near-constant per-call corruption (hundreds of NaN/extreme-value samples per call, non-deterministically). Piper is a mature, widely-deployed project (used in Home Assistant / Rhasspy voice stack), not an experimental model.

**Where the voice model lives:** Hugging Face (the usual home for Piper voices) is **not reachable** from this sandbox's network allowlist. The voice was instead sourced from **Piper's own GitHub releases** (`rhasspy/piper`, tag `v0.0.2`, which bundles older-format but fully-compatible voice files as release assets) — reachable because `github.com` and `release-assets.githubusercontent.com` are on the allowlist. The chosen voice is `en-us-lessac-medium`. Both files are pushed to this repo:
- `piper_en-us-lessac-medium.onnx` (~60MB)
- `piper_en-us-lessac-medium.onnx.json` (config)

**Important: the ONNX file is too large for GitHub's simple Contents API** (`PUT /repos/.../contents/{path}`) — it returned `422 Sorry, your input was too large to process` even via the Git Data API's blob-create endpoint. **The fix was to use real `git` (clone, add, commit, push with the token as basic auth in the remote URL)**, not the REST API, for any file over roughly a few MB. Keep this in mind for any future large binary assets.

**Integration:** `studio2/piper_voice.py` wraps Piper — downloads the voice model from this repo if missing (so it survives sandbox resets), synthesizes, **sanitizes output** (nan_to_num + interpolate over any `|sample| > 1.0`, as a defensive measure even though Piper hasn't shown this issue), normalizes, and resamples from Piper's native 16kHz to the pipeline's working 24kHz via simple linear interpolation (no scipy dependency needed).

The Month 2 builders (`studio2/month2_batch.py`) narrate: the riddle/question is spoken, then a timed countdown, then the answer is spoken on reveal — timing is now **text-length-dependent** (each video's duration varies, e.g. 8.8–11.8s) rather than the fixed durations Month 1 used. This is expected and fine; don't mistake variable durations for a bug.

**Standing rule, unchanged from before:** always render one full sample and get explicit human confirmation on how it sounds before mass-producing with any voice pipeline. The scripted stress-test (15 calls, checking for `|sample|>1.0` and NaN) is a good automated pre-check, but it is not a substitute for an actual human listening — do both.

---



## 8. Posting schedule — data-driven, updated after analytics review

After Month 2 accumulated real view data, an analytics pass (Data API `videos.list` statistics correlated against each video's actual publish hour, 122-video sample) found a clear pattern:

**Best hours (UTC), ranked, all with n≥6 sample size:** 16:00 (688 avg views), 17:00 (468), 05:00 (399), 01:00 (390), 13:00 (350), 20:00 (347), 09:00 (339).
**Worst hour:** 21:00 UTC — 84 avg views across a full 12-video sample. Avoid this slot.
**By weekday:** Thursday/Tuesday/Monday outperform; Sunday underperforms despite the largest sample (28 videos) — a real pattern worth keeping in mind, though daily posting consistency still matters more than skipping weak days entirely.

**Current live schedule (adopted from this analysis):** 6/day at **01:00, 05:00, 09:00, 13:00, 16:00, 20:00 UTC**. All future uploads should use this hour set instead of an arbitrary fixed interval. This replaced an earlier naive "every 4 hours starting from whenever" approach that happened to land some videos in the weak 21:00 slot. All previously-pending Month 2 videos were reshuffled onto this new schedule (condensed from a tail stretching to Aug 21 down to just Aug 6-7).

**Caveat:** this analysis used YouTube Data API statistics (view/like counts) as a proxy, not true YouTube Analytics "when your audience is active" data — that requires a `yt-analytics.readonly` OAuth scope that the current connection doesn't have, and getting it requires a manual reconnect (the channel owner would need to grant it, similar to the "advanced feature access" needed for Related Video). A dedicated `youtubeanalytics` Composio toolkit exists in principle but returned "Toolkit not found" when connection was attempted — may need the channel owner to set this up from their end if real analytics access is wanted. If that scope ever gets added, re-verify this hour ranking against real audience-activity data rather than assuming the proxy analysis is final.

**Recommendation for the next agent:** re-run this same analysis periodically (e.g. after each month's content has had a couple weeks to accumulate views) to see if the pattern holds or shifts, rather than treating this one-time snapshot as permanent.

---

## 9. Long-form episodes — status

1. **Movies & Series Trivia Ep. 1** — video ID `-tem5EZbavM`. Music+SFX only (no narration), ~8:08.
2. **General Trivia Ep. 1** — video ID `vOUs4qeYOTs`. Narrated, ~8:35.
3. **Songs & Pop Culture Ep. 1** — video ID `0PKYTSpiX8o`. Narrated, ~8:43. Public and live.. **First narrated long-form episode**, using Piper TTS (see section 7). ~8:35. 30 questions (10 genuinely sourced from Open Trivia DB via the session-token trick below, 20 hand-written, verified zero duplicates against both Month 1 and Month 2 Shorts banks). Public and live.

### Lesson: the Open Trivia DB caching problem has a real fix — session tokens
Earlier sessions found `web_fetch` caches by a normalized version of the URL (seemingly ignoring most query params beyond `amount`), making it impossible to get varied fresh batches by just changing `category`/`difficulty`. **The fix: request a session token first** (`GET https://opentdb.com/api_token.php?command=request`, search for the URL first since web_fetch requires a prior search hit), then include that token in the actual questions request (`&token=...`). Since the token makes the URL genuinely unique, it bypasses the cache and returns real fresh questions — confirmed working, got 10 genuinely new questions this way for General Trivia Ep. 1. **Still only reliably yields one fresh batch per session** — further variations on the same request pattern re-hit the cache — so budget for "10 real questions per episode, write the rest by hand in matching style" as the realistic sourcing pattern, not "fetch all 25-30 for free."

### Building narrated long-form: key implementation notes for the next episode
- The long-form renderer (`generaltrivia/render.py`, adapt by copying) originally used **fixed timing** (10s think + 3.5s hold per question, always the same regardless of content). Adding narration requires **variable, speech-length-dependent timing** instead — same lesson as the Shorts pipeline.
- **Critical: cache the TTS timeline.** With 30 questions × 2 narration lines (question + answer) = 60 Piper calls, and the render script being invoked many times across chunked frame-rendering calls (segmented rendering is required for long-form — see below), naively re-running all 60 TTS calls on every invocation wastes huge amounts of time. Build the timeline once, pickle it to disk, and load from cache on subsequent invocations of the same script. See `build_timeline()` / `CACHE` pattern in `generaltrivia/render.py`.
- **Watch the total duration vs. the 8-minute mid-roll-ad threshold.** Narration timing is unpredictable until you actually run it — the first narrated pass of General Trivia Ep. 1 came in at only 5:51 (too short), requiring a bump to the per-question think-time (6.0s→11.0s) and a re-render to land at 8:35. Always check `TOTAL` after building the timeline and adjust `THINK`/`REVEAL_HOLD` before committing to the full frame render, since a full re-render is expensive (12,000+ frames).
- **Rendering a long-form video is too slow for one continuous encode.** Use the same segmented approach as Episode 1: render frames to PNGs in chunks (`range START END`), encode each chunk to its own small MP4 (`seg START END IDX`), concatenate (`concat N`), then build audio and mux (`mux`). A full episode needs roughly 4 segment-encode calls plus several frame-range calls — budget ~8-10 tool calls total for one episode.
- **Always verify audio thoroughly before sharing or uploading**, even with Piper's good track record: check RMS (~0.07-0.10 is healthy for narration+music), zero NaN, zero samples with `|x|>0.999` across the *entire* decoded track, not just a sample. This has caught real problems before (KittenTTS) and costs almost nothing to run.

---

## 10. Composio usage patterns worth keeping

- `run_composio_tool("YOUTUBE_MULTIPART_UPLOAD_VIDEO", payload)` — payload needs `videoFile: {name, mimetype, s3key}`; get `s3key` from `upload_local_file(path)` first.
- `proxy_execute("PUT", "/videos", "youtube", query_params={"part": "status"}, body={...})` — this is how scheduling (`publishAt`) gets set; the multipart upload tool itself has **no scheduling field**.
- `proxy_execute("GET", "/playlistItems", "youtube", query_params={"part": "snippet,status", "playlistId": UPLOADS_PLAYLIST_ID, "maxResults": "50"})` — enumerate channel uploads (uploads playlist ID = channel ID with `UC` replaced by `UU`).
- `proxy_execute("DELETE", "/videos", "youtube", query_params={"id": vid})` — delete a video (used for wrong-channel cleanup).

---

*Written by Claude (Anthropic) at the end of a session building and running this channel. Ask the human for current context/decisions on anything not covered here — this doc reflects the state at time of writing, not necessarily now.*

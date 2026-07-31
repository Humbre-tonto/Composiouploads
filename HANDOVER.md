# The Daily Brainy — Channel Handover

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

### YouTube has two separate upload limits — both matter
1. **A pending-schedule cap of ~19 videos.** You cannot have more than ~19 videos simultaneously in `privacyStatus=private` with a future `publishAt` — further uploads get rejected with a quota error even if you haven't uploaded anything "today." This is fixed by scheduling tighter (we moved from 3/day to **6/day, every 4 hours**) so the backlog drains fast enough to keep headroom open.
2. **A separate raw daily upload count cap**, roughly 14–18 successful uploads per rolling window, independent of the pending cap. This one really is time-based and resets roughly daily.

**Practical workflow every session:** check current pending count (query `playlistItems` for the channel's uploads playlist, `UU` + channel ID without `UC`, filter by `privacyStatus=private`), compute headroom = 19 − pending, then attempt uploads up to that headroom OR until a "quota exceeded" error appears, whichever comes first. Stop cleanly on either signal, do not retry-loop against a quota error.

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

## 5. Current channel state (as of this handover)

- **90-video month planned**: 30 days × (1 riddle + 1 quiz + 1 WYR).
- **Uploaded and scheduled so far:** 59 of 90 (through day 20's quiz; day 20's WYR onward still pending upload).
- **Remaining:** 31 Shorts (day 20 WYR → day 30, all three types), already rendered with the cross-promo CTA and pushed to this repo.
- **Posting cadence:** 6/day, every 4 hours (riddle/quiz/wyr slots rotate through the day) — chosen to keep the pending-schedule cap from blocking uploads.
- **Long-form:** 1 episode complete — "Movies & Series Trivia Episode 1" (30 questions, ~8:08, chapters written into the description). Uploaded manually via YouTube Studio (paste-in title/description provided) due to quota constraints blocking the API upload at the time — verify it's live and check its actual video ID/URL before assuming it needs re-uploading.
- **Series planned but not yet built:** General Trivia (validated format, no full episode built yet beyond the prototype), Sports, Science & Biology, Songs & Pop Culture, 90s Nostalgia (fully hand-written, no API source).

---

## 6. Recommended immediate next steps for the next agent

1. Re-verify channel identity before touching anything.
2. Check pending count vs the ~19 cap, compute headroom, resume uploads at day 20's WYR using `seo_meta.py`'s title/description generator.
3. Once the 90-Shorts month is fully live, decide on next month's content (fresh riddles/quiz questions/WYR dilemmas — the current banks will start repeating via the flattening `% len(...)` fallback in `seo_meta.py` if reused past index 29).
4. Build out the next long-form series episode (General Trivia is the most scaffolded).
5. Consider: once YPP-eligible, pull analytics via the YouTube Data API to see which Shorts/hooks retain viewers best, and double down on those formats.

---

## 7. Composio usage patterns worth keeping

- `run_composio_tool("YOUTUBE_MULTIPART_UPLOAD_VIDEO", payload)` — payload needs `videoFile: {name, mimetype, s3key}`; get `s3key` from `upload_local_file(path)` first.
- `proxy_execute("PUT", "/videos", "youtube", query_params={"part": "status"}, body={...})` — this is how scheduling (`publishAt`) gets set; the multipart upload tool itself has **no scheduling field**.
- `proxy_execute("GET", "/playlistItems", "youtube", query_params={"part": "snippet,status", "playlistId": UPLOADS_PLAYLIST_ID, "maxResults": "50"})` — enumerate channel uploads (uploads playlist ID = channel ID with `UC` replaced by `UU`).
- `proxy_execute("DELETE", "/videos", "youtube", query_params={"id": vid})` — delete a video (used for wrong-channel cleanup).

---

*Written by Claude (Anthropic) at the end of a session building and running this channel. Ask the human for current context/decisions on anything not covered here — this doc reflects the state at time of writing, not necessarily now.*

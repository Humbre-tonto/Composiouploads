# The Daily Brainy — daily uploader. Runs INSIDE the Composio remote workbench.
# Upload state lives in uploaded.json in the repo (never inferred from the YouTube
# listing API, which hides ~100 private scheduled videos). Stops cleanly on quota errors.
# After each session: merge out["new"] into uploaded.json with pipeline/merge_progress.py and push.
#
# Usage in a workbench cell:
#   exec(requests.get(RAW + "pipeline/yt_uploader.py").text); run(max_uploads=40, time_budget=165)
# Call run() repeatedly in fresh cells; each call works within the 180 s cell limit.
import json, os, time, datetime as dt, requests

RAW = "https://raw.githubusercontent.com/Humbre-tonto/Composiouploads/main/"
CHANNEL_ID = "UC5tO4ZljncAqK15KAxjU-hA"
UPLOADS = "UU5tO4ZljncAqK15KAxjU-hA"
SLOTS = [1, 5, 9, 13, 16, 20]
STATE = "/mnt/files/brainy_state.json"
QUOTA_WORDS = ("quota", "uploadLimitExceeded", "rateLimitExceeded", "429")

def _d(r):
    d = (r or {}).get("data", r) or {}
    return d.get("response_data", d) if isinstance(d, dict) else d

def _quota(err):
    return any(w in str(err) for w in QUOTA_WORDS)

def iso(t): return t.strftime("%Y-%m-%dT%H:%M:%SZ")
def parse(s): return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)

def next_slot(after):
    t = after.replace(minute=0, second=0, microsecond=0)
    for _ in range(24 * 8):
        t += dt.timedelta(hours=1)
        if t.hour in SLOTS and t > after:
            return t
    raise RuntimeError("no slot")

def verify_channel():
    r, e = run_composio_tool("YOUTUBE_GET_CHANNEL_STATISTICS", {"mine": True, "part": "snippet"})
    if e: return False, f"channel check failed: {str(e)[:200]}"
    chans = _d(r).get("channels") or _d(r).get("items") or []
    ok = any(c.get("id") == CHANNEL_ID for c in chans)
    return ok, "ok" if ok else f"WRONG CHANNEL: {[c.get('id') for c in chans]}"

def channel_inventory():
    """title -> {id, privacy, publishAt} for every upload (incl. private/scheduled)."""
    ids, tok = [], None
    while True:
        a = {"playlistId": UPLOADS, "part": "snippet,status", "maxResults": 50}
        if tok: a["pageToken"] = tok
        r, e = run_composio_tool("YOUTUBE_LIST_PLAYLIST_ITEMS", a)
        if e: raise RuntimeError(e)
        d = _d(r)
        for it in d.get("items", []):
            sn = it.get("snippet", {})
            ids.append((sn.get("resourceId", {}).get("videoId"), sn.get("title", "")))
        tok = d.get("nextPageToken")
        if not tok: break
    inv = {}
    for i in range(0, len(ids), 50):
        chunk = [v for v, _ in ids[i:i + 50] if v]
        r, e = run_composio_tool("YOUTUBE_GET_VIDEO_DETAILS_BATCH", {"id": chunk, "parts": ["snippet", "status"]})
        if e: raise RuntimeError(e)
        for v in _d(r).get("items", []):
            st = v.get("status", {})
            inv[v["snippet"]["title"]] = dict(id=v["id"], privacy=st.get("privacyStatus"),
                                              publishAt=st.get("publishAt"))
    return inv

def set_schedule(vid, when):
    body = {"id": vid, "status": {"privacyStatus": "private", "publishAt": iso(when),
                                  "selfDeclaredMadeForKids": False}}
    return proxy_execute("PUT", "/videos", "youtube", query_params={"part": "status"}, body=body)

def upload_one(item, when):
    path = f"/tmp/{item['file']}"
    if not os.path.exists(path):
        resp = requests.get(RAW + item["file"], timeout=120); resp.raise_for_status()
        open(path, "wb").write(resp.content)
    up, e = upload_local_file(path)
    if e: return None, f"stage: {e}"
    s3 = (up.get("data", up) or {}).get("s3key") or up.get("s3key")
    r, e = run_composio_tool("YOUTUBE_MULTIPART_UPLOAD_VIDEO", {
        "title": item["title"], "description": item["description"], "tags": item["tags"],
        "categoryId": item["categoryId"], "privacyStatus": "private",
        "videoFile": {"s3key": s3, "name": item["file"], "mimetype": "video/mp4"}})
    if e: return None, e
    d = _d(r); vid = d.get("id") or (d.get("video") or {}).get("id") or (d.get("response_data") or {}).get("id")
    if not vid: return None, f"no id in {str(d)[:200]}"
    _, e2 = set_schedule(vid, when)
    try: os.remove(path)
    except OSError: pass
    return vid, (f"uploaded but schedule failed: {e2}" if e2 else None)

def load_state():
    try: return json.load(open(STATE))
    except Exception: return {"inv": None, "inv_at": None, "log": []}

def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True); json.dump(s, open(STATE, "w"))

def run(max_uploads=40, time_budget=165):
    """Upload the next pending queue items.

    Upload state comes from uploaded.json in the repo (committed after every session)
    merged with this sandbox's own session log. The YouTube uploads-playlist API hides
    ~100 private scheduled videos, so it must NOT be used to decide what's uploaded.
    After a session, merge out["new"] into uploaded.json and push it.
    """
    t0 = time.time(); s = load_state(); s.setdefault("new", {})
    out = {"uploaded": [], "stopped": None}
    ok, msg = verify_channel()
    if not ok:
        out["stopped"] = msg; return out
    bust = f"?t={int(time.time())}"
    queue = requests.get(RAW + "queue.json" + bust, timeout=60).json()
    prog = requests.get(RAW + "uploaded.json" + bust, timeout=60).json()
    done = set(prog["videos"]) | set(s["new"])
    last = parse(prog["scheduled_through"])
    for _, when in s["new"].values():
        last = max(last, parse(when))
    floor = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=75)
    for it in queue:
        if len(out["uploaded"]) >= max_uploads or time.time() - t0 > time_budget:
            break
        if it["key"] in done:
            continue
        fixed = prog.get("slot_override", {}).get(it["key"])   # re-upload into its original slot
        when = parse(fixed) if fixed and parse(fixed) > floor else next_slot(max(floor, last))
        vid, err = upload_one(it, when)
        if vid:
            s["new"][it["key"]] = [vid, iso(when)]; done.add(it["key"]); save_state(s)
            if not fixed: last = when
            out["uploaded"].append((it["key"], vid, iso(when)))
            if err:
                out["stopped"] = f"{it['key']} {vid}: {err}"; break
        else:
            out["stopped"] = ("QUOTA: " if _quota(err) else "upload error: ") + str(err)[:250]; break
    out["remaining"] = sum(1 for it in queue if it["key"] not in done)
    out["scheduled_through"] = iso(last)
    out["new"] = s["new"]
    return out

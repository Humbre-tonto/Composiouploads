"""Merge a session's new uploads into uploaded.json.
Usage: python3 pipeline/merge_progress.py '<json of {key: [video_id, publishAt]}>'"""
import json, sys, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(root, "uploaded.json")
prog = json.load(open(path)); new = json.loads(sys.argv[1])
for k, (vid, when) in new.items():
    prog["videos"][k] = vid
    if when > prog["scheduled_through"]:
        prog["scheduled_through"] = when
json.dump(prog, open(path, "w"), indent=1)
q = json.load(open(os.path.join(root, "queue.json")))
print(len(prog["videos"]), "done;", sum(1 for x in q if x["key"] not in prog["videos"]), "remaining; through", prog["scheduled_through"])

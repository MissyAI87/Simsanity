# core/nlu/socials.py
from difflib import get_close_matches
import re

SUPPORTED = {
    "x": {"aliases": ["twitter", "tw", "xtwitter", "x.com"]},
    "instagram": {"aliases": ["ig", "insta"]},
    "facebook": {"aliases": ["fb", "meta"]},
    "linkedin": {"aliases": ["li", "ln", "linkdin"]},
    "tiktok": {"aliases": ["tt", "tik", "tik tok"]},
    "youtube": {"aliases": ["yt", "you tube", "shorts"]},
    "pinterest": {"aliases": ["pin", "pins"]},
    "reddit": {"aliases": ["rdt"]},
    "snapchat": {"aliases": ["snap"]},
}

ALL_KEYWORDS = {"all", "everywhere", "anywhere"}

# alias → canonical
ALIAS_LOOKUP = {}
for k, v in SUPPORTED.items():
    ALIAS_LOOKUP[k] = k
    for a in v["aliases"]:
        ALIAS_LOOKUP[a] = k

def _clean(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s/|,.-]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def _tokens(s: str):
    s = _clean(s)
    parts = re.split(r"[,\s/|]+", s)
    return [p for p in parts if p]

def parse_socials(text: str, *, last=None, min_score: float = 0.82):
    """
    Returns a dict with a status and payload:
      - {"status":"ok","platforms":[...]}
      - {"status":"clarify","msg": "..."}
      - {"status":"confirm","platforms":[...], "msg":"...", "choices":[...]}
    """
    if not text or not text.strip():
        return {"status":"clarify", "msg":"Which platforms should I target? (e.g., X, Instagram, TikTok)"}

    s = _clean(text)

    # shortcuts
    if any(k in s for k in ALL_KEYWORDS):
        return {"status":"ok", "platforms": list(SUPPORTED.keys())}

    if s in {"same", "same as last time", "same as before", "same as last"}:
        if last:
            return {"status":"ok", "platforms": sorted(set(last))}
        return {"status":"clarify", "msg":"I don't have a previous selection saved. Pick from: X, Instagram, TikTok, Facebook, LinkedIn, YouTube, Pinterest, Reddit."}

    toks = _tokens(text)
    # super-short/noise like "t"
    if len("".join(toks)) <= 1:
        return {"status":"clarify","msg":"That looks like a stray character. Which platforms should I target? (X, Instagram, TikTok, …)"}

    normalized = []
    unknown = []
    suggestions = {}

    candidates = list(ALIAS_LOOKUP.keys())
    for tok in toks:
        if tok in ALIAS_LOOKUP:
            normalized.append(ALIAS_LOOKUP[tok])
            continue
        # fuzzy to catch typos
        match = get_close_matches(tok, candidates, n=1, cutoff=min_score)
        if match:
            normalized.append(ALIAS_LOOKUP[match[0]])
        else:
            unknown.append(tok)
            sug = get_close_matches(tok, candidates, n=3, cutoff=0.6)
            if sug:
                suggestions[tok] = sorted({ALIAS_LOOKUP[s] for s in sug})

    if not normalized:
        return {"status":"clarify",
                "msg":"I didn’t recognize any platform names. Try: X, Instagram, TikTok, Facebook, LinkedIn, YouTube, Pinterest, Reddit."}

    platforms = sorted(set(normalized))

    if unknown:
        # some good, some questionable → ask to confirm with hints
        hint_lines = []
        for bad, suggs in suggestions.items():
            if suggs:
                hint_lines.append(f"‘{bad}’ → did you mean: {', '.join(s.title() for s in suggs)}?")
        msg = "Got: " + ", ".join(p.title() for p in platforms) + ". "
        if hint_lines:
            msg += " ".join(hint_lines)
        msg += " Reply with names or numbers, or say 'all'."
        return {"status":"confirm",
                "platforms": platforms,
                "msg": msg,
                "choices": list(SUPPORTED.keys())}

    return {"status":"ok", "platforms": platforms}

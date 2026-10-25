"""Akruti Dev (Bhaskar, Bela, Yogini) text to Unicode Devanagari.

Akruti Dev is a pre-Unicode font family that puts Devanagari glyphs on Latin
code points; text extracted from documents set in it reads as `Heb®ee³ele` for
पंचायत. No maintained library converts it (PyPI and GitHub, searched October
2026), and the Kruti Dev converters do not apply: the two encodings put
different glyphs on the same bytes. The map in data/akruti.json is built by
hand, one entry per glyph, each with the source word it was read from.

The encoding is visual. A consonant with a vertical stem is its half form plus
the stem byte `e` (`v` न्, `ve` न), so `e` after a stemless glyph is the vowel
sign ा. ि is written before the cluster it follows in speech; the reph after
the syllable it precedes; the nukta before its consonant. to_unicode() maps
bytes to code points, longest match first, then moves those marks.
"""

import json
import re
import unicodedata
from importlib.resources import files

UNKNOWN = "\ufffd"
MARKS = {
    "{pre_i}": "\x01",
    "{pre_i_bindu}": "\x04",
    "{reph}": "\x02",
    "{nukta}": "\x03",
}
PASS = set("0123456789.,-()/:'`\" ")

_MAP = json.loads(
    files("legacy_devanagari").joinpath("data/akruti.json").read_text("utf-8")
)


def _code(value):
    for name, mark in MARKS.items():
        value = value.replace(name, mark)
    return value


TABLE = {
    **{k: _code(v["unicode"]) + "्" for k, v in _MAP["stemmed"].items()},
    **{k + "e": _code(v["unicode"]) for k, v in _MAP["stemmed"].items()},
    **{k: _code(v["unicode"]) for k, v in _MAP["plain"].items()},
    **{k: _code(v["unicode"]) for k, v in _MAP["signs"].items()},
    **{k: _code(v["unicode"]) for k, v in _MAP["special"].items()},
}
LONGEST = max(map(len, TABLE))

# क and फ are drawn in two pieces, k or He then À, with any vowel sign typed
# between them: kegÀ is कु. Moving the signs after À lets keÀ and HeÀ match.
SPLIT_LETTER = re.compile(r"(k|H)e?([gtsw=bB]*)À")

CONSONANT = "[\u0915-\u0939\u0958-\u095f]"
MATRAS = "[\u093e-\u094c\u0901-\u0903\u0962\u0963]"
CLUSTER = f"(?:{CONSONANT}\u093c?\u094d)*{CONSONANT}\u093c?(?:\u094dर)?"
REORDER = [
    (re.compile(MARKS["{nukta}"] + f"({CONSONANT})"), "\\1\u093c"),
    (re.compile(MARKS["{pre_i}"] + f"({CLUSTER})"), "\\1ि"),
    (re.compile(MARKS["{pre_i_bindu}"] + f"({CLUSTER})"), "\\1िं"),
    (re.compile(f"({CLUSTER}{MATRAS}*)" + MARKS["{reph}"]), "र्\\1"),
    # the anusvara or candrabindu typed before its vowel sign: कंा is कां
    (re.compile("([\u0901\u0902])([\u093e-\u094c])"), "\\2\\1"),
]
VOWELS = {"अा": "आ", "अो": "ओ", "अौ": "औ", "आे": "ओ", "आै": "औ"}


def _lookup(text):
    out, i = [], 0
    while i < len(text):
        for size in range(min(LONGEST, len(text) - i), 0, -1):
            piece = text[i : i + size]
            if piece in TABLE:
                out.append(TABLE[piece])
                i += size
                break
        else:
            char = text[i]
            out.append(char if char in PASS or char.isspace() else UNKNOWN)
            i += 1
    return "".join(out)


def to_unicode(text):
    """Unicode Devanagari for Akruti text.

    A byte the map does not cover, and a mark left with nothing to attach to,
    become U+FFFD, so a failed reading is visible rather than plausible.
    """
    if not text:
        return text
    out = _lookup(SPLIT_LETTER.sub(r"\1eÀ\2", text))
    for pattern, replacement in REORDER:
        out = pattern.sub(replacement, out)
    for old, new in VOWELS.items():
        out = out.replace(old, new)
    for mark in MARKS.values():
        out = out.replace(mark, UNKNOWN)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", out).strip())


def unmapped(text):
    """The bytes of `text` that the map does not cover."""
    known = {char for key in TABLE for char in key}
    return {c for c in text if c not in PASS and not c.isspace()} - known

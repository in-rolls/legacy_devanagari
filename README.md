# legacy_devanagari

Convert text set in pre-Unicode Devanagari font encodings to Unicode.
Government documents from the 1990s and 2000s were typeset in fonts that put
Devanagari glyphs on Latin code points, so the text you extract from them reads
as Latin noise. This package turns it back into Devanagari.

It covers one encoding so far: **Akruti Dev** (AkrutiDevBhaskar,
AkrutiDevBela, AkrutiDevYogini, which share one layout). Kruti Dev is meant to
join it.

## Install

    pip install git+https://github.com/in-rolls/legacy_devanagari

No runtime dependencies; Python 3.12+.

## Use

```python
from legacy_devanagari import akruti_to_unicode

akruti_to_unicode("ef$emlejer³e Heb®ee³ele efveJee&®eve, 2001")
# 'त्रिस्तरीय पंचायत निर्वाचन, 2001'
akruti_to_unicode("Þeer efJepe³e kegÀceej ³eeoJe")
# 'श्री विजय कुमार यादव'
akruti_to_unicode("Mewuesvê Òemeeo eEmen")
# 'शैलेन्द्र प्रसाद सिंह'
akruti_to_unicode("Heùe")
# 'प�ा' - a byte the map does not cover stays visible as U+FFFD
```

`legacy_devanagari.akruti.unmapped(text)` lists the bytes of `text` the map
does not cover, so you can find them before trusting a conversion.

Extract text in the order the PDF stores it. Akruti draws ि before its
consonant and the reph after its syllable, and a reader that sorts glyphs by x
position splits words at those marks. With pdfplumber, join `page.chars` in
their stored order.

## How it works

The encoding is visual, so conversion is a lookup followed by reordering.

- A consonant with a vertical stem is its half form plus the stem byte `e`:
  `v` is न्, `ve` is न. After a stemless glyph, `e` is the vowel sign ा
  (`je` is रा).
- ि (`ef`) is typed before the cluster it follows in speech, the reph (`&`)
  after the syllable it precedes, and the nukta (`æ`) before its consonant.
  `to_unicode()` maps bytes, longest match first, then moves these marks.
- क and फ are drawn in two pieces (`k`…`À`, `He`…`À`) with any vowel sign
  typed between them; `kegÀ` is कु.

## How the map was derived and checked

No maintained library covered Akruti (PyPI and GitHub, searched October 2026),
and the Kruti Dev converters do not apply: the two encodings put different
glyphs on the same bytes. So the map in
[`src/legacy_devanagari/data/akruti.json`](src/legacy_devanagari/data/akruti.json)
was built by hand from one corpus, the Bihar State Election Commission's 2001
lists of elected mukhiyas (8,426 panchayats, saved from the Internet Archive's
captures of sec.bih.nic.in). Every entry records the source word it was read
from and that word's Unicode spelling, taken from the lists' printed headings
or from the same panchayats in the SEC's 2006 workbooks, which are in Kruti
Dev and decode independently.

Two checks that share no code with the map:

- **OCR.** 330 panchayat-name cells sampled at random, rendered at 300 dpi and
  read with Tesseract (`hin`): character error rate 1.2%, 92.4% identical,
  98.8% within one character. The remaining disagreements are OCR errors (घ
  for ध, छ for ड, औ for श्री). An earlier round showed OCR and the 2006
  spellings both reading `ª` as रू where the map had रु; the map was corrected.
- **The 2006 spelling of the same places.** Of 8,094 panchayats in districts
  with a 2006 workbook, 57.5% match a 2006 name exactly and 82.3% have a 2006
  name with similarity at least 0.8. The rest are the SEC spelling a place
  differently five years apart (`सबलपुर`/`सब्बलपुर`, `प0`/`प.`) or panchayats
  missing from the 2006 workbook.

Bytes seen three times or fewer without a word to pin them (`ù`, `R`, `z`,
`Q`) are left unmapped and come out as U+FFFD.

## Develop

    make sync    # uv sync --frozen --group dev
    make check   # ruff + pytest

## License

MIT

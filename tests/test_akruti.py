"""Akruti words from the Bihar SEC's 2001 lists, against their known spellings."""

import json
from importlib.resources import files

import pytest

from legacy_devanagari.akruti import UNKNOWN, to_unicode, unmapped

WORDS = [
    # headings printed on every list
    ("ef$emlejer³e Heb®ee³ele efveJee&®eve, 2001", "त्रिस्तरीय पंचायत निर्वाचन, 2001"),
    ("efveJee&ef®ele cegefKe³ee keÀer met®eer", "निर्वाचित मुखिया की सूची"),
    ("Òeceb[ue - Heìvee", "प्रमंडल - पटना"),
    # panchayat names, as spelled in the SEC's 2006 workbooks
    ("vekeÀìe efo³eeje", "नकटा दियारा"),
    ("HeefM®eceer oerIee", "पश्चिमी दीघा"),
    ("HetJeer& cewveHegje", "पूर्वी मैनपुरा"),
    ("HeÀlesnHegj", "फतेहपुर"),
    ("peceeuegÎerve®ekeÀ", "जमालुद्दीनचक"),
    ("DeefKle³eejHegj", "अख्तियारपुर"),
    ("mesunewjer yesunewjer", "सेल्हौरी बेल्हौरी"),
    ("YeeueeHeÆer", "भालापट्टी"),
    ("meªDee", "सरूआ"),
    ("yeÏ¿eHegj HetJeer&", "ब्रह्मपुर पूर्वी"),
    ("MesjHegj HetJeea", "शेरपुर पूर्वी"),
    # names of the elected
    ("Þeer efJepe³e kegÀceej ³eeoJe", "श्री विजय कुमार यादव"),
    ("efMeJe MebkeÀj Mecee&", "शिव शंकर शर्मा"),
    ("Oecexvê", "धर्मेन्द्र"),
    ("Mewuesvê Òemeeo eEmen", "शैलेन्द्र प्रसाद सिंह"),
    ("ke=À<Ce ceesnve þekegÀj", "कृष्ण मोहन ठाकुर"),
    ("ye´ïeosJe Pee", "ब्रह्मदेव झा"),
    ("$eÝef<ekesÀMe ceC[ue", "ऋषिकेश मण्डल"),
    ("ceespeHeÌHeÀj Fceece", "मोजफ्फर इमाम"),
    ("meeq®®eoevevo ®eewOejer", "सच्चिदानन्द चौधरी"),
    ("Ëo³e He´keÀeMe Jecee&", "हृदय प्रकाश वर्मा"),
    ("cees0 DepeejÀue nkeÀ", "मो0 अजारुल हक"),
]


@pytest.mark.parametrize(("akruti", "unicode"), WORDS)
def test_known_words(akruti, unicode):
    assert to_unicode(akruti) == unicode


def test_an_unmapped_byte_is_visible():
    assert UNKNOWN in to_unicode("Heùe")
    assert unmapped("Heùe") == {"ù"}


def test_a_stray_mark_is_visible():
    # ि with no consonant after it cannot be placed
    assert to_unicode("ef") == UNKNOWN


def test_every_entry_names_its_evidence():
    table = json.loads(
        files("legacy_devanagari").joinpath("data/akruti.json").read_text("utf-8")
    )
    for kind in ("stemmed", "plain", "signs", "special"):
        for key, entry in table[kind].items():
            assert entry["evidence"], (kind, key)

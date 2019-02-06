
"""Grep statistics from text."""

import enchant


def is_of_lang(lang, filter_text=None, percentage=0.5):
    """Return if the text is of this language."""
    filter_text = filter_text or (lambda x: True)
    if lang:
        d = enchant.Dict(lang)

    def f(text):
        if not lang:
            return True
        if not text:
            return False
        words = [w for w in text.split(' ') if w != '' and filter_text(w)]
        return [
            d.check(w) for w in words
        ].count(True) > (len(words) * percentage)

    return f


def parse_humanized_int(text):
    """Convert numbers as 1.5K to 1500."""
    mult = 1
    if text.endswith('K'):
        mult = 1000
        text = text[:-1]
    if text.endswith('M'):
        mult = 1000000
        text = text[:-1]
    if text.endswith('G'):
        mult = 1000000000
        text = text[:-1]
    return int(float(text) * mult)

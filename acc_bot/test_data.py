"""
Test data loaders. The module uses random data generator
with fixed state for reproducible tests.
"""

import datetime
import random
import gettext

gettext.install("bot", os.path.dirname(__file__), names=("ngettext",))
# try :
#     translation = gettext.translation('bot', 'po')
#     _ = translation.gettext
#     ngettext = translation.ngettext
# except : # pylint: disable=bare-except
#     _ = lambda x : x

random.seed(a=42)
fix_state = random.getstate()

CATEGORIES_FLAT = [
    _('restaurants'), _('transport'), _('supermarkets'),
    _('pharmacy'), _('entertainment'), _('other')
]


def load_test_data_1() -> dict:
    """Generates test data with 1 week span"""
    samples_numb = 100

    span = datetime.timedelta(days=6, hours=23)
    date_initial = datetime.datetime.now() - span
    res = {}
    random.setstate(fix_state)
    costs = [random.randint(5, 2000) for _ in range(samples_numb)]
    for i in range(samples_numb):
        res[date_initial + (span / samples_numb) * i] = \
            (CATEGORIES_FLAT[i % len(CATEGORIES_FLAT)], costs[i])

    return res


def load_test_data_2() -> dict:
    """Generates test data with several weeks span"""
    samples_numb = 1000

    # 8 week span
    span = datetime.timedelta(days=8*7)
    date_initial = datetime.datetime.now() - span
    res = {}
    random.setstate(fix_state)
    costs = [random.randint(5, 2000) for _ in range(samples_numb)]
    for i in range(samples_numb):
        res[date_initial + (span / samples_numb) * i] = \
            (CATEGORIES_FLAT[i % len(CATEGORIES_FLAT)], costs[i])

    return res

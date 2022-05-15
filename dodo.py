"""
"""

from argparse import Action
import glob

def task_html() :
    """Make HTML doumentation."""
    return {
        'actions' : ['sphinx-build acc_bot/docs/source _build'],
        'file_dep' : glob.glob("*.py") + glob.glob("*.rst"),
        'targets' : ['_build/index.html']
    }

def task_test() :
    """Test module."""
    return {
        'actions' : ['coverage run -m unittest acc_bot/test_util.py'],
        'targets' : ['.coverage']
    }

def task_coverage() :
    """Produce HTML coverage table"""
    return {
        'actions' : ['coverage html'],
        'task_dep' : ['test'],
        'targets' : ['htmlcov/index.html']
    }

def task_gen_locale() :
    """Generate translation."""
    return {
        'actions' : [
            'pybabel compile -D bot -d acc_bot/po -l en',
            'pybabel compile -D bot -d acc_bot/po -l ru'
        ],
        'targets' : [
            'acc_bot/po/ru/LC_MESSAGES/bot.po',
            'acc_bot/po/en/LC_MESSAGES/bot.po'
        ]
    }

def task_build_whl() :
    """Generate distributable"""
    return {
        'actions' : ['python -m build'],
        'task_dep' : ['gen_locale']
    }
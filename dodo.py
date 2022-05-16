"""
Dafault: create wheel
"""

import glob
from doit.tools import create_folder


def task_html() :
    """Make HTML doumentation."""
    return {
        'actions' : ['sphinx-build acc_bot/docs/source _build'],
        'file_dep' : glob.glob("*.py") + glob.glob("*.rst"),
        'targets' : ['_build/index.html']
    }

def task_test():
    """Preform tests."""
    yield {'actions': ['coverage run -m unittest -v'], 'name': "run"}
    yield {'actions': ['coverage report'], 'verbosity': 2, 'name': "report"}


def task_coverage() :
    """Produce HTML coverage table"""
    return {
        'actions' : ['coverage html'],
        'task_dep' : ['test'],
        'targets' : ['htmlcov/index.html']
    }


def task_pot():
    """Re-create .pot ."""
    return {
            'actions': ['pybabel extract -o acc_bot/po/bot.pot acc_bot'],
            'file_dep': glob.glob('acc_bot/*.py'),
            'targets': ['po/bot.pot'],
           }


def task_po():
    """Update translations."""
    return {
            'actions': ['pybabel update -D bot -d acc_bot/po -i acc_bot/po/bot.pot'],
            'file_dep': ['acc_bot/po/bot.pot'],
            'targets': ['acc_bot/po/ru/LC_MESSAGES/bot.po'],
            'task_dep' : ['pot']
           }


def task_mo():
    """Compile translations."""
    return {
            'actions': [
                (create_folder, ['acc_bot/ru/LC_MESSAGES']),
                'pybabel compile -D bot -l ru -i acc_bot/po/ru/LC_MESSAGES/bot.po -d acc_bot',
                (create_folder, ['acc_bot/en/LC_MESSAGES']),
                'pybabel compile -D bot -l en -i acc_bot/po/en/LC_MESSAGES/bot.po -d acc_bot',
                       ],
            'file_dep': ['acc_bot/po/ru/LC_MESSAGES/bot.po'],
            'targets': ['acc_bot/ru/LC_MESSAGES/bot.mo', 'acc_bot/en/LC_MESSAGES/bot.mo'],
            'task_dep' : ['po']
           }




def task_sdist():
    """Create source distribution."""
    return {
            'actions': ['python -m build -s'],
            'task_dep': ['gitclean'],
           }


def task_wheel():
    """Create binary wheel distribution."""
    return {
            'actions': ['python -m build -w'],
            'task_dep': ['mo'],
           }


def task_app():
    """Run application."""
    return {
            'actions': ['python -m AppBase'],
            'task_dep': ['mo'],
           }





# def task_gen_locale() :
#     """Generate translation."""
#     return {
#         'actions' : [
#             'pybabel compile -D bot -d acc_bot/po -l en',
#             'pybabel compile -D bot -d acc_bot/po -l ru'
#         ],
#         'targets' : [
#             'acc_bot/po/ru/LC_MESSAGES/bot.po',
#             'acc_bot/po/en/LC_MESSAGES/bot.po'
#         ]
#     }

# def task_build_whl() :
#     """Generate distributable"""
#     return {
#         'actions' : ['python -m build'],
#         'task_dep' : ['gen_locale']
#     }

def task_gitclean():
    """Clean all generated files not tracked by GIT."""
    return {
            'actions': ['git clean -xdf'],
           }


def task_style():
    """Check style against flake8."""
    return {
            'actions': ['flake8 acc_bot']
           }


def task_docstyle():
    """Check docstrings against pydocstyle."""
    return {
            'actions': ['pydocstyle acc_bot']
           }


def task_check():
    """Perform all checks."""
    return {
            'actions': None,
            'task_dep': ['style', 'docstyle', 'test']
           }

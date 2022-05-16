"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
"""

import sys
import os
import datetime
import gettext
import locale

from telegram import (
    Update,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    CallbackContext,
)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


from acc_bot.util import (  # noqa: E402
    accumulate_by_span,
    check_limit,
    gater_week,
    make_spending_prediction,
    make_pie
)
from acc_bot.test_data import load_test_data_1, load_test_data_2  # noqa: E402

gettext.install("bot", os.path.dirname(__file__), names=("ngettext",))

CATEGORIES = [
    [_('restaurants'), _('transport')],
    [_('supermarkets'), _('pharmacy')],
    [_('entertainment'), _('other')]
]
CATEGORIES_FLAT = [
    _('restaurants'), _('transport'), _('supermarkets'),
    _('pharmacy'), _('entertainment'), _('other')
]
CATEGORIES_FILTER = Filters.regex('^' + '|'.join(CATEGORIES_FLAT) + '$')
NUMBERS_FILTER = Filters.regex('^[0-9]+$')
AGGRESSION_LEVEL = [
    _('Sorry, I dont understand.'),
    _('I dont understand🧐'),
    _('I dont understand!🤬'),
    _('STOP!✋')
]


def reset_context(context: dict) -> None:
    """Reset context of a specific user."""
    context.pop('to_add', None)
    if 'data' not in context:
        context['data'] = {}
    if 'limits' not in context:
        context['limits'] = {}
    context['aggression_lvl'] = 0
    context['context'] = 'free'


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    reset_context(context.user_data)
    welcome_txt = _('Hey! Im an accountant bot.\nIll help u managing ur finances!')
    update.message.reply_text(text=welcome_txt)


def unknown_cmd(update: Update, context: CallbackContext) -> None:
    """Reply to an unknown command."""
    reset_context(context.user_data)
    update.message.reply_text(_('Unknown cmd 🥵'))


def dont_understand(update: Update, context: CallbackContext) -> None:
    """Reply to meaningless input. Supports different levels of annoyance."""
    if context.user_data['context'] == 'free':
        update.message.reply_text(
            AGGRESSION_LEVEL[min(
                len(AGGRESSION_LEVEL) - 1,
                context.user_data['aggression_lvl']
            )]
        )
        context.user_data['aggression_lvl'] += 1
        return
    reset_context(context.user_data)
    update.message.reply_text(_('Wrong input'))
    return


def add(update: Update, context: CallbackContext) -> None:
    """Handle add spending scenario. Switches the context & provides interactive keyboard."""
    reset_context(context.user_data)
    context.user_data['context'] = 'cat_chooser_add'
    update.message.reply_text(
        text=_('Please, choose category:'),
        reply_markup=ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True)
    )


def set_limit(update: Update, context: CallbackContext) -> None:
    """Handle set limit scenario. Switches the context & provides interactive keyboard."""
    reset_context(context.user_data)
    context.user_data['context'] = 'cat_chooser_lim'
    update.message.reply_text(
        text=_('Please, choose category:'),
        reply_markup=ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True)
    )


def category_chooser(update: Update, context: CallbackContext) -> None:
    """Interactive keyboard input handler. Saves chosen result and switches the context."""
    if context.user_data['context'] != 'cat_chooser_add' and \
            context.user_data['context'] != 'cat_chooser_lim':
        reset_context(context.user_data)
        update.message.reply_text(_('Wrong input'))
        return

    context.user_data['curr_category'] = update.message.text

    rep_txt = ''
    if context.user_data['context'] == 'cat_chooser_lim':
        context.user_data['context'] = 'cat_upd_lim'
        rep_txt = _('Type new limit')
    else:
        context.user_data['context'] = 'cat_upd_add'
        rep_txt = _('Type the amount spent')

    update.message.reply_text(rep_txt)


def category_upd(update: Update, context: CallbackContext) -> None:
    """Handle 'add category spending' and 'set category limit' scanarios.

    Saves the result to 'context.user_data' and replies with success message.
    Resets the context.
    """
    if context.user_data['context'] != 'cat_upd_add' and \
            context.user_data['context'] != 'cat_upd_lim':
        reset_context(context.user_data)
        update.message.reply_text(_('Wrong input'))
        return

    rep_txt = ''
    cat = context.user_data['curr_category']
    val = int(update.message.text)

    if context.user_data['context'] == 'cat_upd_add':
        if 'data' not in context.user_data:
            context.user_data['data'] = {}
        cur_time = datetime.datetime.now()
        context.user_data['data'][cur_time] = (cat, val)
        rep_txt = _('Category {} was updated!').format(cat)
        # Check if exceeds limit
        cat_spent, cat_lim = check_limit(context.user_data, cat)
        if cat_lim:
            if cat_spent > cat_lim:
                rep_txt += _('\nYouve exceeded your weekly limit for the category {} 😱').format(cat_lim)
            else:
                rep_txt += _('\nYouve already spent {} of you limit {} for this week').format(cat_spent, cat_lim)
    else:
        if 'limits' not in context.user_data:
            context.user_data['limits'] = {}
        context.user_data['limits'][cat] = val
        rep_txt = _('Limit for {} category was updated!').format(cat)

    update.message.reply_text(rep_txt)
    reset_context(context.user_data)


def week(update: Update, context: CallbackContext) -> None:
    """Show the user spendings for the last week."""
    reset_context(context.user_data)

    if 'data' not in context.user_data or len(context.user_data['data']) == 0:
        update.message.reply_text(_('You havent spent any money this week 😢'))
        return

    week_spendings = gater_week(context.user_data['data'])
    total = 0
    for val in week_spendings.values():
        total += val

    if not total:
        update.message.reply_text(_('You havent spent any money this week 😢'))
        return

    res_msg = _('Wow!🤩 Heres your top spenings of this week:\n\n')
    for num, item in enumerate(sorted(week_spendings.items(), key=lambda x: -x[1])):
        res_msg += f'{num+1}. {item[0]}: {item[1]}\n'
    res_msg += _('\nAnd the total is: {} moneys!💸').format(total)
    res_msg += ngettext('\nOnly {} category present',
                        '\n{} categories present!', len(week_spendings)).format(len(week_spendings))
    update.message.reply_text(res_msg)


def weeks(update: Update, context: CallbackContext) -> None:
    """Collect spending statistics throughout the whole history."""
    reset_context(context.user_data)

    if 'data' not in context.user_data or len(context.user_data['data']) == 0:
        update.message.reply_text(_('You havent spent any money this week 😢'))
        return

    week_totals = accumulate_by_span(context.user_data['data'], datetime.timedelta(days=7))

    if len(week_totals) < 2:
        update.message.reply_text(_('Too few data 😔'))
        return

    res_msg = _('Your week totals:\n\n')
    for i in reversed(week_totals):
        res_msg += f' - {i}\n'

    res_msg += _('\nBy the way, we predict you to spend {} next week!').format(
        make_spending_prediction(context.user_data['data']))
    update.message.reply_text(res_msg[:-1])


def chart(update: Update, context: CallbackContext) -> None:
    """Plot a pie char with weekly spendings."""
    make_pie(context.user_data['data'])
    with open('tmp.png', 'rb') as photo:
        update.message.reply_photo(photo=photo)
    os.remove('tmp.png')


def bot_help(update: Update, context: CallbackContext) -> None:
    """Reply with the help message."""
    reset_context(context.user_data)
    help_msg = _("This is a help message\n")
    help_msg += _("/add - add spending for specific category.\n")
    help_msg += _("/set_limit - set the limit for the category.\n")
    help_msg += _("/week show stats for the last week.\n")
    help_msg += _("/weeks show accumulated stats for the whole history.")
    update.message.reply_text(help_msg)


def load_test_1(update: Update, context: CallbackContext) -> None:
    """Load prepared testing data to context.user_data['data']."""
    reset_context(context.user_data)
    context.user_data['data'] = load_test_data_1()
    update.message.reply_text('Test data 1 loaded')


def load_test_2(update: Update, context: CallbackContext) -> None:
    """Load prepared testing data to context.user_data['data']."""
    reset_context(context.user_data)
    context.user_data['data'] = load_test_data_2()
    update.message.reply_text('Test data 2 loaded')


def main():
    """Call main application."""
    locale.setlocale(locale.LC_ALL, locale.getdefaultlocale())

    token = input(_("Please, provide telegram-bot token or left blank to use default:\n"))
    default_token = '5337419761:AAFahgNMGQNpzyRvFFlS3_N_-9DyfNB5bfQ'
    updater = Updater(token=token if token else default_token, use_context=True)
    dispatcher = updater.dispatcher
    print(_('The bot is ready!'))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('add', add))
    dispatcher.add_handler(CommandHandler('set_limit', set_limit))
    dispatcher.add_handler(CommandHandler('help', bot_help))
    dispatcher.add_handler(CommandHandler('week', week))
    dispatcher.add_handler(CommandHandler('weeks', weeks))
    dispatcher.add_handler(CommandHandler('chart', chart))
    dispatcher.add_handler(CommandHandler('load_test_1', load_test_1))
    dispatcher.add_handler(CommandHandler('load_test_2', load_test_2))
    dispatcher.add_handler(MessageHandler(CATEGORIES_FILTER, category_chooser))
    dispatcher.add_handler(MessageHandler(NUMBERS_FILTER, category_upd))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_cmd))
    dispatcher.add_handler(MessageHandler(Filters.text, dont_understand))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

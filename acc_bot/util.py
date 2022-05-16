"""Module implements a number of tools used all across the project."""


import datetime
import subprocess
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns


def accumulate_by_span(data: dict, span: datetime.timedelta) -> list:
    """Gater data(spendings) grouped by aforementioned time span."""
    res = []
    date_initial = datetime.datetime.now()
    tmp = sorted(data.items(), key=lambda x: x[0])
    for item in reversed(tmp):
        while date_initial > item[0]:
            res.append(0)
            date_initial -= span
        res[-1] += item[1][1]

    return res[::-1]


def gater_week(data: dict) -> dict[str, int]:
    """Gater categorial data(spendings) for the last week."""
    date_initial = datetime.datetime.now() - datetime.timedelta(days=7)
    week_spendings = {}
    for key, val in data.items():
        if key >= date_initial:
            if val[0] not in week_spendings:
                week_spendings[val[0]] = 0
            week_spendings[val[0]] += val[1]
    return week_spendings


def check_limit(data: dict, category: str) -> tuple[int, int]:
    """Check if category spendings for the last week exceeds the limit."""
    week_spendings = gater_week(data['data'])
    cat_lim = data['limits'].get(category, 0)
    cat_spent = week_spendings.get(category, 0)
    return (cat_spent, cat_lim)


def make_spending_prediction(data: dict) -> int:
    """Make spending prediction based on avalible data."""
    res = accumulate_by_span(data, datetime.timedelta(days=7))
    if len(res) == 0:
        return -1
    x_data = np.c_[np.ones(len(res), dtype=np.float32), np.arange(len(res))]
    y_data = np.c_[np.array(res)]
    w_matr = np.linalg.inv(x_data.T@x_data)@x_data.T@y_data
    return int((np.array([1, len(res)])@w_matr)[0])


def make_pie(data: dict) -> None:
    """Plot pie chart of weekly spendings."""
    res = gater_week(data)
    data, labels = [*res.values()], [*res.keys()]
    # colors = sns.color_palette('pastel')[0:5]
    # plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')
    # plt.savefig('tmp.png')
    cmd = ["python"]
    cmd.append("-c")
    cmd.append("\"import matplotlib.pyplot as plt\n import seaborn as sns\n")
    cmd[-1] += "colors = sns.color_palette('pastel')[0:5]\n"
    cmd[-1] += f"data = {data}\n"
    cmd[-1] += f"labels = {labels}\n"
    cmd[-1] += "plt.pie(data, labels = labels, colors = colors, autopct='%.0f%%')\n"
    cmd[-1] += "plt.savefig('tmp.png')\""
    subprocess.run(cmd, check=True)

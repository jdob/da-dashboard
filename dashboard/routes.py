import os

from flask import current_app as app
from flask import render_template, request
from trello import TrelloClient

from .data import DashboardData


ENV_API_KEY = 'API_KEY'
ENV_API_SECRET = 'API_SECRET'
ENV_TOKEN = 'TOKEN'


@app.route('/', methods=('GET',))
def in_progress():
    dd = _load_data()
    in_progress_cards = dd.in_progress_cards()
    return render_template('in_progress.html', cards=in_progress_cards)


@app.route('/done', methods=('GET',))
def done():
    dd = _load_data()
    done_cards = dd.done_cards()
    return render_template('done.html', cards=done_cards)


@app.route('/soon', methods=('GET',))
def soon():
    dd = _load_data()
    soon_cards = dd.coming_soon_cards()
    return render_template('soon.html', cards=soon_cards)


@app.route('/activity', methods=('GET', ))
def activity():
    dd = _load_data()
    cards_by_label = dd.ongoing_activities()
    return render_template('activity.html', cards=cards_by_label)


@app.route('/products', methods=('GET', ))
def products():
    dd = _load_data()
    cards_by_label = dd.ongoing_products()
    return render_template('products.html', cards=cards_by_label)


@app.route('/epics', methods=('GET',))
def epics():
    dd = _load_data()
    cards_by_epic = dd.epics()
    return render_template('epics.html', cards=cards_by_epic)


@app.route('/month', methods=('GET',))
def month():
    dd = _load_data()

    month_list_id = request.args.get('month', None)
    if month_list_id:
        cards = dd.month_highlights(month_list_id)
        if request.args.get('text', None):
            return render_template('highlights_text.html', cards=cards)
        else:
            return render_template('highlights.html', cards=cards, list_id=month_list_id)
    else:
        month_list = dd.month_list()
        return render_template('month_list.html', months=month_list)


def _load_data() -> DashboardData:
    # Load Trello credentials from environment and create client
    api_key = os.environ.get(ENV_API_KEY)
    api_secret = os.environ.get(ENV_API_SECRET)
    token = os.environ.get(ENV_TOKEN)

    client = TrelloClient(api_key=api_key, api_secret=api_secret, token=token)
    dd = DashboardData()
    dd.load(client)

    return dd
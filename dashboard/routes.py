import os

from flask import current_app as app
from flask import render_template
from trello import TrelloClient

from .data import DashboardData


ENV_API_KEY = 'API_KEY'
ENV_API_SECRET = 'API_SECRET'
ENV_TOKEN = 'TOKEN'


@app.route('/', methods=('GET',))
def in_progress():
    dd = _load_data()
    in_progress_cards = dd.in_progress_cards()
    return render_template('index.html', cards=in_progress_cards)


@app.route('/done', methods=('GET',))
def done():
    dd = _load_data()
    done_cards = dd.done_cards()
    return render_template('done.html', cards=done_cards)


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


def _load_data() -> DashboardData:
    # Load Trello credentials from environment and create client
    api_key = os.environ.get(ENV_API_KEY)
    api_secret = os.environ.get(ENV_API_SECRET)
    token = os.environ.get(ENV_TOKEN)

    client = TrelloClient(api_key=api_key, api_secret=api_secret, token=token)
    dd = DashboardData()
    dd.load(client)

    return dd
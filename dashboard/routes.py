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


@app.route('/in-progress-activity', methods=('GET', ))
def in_progress_activity():
    dd = _load_data()
    cards_by_label = dd.in_progress_activities()
    return render_template('activity.html', cards=cards_by_label)


@app.route('/in-progress-products', methods=('GET', ))
def in_progress_products():
    dd = _load_data()
    cards_by_label = dd.in_progress_products()
    return render_template('products.html', cards=cards_by_label)


@app.route('/in-progress-epics', methods=('GET',))
def in_progress_epics():
    dd = _load_data()
    cards_by_epic = dd.in_progress_epics()
    return render_template('epics.html', cards=cards_by_epic)


@app.route('/in-progress-team', methods=('GET', ))
def in_progress_team():
    dd = _load_data()
    cards_by_member = dd.in_progress_team()
    return render_template('team.html', cards=cards_by_member)


@app.route('/backlog', methods=('GET',))
def backlog():
    dd = _load_data()
    backlog_cards = dd.backlog_cards()
    return render_template('in_progress.html', cards=backlog_cards)


@app.route('/backlog-activity', methods=('GET', ))
def backlog_activity():
    dd = _load_data()
    cards_by_label = dd.backlog_activities()
    return render_template('activity.html', cards=cards_by_label)


@app.route('/backlog-products', methods=('GET', ))
def backlog_products():
    dd = _load_data()
    cards_by_label = dd.backlog_products()
    return render_template('products.html', cards=cards_by_label)


@app.route('/backlog-epics', methods=('GET',))
def backlog_epics():
    dd = _load_data()
    cards_by_epic = dd.backlog_epics()
    return render_template('epics.html', cards=cards_by_epic)


@app.route('/backlog-team', methods=('GET', ))
def backlog_team():
    dd = _load_data()
    cards_by_member = dd.backlog_team()
    return render_template('team.html', cards=cards_by_member)


@app.route('/upcoming-events', methods=('GET', ))
def upcoming_events():
    dd = _load_data()
    cards = dd.upcoming_events_cards()
    return render_template('events.html', cards=cards)


@app.route('/all-attendees', methods=('GET', ))
def attendees():
    dd = _load_data()
    month_cards, month_data = dd.all_attendees()
    return render_template('attendees.html', cards=month_cards, data=month_data)


@app.route('/customer-engagements', methods=('GET', ))
def customer_engagements():
    dd = _load_data()
    month_cards, month_data = dd.customer_attendees()
    return render_template('attendees.html', cards=month_cards, data=month_data)


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
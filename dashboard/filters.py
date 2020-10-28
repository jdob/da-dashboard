from flask import current_app as app


@app.template_filter()
def type_style(s):
    formatted = s.replace(',', '').replace(' & ', '').replace(' ', '-').lower()
    return formatted

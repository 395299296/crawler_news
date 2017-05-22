from flask import render_template

def handle_unmatchable(*args, **kwargs):
    return 'unmatchable page', 404

def page_not_found(e):
    data = get_base_data()
    return '404 page', 404

def handle_bad_request(e):
    return 'bad request!', 400


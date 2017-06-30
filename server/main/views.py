from flask import request, redirect, render_template, url_for, abort, flash, g, session, jsonify
from .models import Models
import json

def get_base_data():
    data = {}
    return data

def index():
    data = get_base_data()
    data['items'] = Models().get_data()
    return render_template('index.html', **data)

def show_more():
    data = json.loads(request.form.get('data'))
    items = Models().get_data(data['index'])
    return jsonify(items)

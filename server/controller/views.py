from flask import request, redirect, render_template, url_for, abort, flash, g, session

def index():
    return render_template('index.htm')

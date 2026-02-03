from flask import render_template
from flask_login import login_required
from app import app

@app.route('/billing/gst-invoice')
@login_required
def gst_invoice():
    return render_template('billing/gst_invoice.html')

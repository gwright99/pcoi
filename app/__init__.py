from flask import Flask
import os

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.debug = True
app.static_folder = os.path.abspath("app/templates/static")
app.pdf_folder = os.path.abspath("app/templates/static/pdf")

from app import routes
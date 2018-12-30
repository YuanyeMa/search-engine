"""
 the flask application package
 搜索引擎的web展示
"""
from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

from . import views

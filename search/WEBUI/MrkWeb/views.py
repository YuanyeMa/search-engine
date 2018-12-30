"""
路由和视图
"""
from flask import render_template, request
from . import app
import search.search as search

TITLE = "信息检索大作业——搜索引擎"


@app.route('/')
def index():
    """封面搜索页"""
    return render_template('index.html', title=TITLE)


@app.route('/result', methods=['GET'])
def result():
    """搜索结果页"""
    keyword = request.args.get('keyword')
    url_list = search.run(str(keyword))
    return render_template('result.html', title=TITLE, list=url_list)

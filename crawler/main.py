from rio_grande_do_sul_scripts import Scripts_RS
from flask import jsonify, make_response

def crawl_rs(request):
    Scripts_RS().run()
    return jsonify({'Done': True}), 200
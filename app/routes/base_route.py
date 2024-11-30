from flask import Flask, render_template, Blueprint
import os
from ..forms import UrlSubmit
from ..content_processor import ContentProcessor

bp = Blueprint('base', __name__)


@bp.route('/',methods=['GET','POST'])
def base():
    form = UrlSubmit()
    result = None

    if form.validate_on_submit():
        try:
            processor = ContentProcessor()
            result = processor.process_url(form.url.data)
        except Exception as e:
            result = {
                "status":"error",
                "message": f"An error occured: {str(e)}"
            }

    return render_template('index.html', form=form, result=result)
    

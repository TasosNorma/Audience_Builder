from flask import Flask, render_template, Blueprint, redirect, flash, url_for
import os
from ..forms import UrlSubmit, PromptForm
from ..content_processor import ContentProcessor
from ..database.database import SessionLocal
from ..database.models import Prompt

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


@bp.route('/prompts', methods =['GET','POST'])
def prompts():
    db = SessionLocal()
    prompt = db.query(Prompt).filter(Prompt.id == 1).first()

    # Create a prompt object that will be placed inside the form for a placeholder in order to showcase only the relevant parts of the prompt
    modified_prompt = prompt
    parts = modified_prompt.template.split("{content}")
    editable_template = parts[1] if len(parts) >1 else ''
    modified_prompt.template = editable_template

    if modified_prompt:
        form = PromptForm(obj=modified_prompt)
    else:
        form = PromptForm(obj=prompt)

    # Change the name and the template of the prompt
    if form.validate_on_submit():
        try:
            prompt.name = form.name.data
            new_template = f"Using the following content: \n\n {{content}} \n\n {form.template.data.strip()}"
            print(f"New template = {new_template}")
            prompt.template = f"Using the following content: \n\n {{content}} \n\n {form.template.data.strip()}"
            db.commit()
            print(f"Prompt template : {prompt.template}")
            flash('Prompt updated successfully', 'success')
            return redirect(url_for('base.prompts'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating prompt {str(e)}','error')
    
    db.close()
    return render_template('prompts.html', form=form)
    

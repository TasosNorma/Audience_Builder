from flask import Flask, render_template, Blueprint, redirect, flash, url_for
import os
from ..forms import UrlSubmit, PromptForm, ProfileForm
from ..content_processor import ContentProcessor
from ..database.database import SessionLocal
from ..database.models import Prompt, Profile

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
    parts = modified_prompt.template.split("### Suffix_")
    editable_template = parts[0] if len(parts) >1 else ''
    modified_prompt.template = editable_template

    if modified_prompt:
        form = PromptForm(obj=modified_prompt)
    else:
        form = PromptForm(obj=prompt)

    # Change the name and the template of the prompt
    if form.validate_on_submit():
        try:
            prompt.name = form.name.data
            prompt.template = f"{form.template.data.strip()} \n ### Suffix_ {parts[1]}"
            db.commit()
            print(f"Prompt template : {prompt.template}")
            flash('Prompt updated successfully', 'success')
            return redirect(url_for('base.prompts'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating prompt {str(e)}','error')
    
    db.close()
    return render_template('prompts.html', form=form)
    
@bp.route('/profile', methods = ['GET','POST'])
def profile():
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.id == 1).first()
    if profile:
        form = ProfileForm(obj=profile)
    else:
        form = ProfileForm()
    if form.validate_on_submit():
        try:
            print('Trying to change the database object')
            profile.full_name = form.full_name.data
            profile.bio = form.bio.data
            profile.interests_description = form.interests_description.data
            db.commit()
            flash('Profile updated successfully','success')
            print("Finished")
            return redirect(url_for('base.profile'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating profile {str(e)}')
        
    db.close()
    return render_template('profile.html', form=form)

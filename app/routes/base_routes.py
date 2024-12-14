from flask import Flask, render_template, Blueprint, redirect, flash, url_for
import os
from ..forms import UrlSubmit, PromptForm, ProfileForm, ArticleCompareForm, BlogForm
from ..content_processor import ContentProcessor, ProfileComparer, BlogHandler
from ..database.database import SessionLocal
from ..database.models import Prompt, Profile
import asyncio
from ..api.article_operations import get_user_articles
import logging

bp = Blueprint('base', __name__)


@bp.route('/',methods=['GET','POST'])
def base():
    form = UrlSubmit()
    result = None

    if form.validate_on_submit():
        try:
            processor = ContentProcessor()
            result = asyncio.run(processor.process_url(form.url.data))
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
async def profile():
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.id == 1).first()
    
    profile_form = ProfileForm(obj=profile) if profile else ProfileForm()
    article_comparison_form = ArticleCompareForm()
    comparison_result = None
    db.close()
    return render_template('profile.html', 
                        profile_form=profile_form, 
                        article_comparison_form=article_comparison_form,
                        comparison_result=comparison_result)

@bp.route('/profile/update', methods=['POST'])
async def update_profile():
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.id == 1).first()
    profile_form = ProfileForm(obj=profile)
    if profile_form.validate_on_submit():
        try:
            profile.full_name = profile_form.full_name.data
            profile.bio = profile_form.bio.data
            profile.interests_description = profile_form.interests_description.data
            db.commit()
            flash('Profile updated successfully','success')
            return redirect(url_for('base.profile'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating profile {str(e)}') 
    db.close()
    return redirect(url_for('base.profile'))
    
@bp.route('/profile/compare',methods=['POST'])
async def compare_article():
    logging.getLogger().setLevel(logging.ERROR)
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.id == 1).first()
    article_comparison_form = ArticleCompareForm()
    comparison_result = None
    if article_comparison_form.validate_on_submit():
        try:
            comparer = ProfileComparer()
            comparison_result = await comparer.compare_article_to_profile(
                article_url=article_comparison_form.article_url.data,
                id=profile.id
            )
            flash('Article comparison completed', 'success')
        except Exception as e:
            flash(f'Error comparing the articles {str(e)}')
    db.close()
    return render_template('profile.html', 
                         profile_form=ProfileForm(obj=profile), 
                         article_comparison_form=article_comparison_form,
                         comparison_result=comparison_result)

@bp.route('/blogs' ,methods=['GET','POST'])
async def blogs():
    form = BlogForm()
    result = None

    if form.validate_on_submit():
        try:
            blog_handler = BlogHandler()
            result = await blog_handler.process_and_store_articles(form.url.data,1)
        except Exception as e:
                result = {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
                }
    return render_template('blogs.html',form=form,result=result)

@bp.route('/processed-articles', methods=['GET'])
def processed_articles():
    db = SessionLocal()
    try:
        articles = get_user_articles(db, profile_id=1)  # Hardcoded profile_id for now
        return render_template('processed_articles.html', 
                             articles=articles)
    except Exception as e:
        flash(f'Error loading articles: {str(e)}', 'error')
        return redirect(url_for('base.base'))
    finally:
        db.close()
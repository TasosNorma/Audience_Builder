from flask import Flask, render_template, Blueprint, redirect, flash, url_for, request
from flask_login import login_required, current_user
import os
from ..forms import UrlSubmit, PromptForm, ProfileForm, ArticleCompareForm, BlogForm
from ..content_processor import ContentProcessor, ProfileComparer, BlogHandler
from ..database.database import SessionLocal
from ..database.models import Prompt, Profile, User
import asyncio
from ..api.article_operations import get_user_articles
import logging

bp = Blueprint('base', __name__)

@bp.before_request
def check_onboarding():
    # We only need to check if the current page isn't the onboarding page
    if not current_user.is_onboarded and request.endpoint != 'base.onboarding':
        return redirect(url_for('base.onboarding'))

@bp.route('/home',methods=['GET','POST'])
@login_required
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
@login_required
def prompts():
    db = SessionLocal()
    prompt = db.query(Prompt).filter(Prompt.user_id == current_user.id, Prompt.type == 1).first()

    # Create a prompt object that will be placed inside the form for a placeholder in order to showcase only the relevant parts of the prompt
    modified_prompt = prompt
    parts = modified_prompt.template.split("### Suffix_")
    editable_template = parts[0] if len(parts) >1 else ''
    modified_prompt.template = editable_template

    if modified_prompt:
        form = PromptForm(obj=modified_prompt)
    else:
        form = PromptForm()

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
@login_required
async def profile():
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    profile_form = ProfileForm(obj=profile) if profile else ProfileForm()
    article_comparison_form = ArticleCompareForm()
    comparison_result = None
    db.close()
    return render_template('profile.html', 
                        profile_form=profile_form, 
                        article_comparison_form=article_comparison_form,
                        comparison_result=comparison_result)

@bp.route('/profile/update', methods=['POST'])
@login_required
async def update_profile():
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    profile_form = ProfileForm(obj=profile)
    if profile_form.validate_on_submit():
        try:
            profile.full_name = profile_form.full_name.data
            profile.bio = profile_form.bio.data
            profile.interests_description = profile_form.interests_description.data
            profile.user_id = current_user.id
            db.commit()
            flash('Profile updated successfully','success')
            return redirect(url_for('base.profile'))
        except Exception as e:
            db.rollback()
            flash(f'Error updating profile {str(e)}') 
    db.close()
    return redirect(url_for('base.profile'))
    
@bp.route('/profile/compare',methods=['POST'])
@login_required
async def compare_article():
    logging.getLogger().setLevel(logging.ERROR)
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    article_comparison_form = ArticleCompareForm()
    comparison_result = None
    if article_comparison_form.validate_on_submit():
        try:
            comparer = ProfileComparer(current_user.id)
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
@login_required
async def blogs():
    form = BlogForm()
    result = None

    if form.validate_on_submit():
        try:
            blog_handler = BlogHandler()
            result = await blog_handler.process_and_store_articles(form.url.data,current_user.id)
        except Exception as e:
                result = {
                "status": "error",
                "message": f"An error occurred: {str(e)}"
                }
    return render_template('blogs.html',form=form,result=result)

@bp.route('/processed-articles', methods=['GET'])
@login_required
def processed_articles():
    db = SessionLocal()
    try:
        articles = get_user_articles(db,current_user.id)
        return render_template('processed_articles.html', 
                             articles=articles)
    except Exception as e:
        flash(f'Error loading articles: {str(e)}', 'error')
        return redirect(url_for('base.base'))
    finally:
        db.close()

@bp.route('/onboarding',methods=['GET','POST'])
@login_required
def onboarding():
    if current_user.is_onboarded:
        return redirect(url_for('base.base'))
    
    db= SessionLocal()
    form = ProfileForm()

    if form.validate_on_submit():
        try:
            profile = Profile(
                user_id = current_user.id,
                username = current_user.email.split('@')[0],
                full_name = form.full_name.data,
                bio = form.bio.data,
                interests_description = form.interests_description.data
            )
            user = db.query(User).get(current_user.id)
            user.is_onboarded = True

            db.add(profile)
            db.commit()

            flash('Profile Created Successfully!','success')
            return redirect(url_for('base.base'))
        except Exception as e:
            db.rollback()
            flash('Error creating the profile','error')
            print(f'Error creating the profile {str(e)} ')
        finally:
            db.close()
    
    return render_template('onboarding.html',form=form)
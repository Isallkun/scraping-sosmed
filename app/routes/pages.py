"""
HTML page routes for Flask Analytics Dashboard.

This module defines routes that render HTML templates for the dashboard pages.
Each route passes necessary configuration values to the templates.
"""

from flask import Blueprint, render_template, current_app

# Create blueprint for page routes
pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def home():
    """
    Render home/overview page with summary statistics.
    
    Returns:
        Rendered home.html template with refresh interval configuration
    """
    return render_template(
        'home.html',
        refresh_interval=current_app.config.get('AUTO_REFRESH_INTERVAL', 30),
        page_title='Dashboard Overview'
    )


@pages_bp.route('/sentiment')
def sentiment():
    """
    Render sentiment analysis page with sentiment visualizations.
    
    Returns:
        Rendered sentiment.html template
    """
    return render_template(
        'sentiment.html',
        page_title='Sentiment Analysis'
    )


@pages_bp.route('/engagement')
def engagement():
    """
    Render engagement metrics page with engagement visualizations.
    
    Returns:
        Rendered engagement.html template
    """
    return render_template(
        'engagement.html',
        page_title='Engagement Metrics'
    )


@pages_bp.route('/content')
def content():
    """
    Render content analysis page with content pattern visualizations.
    
    Returns:
        Rendered content.html template
    """
    return render_template(
        'content.html',
        page_title='Content Analysis'
    )


@pages_bp.route('/explorer')
def explorer():
    """
    Render data explorer page with searchable and filterable post table.
    
    Returns:
        Rendered explorer.html template
    """
    return render_template(
        'explorer.html',
        page_title='Data Explorer'
    )

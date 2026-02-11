"""
Scraping Service Module

This module provides functionality to run Instagram scraping jobs
and automatically import results to the database.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any

from app.services.import_service import process_import_file, ImportServiceError
from werkzeug.datastructures import FileStorage
import io

# Configure logging
logger = logging.getLogger(__name__)


class ScrapingServiceError(Exception):
    """Custom exception for scraping service errors"""
    pass


def run_instagram_scrape(
    target_url: str,
    limit: int = 5,
    scrape_comments: bool = True,
    run_sentiment: bool = True,
    headless: bool = True
) -> Dict[str, Any]:
    """
    Run Instagram scraping job.
    
    Args:
        target_url: Instagram profile URL to scrape
        limit: Number of posts to scrape
        scrape_comments: Whether to scrape comments
        run_sentiment: Whether to run sentiment analysis
        headless: Run browser in headless mode
        
    Returns:
        Dict with job results including file paths and stats
        
    Raises:
        ScrapingServiceError: If scraping fails
    """
    try:
        logger.info(f"Starting Instagram scrape: {target_url}, limit={limit}")
        
        # Get project root
        project_root = Path(__file__).parent.parent.parent
        scraper_script = project_root / "scrape_instagram_simple.py"
        
        if not scraper_script.exists():
            raise ScrapingServiceError(f"Scraper script not found: {scraper_script}")
        
        # Build command
        # Usage: python scrape_instagram_simple.py <profile_url> <limit> <headless> <scrape_comments> <comments_per_post>
        cmd = [
            sys.executable,
            str(scraper_script),
            target_url,
            str(limit),
            str(headless).lower(),
            str(scrape_comments).lower(),
            "999"  # comments_per_post - scrape all available comments
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Run scraper with timeout
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
            encoding='utf-8',
            errors='replace'
        )
        
        # Check if scraping succeeded
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            logger.error(f"Scraping failed: {error_msg}")
            raise ScrapingServiceError(f"Scraping failed: {error_msg}")
        
        logger.info("Scraping completed successfully")
        logger.debug(f"Scraper output: {result.stdout}")
        
        # Find the output file (scrape_instagram_simple.py saves to output/instagram/raw/posts_*.json)
        output_dir = project_root / "output" / "instagram" / "raw"
        
        if not output_dir.exists():
            raise ScrapingServiceError(f"Output directory not found: {output_dir}")
        
        json_files = sorted(
            output_dir.glob("posts_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not json_files:
            raise ScrapingServiceError("No output file found after scraping")
        
        output_file = json_files[0]
        logger.info(f"Scraping output file: {output_file}")
        
        # Read scraping results
        with open(output_file, 'r', encoding='utf-8') as f:
            scrape_data = json.load(f)
        
        result_data = {
            'status': 'success',
            'output_file': str(output_file),
            'posts_scraped': scrape_data.get('metadata', {}).get('total_posts', 0),
            'sentiment_file': None,
            'sentiment_run': False
        }
        
        # Run sentiment analysis if requested
        if run_sentiment and scrape_data.get('posts'):
            logger.info("Running sentiment analysis...")
            sentiment_file = run_sentiment_analysis(str(output_file))
            result_data['sentiment_file'] = sentiment_file
            result_data['sentiment_run'] = True
            logger.info(f"Sentiment analysis completed: {sentiment_file}")
        
        return result_data
        
    except subprocess.TimeoutExpired:
        logger.error("Scraping timeout after 10 minutes")
        raise ScrapingServiceError("Scraping timeout - process took too long")
    except Exception as e:
        logger.error(f"Scraping error: {e}", exc_info=True)
        raise ScrapingServiceError(f"Scraping failed: {str(e)}")


def run_sentiment_analysis(input_file: str) -> str:
    """
    Run sentiment analysis on scraped data.
    
    Args:
        input_file: Path to input JSON file
        
    Returns:
        Path to sentiment output file
        
    Raises:
        ScrapingServiceError: If sentiment analysis fails
    """
    try:
        project_root = Path(__file__).parent.parent.parent
        sentiment_script = project_root / "sentiment" / "main_analyzer.py"
        
        if not sentiment_script.exists():
            raise ScrapingServiceError(f"Sentiment script not found: {sentiment_script}")
        
        # Generate output path
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_sentiment.json"
        
        # Build command
        cmd = [
            sys.executable,
            "-m",
            "sentiment.main_analyzer",
            "--input", str(input_file),
            "--output", str(output_file),
            "--model", "vader"
        ]
        
        logger.info(f"Running sentiment analysis: {' '.join(cmd)}")
        
        # Run sentiment analysis
        result = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            logger.warning(f"Sentiment analysis failed: {error_msg}")
            raise ScrapingServiceError(f"Sentiment analysis failed: {error_msg}")
        
        if not output_file.exists():
            raise ScrapingServiceError("Sentiment output file not created")
        
        logger.info(f"Sentiment analysis completed: {output_file}")
        return str(output_file)
        
    except subprocess.TimeoutExpired:
        logger.error("Sentiment analysis timeout")
        raise ScrapingServiceError("Sentiment analysis timeout")
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise ScrapingServiceError(f"Sentiment analysis failed: {str(e)}")


def import_scrape_results(
    file_path: str,
    platform: str = 'instagram',
    clear_existing: bool = True
) -> Dict[str, Any]:
    """
    Import scraping results to database.
    
    Args:
        file_path: Path to JSON file to import
        platform: Social media platform
        clear_existing: Whether to clear existing data
        
    Returns:
        Import statistics
        
    Raises:
        ScrapingServiceError: If import fails
    """
    try:
        logger.info(f"Importing scrape results from: {file_path}")
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create a file-like object for import service
        file_storage = FileStorage(
            stream=io.BytesIO(content.encode('utf-8')),
            filename=Path(file_path).name,
            content_type='application/json'
        )
        
        # Import using existing import service
        from app.services.import_service import process_import_file
        result = process_import_file(file_storage, 'json', platform, clear_existing)
        
        logger.info(f"Import completed: {result}")
        return result
        
    except ImportServiceError as e:
        logger.error(f"Import failed: {e}")
        raise ScrapingServiceError(f"Import failed: {str(e)}")
    except Exception as e:
        logger.error(f"Import error: {e}", exc_info=True)
        raise ScrapingServiceError(f"Import failed: {str(e)}")

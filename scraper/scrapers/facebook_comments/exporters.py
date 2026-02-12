"""Export operations for crawled Facebook comment data (CSV, Excel, JSON)"""

import json
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from scraper.utils.logger import get_logger
from scraper.scrapers.facebook_comments.config import FBCommentConfig
from scraper.scrapers.facebook_comments.utils import get_timestamp_string, sanitize_filename

logger = get_logger('scraper.facebook_comments.exporters')


class CSVExporter:
    """Handle CSV and Excel export operations"""

    def __init__(self, export_mode: str = "single", export_format: str = "csv"):
        self.export_mode = export_mode or FBCommentConfig.EXPORT_MODE
        self.export_format = export_format or FBCommentConfig.EXPORT_FORMAT
        self.comments_data: List[Dict[str, Any]] = []

    def add_comments(self, comments: List[Dict[str, Any]]) -> None:
        """Add comments to the internal buffer"""
        self.comments_data.extend(comments)

    def export(self, username: Optional[str] = None) -> List[str]:
        """Export comments to file(s)"""
        if not self.comments_data:
            logger.warning("No comments to export")
            return []

        if self.export_mode == "single":
            return [self._export_single_file(username)]
        else:
            return self._export_per_post()

    def _export_single_file(self, username: Optional[str] = None) -> str:
        """Export all comments to a single file"""
        timestamp = get_timestamp_string()

        if username:
            filename = f"comments_{sanitize_filename(username)}_{timestamp}"
        else:
            filename = f"comments_{timestamp}"

        if self.export_format == "excel":
            filename += ".xlsx"
        else:
            filename += ".csv"

        csv_dir = FBCommentConfig.EXPORTS_DIR / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)
        filepath = csv_dir / filename

        df = pd.DataFrame(self.comments_data)

        column_order = [
            'post_url', 'post_author', 'post_timestamp',
            'comment_author_name', 'comment_author_url',
            'comment_text', 'comment_timestamp',
            'likes_count', 'replies_count', 'crawled_at'
        ]

        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]

        if self.export_format == "excel":
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            df.to_csv(filepath, index=False, encoding='utf-8-sig')

        logger.info(f"Exported {len(df)} comments to {filepath}")
        return str(filepath)

    def _export_per_post(self) -> List[str]:
        """Export comments with one file per post"""
        exported_files = []
        df = pd.DataFrame(self.comments_data)

        if 'post_url' not in df.columns:
            logger.error("post_url column not found, cannot export per-post")
            return []

        grouped = df.groupby('post_url')
        csv_dir = FBCommentConfig.EXPORTS_DIR / "csv"
        csv_dir.mkdir(parents=True, exist_ok=True)

        for post_url, group_df in grouped:
            post_id = _extract_post_id(post_url)
            timestamp = get_timestamp_string()

            filename = f"comments_{sanitize_filename(post_id)}_{timestamp}"
            filename += ".xlsx" if self.export_format == "excel" else ".csv"
            filepath = csv_dir / filename

            column_order = [
                'post_url', 'post_author', 'post_timestamp',
                'comment_author_name', 'comment_author_url',
                'comment_text', 'comment_timestamp',
                'likes_count', 'replies_count', 'crawled_at'
            ]

            existing_columns = [col for col in column_order if col in group_df.columns]
            group_df = group_df[existing_columns]

            if self.export_format == "excel":
                group_df.to_excel(filepath, index=False, engine='openpyxl')
            else:
                group_df.to_csv(filepath, index=False, encoding='utf-8-sig')

            exported_files.append(str(filepath))

        logger.info(f"Exported comments to {len(exported_files)} files")
        return exported_files

    def clear_buffer(self) -> None:
        """Clear the internal comments buffer"""
        self.comments_data = []

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about buffered comments"""
        if not self.comments_data:
            return {'total_comments': 0, 'unique_posts': 0, 'unique_authors': 0}

        df = pd.DataFrame(self.comments_data)
        return {
            'total_comments': len(df),
            'unique_posts': df['post_url'].nunique() if 'post_url' in df.columns else 0,
            'unique_authors': df['comment_author_name'].nunique() if 'comment_author_name' in df.columns else 0
        }


class JSONExporter:
    """Handle JSON export operations"""

    def __init__(self, export_mode: str = "single", pretty: bool = True):
        self.export_mode = export_mode or FBCommentConfig.EXPORT_MODE
        self.pretty = pretty
        self.comments_data: List[Dict[str, Any]] = []

    def add_comments(self, comments: List[Dict[str, Any]]) -> None:
        """Add comments to the internal buffer"""
        self.comments_data.extend(comments)

    def export(self, username: Optional[str] = None) -> List[str]:
        """Export comments to JSON file(s)"""
        if not self.comments_data:
            logger.warning("No comments to export")
            return []

        if self.export_mode == "single":
            return [self._export_single_file(username)]
        else:
            return self._export_per_post()

    def _export_single_file(self, username: Optional[str] = None) -> str:
        """Export all comments to a single JSON file"""
        timestamp = get_timestamp_string()

        if username:
            filename = f"comments_{sanitize_filename(username)}_{timestamp}.json"
        else:
            filename = f"comments_{timestamp}.json"

        json_dir = FBCommentConfig.EXPORTS_DIR / "json"
        json_dir.mkdir(parents=True, exist_ok=True)
        filepath = json_dir / filename

        clean_comments = []
        for comment in self.comments_data:
            clean_comment = {k: v for k, v in comment.items()
                           if k not in ['post_content', 'comment_id', 'parent_comment_id']}
            clean_comments.append(clean_comment)

        export_data = {
            "metadata": {
                "total_comments": len(clean_comments),
                "exported_at": datetime.now().isoformat(),
                "username": username if username else "unknown"
            },
            "comments": clean_comments
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            if self.pretty:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(export_data, f, ensure_ascii=False)

        logger.info(f"Exported {len(clean_comments)} comments to {filepath}")
        return str(filepath)

    def _export_per_post(self) -> List[str]:
        """Export comments with one JSON file per post"""
        exported_files = []

        posts_comments = {}
        for comment in self.comments_data:
            post_url = comment.get('post_url', 'unknown')
            if post_url not in posts_comments:
                posts_comments[post_url] = []
            posts_comments[post_url].append(comment)

        json_dir = FBCommentConfig.EXPORTS_DIR / "json"
        json_dir.mkdir(parents=True, exist_ok=True)

        for post_url, comments in posts_comments.items():
            post_id = _extract_post_id(post_url)
            timestamp = get_timestamp_string()
            filename = f"comments_{sanitize_filename(post_id)}_{timestamp}.json"
            filepath = json_dir / filename

            export_data = {
                "metadata": {
                    "post_url": post_url,
                    "total_comments": len(comments),
                    "exported_at": datetime.now().isoformat()
                },
                "comments": comments
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                if self.pretty:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(export_data, f, ensure_ascii=False)

            exported_files.append(str(filepath))

        logger.info(f"Exported comments to {len(exported_files)} JSON files")
        return exported_files

    def clear_buffer(self) -> None:
        """Clear the internal comments buffer"""
        self.comments_data = []

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about buffered comments"""
        if not self.comments_data:
            return {'total_comments': 0, 'unique_posts': 0, 'unique_authors': 0}

        unique_posts = set()
        unique_authors = set()

        for comment in self.comments_data:
            if 'post_url' in comment:
                unique_posts.add(comment['post_url'])
            if 'comment_author_name' in comment:
                unique_authors.add(comment['comment_author_name'])

        return {
            'total_comments': len(self.comments_data),
            'unique_posts': len(unique_posts),
            'unique_authors': len(unique_authors)
        }


def _extract_post_id(post_url: str) -> str:
    """Extract post ID from Facebook post URL"""
    try:
        if "/posts/" in post_url:
            post_id = post_url.split("/posts/")[-1].split("/")[0].split("?")[0]
        elif "/reel/" in post_url:
            post_id = post_url.split("/reel/")[-1].split("/")[0].split("?")[0]
        elif "story_fbid=" in post_url:
            post_id = post_url.split("story_fbid=")[-1].split("&")[0]
        elif "fbid=" in post_url:
            post_id = post_url.split("fbid=")[-1].split("&")[0]
        else:
            post_id = post_url.rstrip('/').split('/')[-1].split('?')[0]

        return post_id[:50]
    except Exception:
        return "unknown"

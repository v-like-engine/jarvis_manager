"""Application favorites and usage tracking."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AppFavorites:
    """
    Manage application favorites and usage tracking.

    Features:
    - Mark apps as favorites
    - Track app launch frequency
    - Track recent apps
    - Learning: improve fuzzy matching based on usage
    """

    def __init__(self, favorites_file: Optional[Path] = None):
        """
        Initialize app favorites manager.

        Args:
            favorites_file: Path to favorites storage file
        """
        if favorites_file is None:
            favorites_file = Path(__file__).parent.parent.parent / "data" / "app_favorites.json"

        self.favorites_file = favorites_file
        self.favorites: List[str] = []  # List of favorite app names
        self.launch_count: Dict[str, int] = defaultdict(int)  # App name -> launch count
        self.recent_apps: List[Dict[str, Any]] = []  # Recently launched apps
        self.usage_patterns: Dict[str, List[str]] = defaultdict(list)  # Query -> app name mappings

        # Create data directory
        self.favorites_file.parent.mkdir(parents=True, exist_ok=True)

        # Load data
        self._load_data()

        logger.info("AppFavorites initialized")

    def add_favorite(self, app_name: str) -> Dict[str, Any]:
        """
        Add app to favorites.

        Args:
            app_name: Application name

        Returns:
            Dictionary with result
        """
        try:
            if app_name not in self.favorites:
                self.favorites.append(app_name)
                self._save_data()

                return {
                    'success': True,
                    'message': f"{app_name} added to favorites"
                }
            else:
                return {
                    'success': True,
                    'message': f"{app_name} is already in favorites"
                }

        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def remove_favorite(self, app_name: str) -> Dict[str, Any]:
        """
        Remove app from favorites.

        Args:
            app_name: Application name

        Returns:
            Dictionary with result
        """
        try:
            if app_name in self.favorites:
                self.favorites.remove(app_name)
                self._save_data()

                return {
                    'success': True,
                    'message': f"{app_name} removed from favorites"
                }
            else:
                return {
                    'success': False,
                    'error': f"{app_name} is not in favorites"
                }

        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_favorites(self) -> List[str]:
        """
        Get list of favorite apps.

        Returns:
            List of favorite app names
        """
        return self.favorites.copy()

    def is_favorite(self, app_name: str) -> bool:
        """
        Check if app is in favorites.

        Args:
            app_name: Application name

        Returns:
            True if favorite, False otherwise
        """
        return app_name in self.favorites

    def record_launch(self, app_name: str, query: Optional[str] = None):
        """
        Record app launch for usage tracking.

        Args:
            app_name: Application name that was launched
            query: Optional user query that triggered the launch
        """
        try:
            # Increment launch count
            self.launch_count[app_name] += 1

            # Add to recent apps
            recent_entry = {
                'app_name': app_name,
                'timestamp': datetime.now().isoformat(),
                'query': query
            }

            self.recent_apps.insert(0, recent_entry)

            # Keep only last 50 recent apps
            self.recent_apps = self.recent_apps[:50]

            # Record usage pattern if query provided
            if query:
                if app_name not in self.usage_patterns[query.lower()]:
                    self.usage_patterns[query.lower()].append(app_name)

            self._save_data()

            logger.debug(f"Recorded launch: {app_name} (total: {self.launch_count[app_name]})")

        except Exception as e:
            logger.error(f"Error recording launch: {e}")

    def get_recent_apps(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently launched apps.

        Args:
            limit: Maximum number of apps to return

        Returns:
            List of recent app entries
        """
        return self.recent_apps[:limit]

    def get_most_used_apps(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently used apps.

        Args:
            limit: Maximum number of apps to return

        Returns:
            List of (app_name, launch_count) sorted by count
        """
        sorted_apps = sorted(
            self.launch_count.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {'app_name': name, 'launch_count': count}
            for name, count in sorted_apps[:limit]
        ]

    def get_learned_match(self, query: str) -> Optional[str]:
        """
        Get learned app match for a query.

        Args:
            query: User query

        Returns:
            App name if learned, None otherwise
        """
        query_lower = query.lower()

        # Check exact learned pattern
        if query_lower in self.usage_patterns:
            matches = self.usage_patterns[query_lower]
            if matches:
                # Return the most recent match
                return matches[-1]

        # Check partial matches
        for pattern, apps in self.usage_patterns.items():
            if query_lower in pattern or pattern in query_lower:
                if apps:
                    return apps[-1]

        return None

    def boost_score_for_favorites(self, app_name: str, base_score: int) -> int:
        """
        Boost fuzzy match score for favorite apps.

        Args:
            app_name: Application name
            base_score: Base fuzzy match score

        Returns:
            Boosted score
        """
        if self.is_favorite(app_name):
            # Boost favorites by 10 points
            return min(100, base_score + 10)

        return base_score

    def boost_score_for_usage(self, app_name: str, base_score: int) -> int:
        """
        Boost fuzzy match score based on usage frequency.

        Args:
            app_name: Application name
            base_score: Base fuzzy match score

        Returns:
            Boosted score
        """
        if app_name in self.launch_count:
            count = self.launch_count[app_name]

            # Boost based on launch count (logarithmic scale)
            if count >= 50:
                boost = 15
            elif count >= 20:
                boost = 10
            elif count >= 10:
                boost = 7
            elif count >= 5:
                boost = 5
            else:
                boost = 2

            return min(100, base_score + boost)

        return base_score

    def get_stats(self) -> Dict[str, Any]:
        """
        Get favorites and usage statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'favorites_count': len(self.favorites),
            'tracked_apps': len(self.launch_count),
            'total_launches': sum(self.launch_count.values()),
            'recent_count': len(self.recent_apps),
            'learned_patterns': len(self.usage_patterns)
        }

    def clear_recent(self):
        """Clear recent apps history."""
        self.recent_apps = []
        self._save_data()
        logger.info("Recent apps cleared")

    def clear_all_data(self):
        """Clear all favorites and usage data."""
        self.favorites = []
        self.launch_count = defaultdict(int)
        self.recent_apps = []
        self.usage_patterns = defaultdict(list)
        self._save_data()
        logger.info("All favorites and usage data cleared")

    def _load_data(self):
        """Load favorites and usage data from file."""
        try:
            if self.favorites_file.exists():
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    self.favorites = data.get('favorites', [])
                    self.launch_count = defaultdict(int, data.get('launch_count', {}))
                    self.recent_apps = data.get('recent_apps', [])
                    self.usage_patterns = defaultdict(list, data.get('usage_patterns', {}))

                logger.info(f"Loaded favorites and usage data")

        except Exception as e:
            logger.error(f"Error loading favorites data: {e}")

    def _save_data(self):
        """Save favorites and usage data to file."""
        try:
            data = {
                'favorites': self.favorites,
                'launch_count': dict(self.launch_count),
                'recent_apps': self.recent_apps,
                'usage_patterns': {k: list(v) for k, v in self.usage_patterns.items()}
            }

            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug("Saved favorites and usage data")

        except Exception as e:
            logger.error(f"Error saving favorites data: {e}")

"""Application database with caching and fuzzy matching."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)


class AppDatabase:
    """
    Database of installed applications with caching and fuzzy matching.

    Features:
    - Cache discovered apps to disk
    - Fuzzy string matching for app names
    - Automatic cache refresh
    """

    def __init__(
        self,
        cache_file: Optional[Path] = None,
        cache_refresh_interval: int = 3600,  # 1 hour
        fuzzy_threshold: int = 70
    ):
        """
        Initialize app database.

        Args:
            cache_file: Path to cache file
            cache_refresh_interval: Cache refresh interval in seconds
            fuzzy_threshold: Minimum fuzzy match score (0-100)
        """
        if cache_file is None:
            cache_file = Path(__file__).parent.parent.parent / "cache" / "apps.json"

        self.cache_file = cache_file
        self.cache_refresh_interval = cache_refresh_interval
        self.fuzzy_threshold = fuzzy_threshold

        self.apps: List[Dict[str, Any]] = []
        self.last_refresh: Optional[datetime] = None

        # Create cache directory
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"App database initialized (cache: {cache_file})")

    def load_cache(self) -> bool:
        """
        Load apps from cache file.

        Returns:
            True if cache was loaded successfully
        """
        if not self.cache_file.exists():
            logger.debug("Cache file doesn't exist")
            return False

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.apps = data.get('apps', [])
                last_refresh_str = data.get('last_refresh')

                if last_refresh_str:
                    self.last_refresh = datetime.fromisoformat(last_refresh_str)

            logger.info(f"Loaded {len(self.apps)} apps from cache")
            return True

        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return False

    def save_cache(self) -> bool:
        """
        Save apps to cache file.

        Returns:
            True if cache was saved successfully
        """
        try:
            data = {
                'apps': self.apps,
                'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved {len(self.apps)} apps to cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            return False

    def needs_refresh(self) -> bool:
        """
        Check if cache needs to be refreshed.

        Returns:
            True if cache is stale or doesn't exist
        """
        if not self.apps or not self.last_refresh:
            return True

        elapsed = datetime.now() - self.last_refresh
        return elapsed.total_seconds() > self.cache_refresh_interval

    def update_apps(self, apps: List[Dict[str, Any]]):
        """
        Update database with new app list.

        Args:
            apps: List of discovered applications
        """
        self.apps = apps
        self.last_refresh = datetime.now()
        self.save_cache()
        logger.info(f"Updated database with {len(apps)} apps")

    def get_all_apps(self) -> List[Dict[str, Any]]:
        """
        Get all apps in database.

        Returns:
            List of all applications
        """
        return self.apps.copy()

    def find_exact_match(self, app_name: str) -> Optional[Dict[str, Any]]:
        """
        Find exact match for app name (case-insensitive).

        Args:
            app_name: Application name to find

        Returns:
            App info or None
        """
        name_lower = app_name.lower()

        for app in self.apps:
            if app['name'].lower() == name_lower:
                return app

        return None

    def find_fuzzy_match(
        self,
        query: str,
        limit: int = 5
    ) -> List[Tuple[Dict[str, Any], int]]:
        """
        Find best fuzzy matches for query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of (app_info, match_score) tuples, sorted by score
        """
        if not self.apps:
            return []

        # Create list of app names for fuzzy matching
        app_names = [app['name'] for app in self.apps]

        # Use rapidfuzz to find best matches
        matches = process.extract(
            query,
            app_names,
            scorer=fuzz.WRatio,
            limit=limit
        )

        # Filter by threshold and map back to app info
        results = []
        for name, score, _ in matches:
            if score >= self.fuzzy_threshold:
                # Find the app with this name
                for app in self.apps:
                    if app['name'] == name:
                        results.append((app, score))
                        break

        return results

    def find_best_match(self, query: str) -> Optional[Tuple[Dict[str, Any], int]]:
        """
        Find single best match for query.

        Args:
            query: Search query

        Returns:
            Tuple of (app_info, match_score) or None
        """
        # Try exact match first
        exact = self.find_exact_match(query)
        if exact:
            return (exact, 100)

        # Try fuzzy match
        matches = self.find_fuzzy_match(query, limit=1)
        if matches:
            return matches[0]

        return None

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for apps matching query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching apps
        """
        # Get fuzzy matches
        matches = self.find_fuzzy_match(query, limit=limit)

        # Return just the app info (without scores)
        return [app for app, _ in matches]

    def get_by_path(self, exe_path: str) -> Optional[Dict[str, Any]]:
        """
        Find app by executable path.

        Args:
            exe_path: Path to executable

        Returns:
            App info or None
        """
        path_lower = exe_path.lower()

        for app in self.apps:
            if app.get('exe_path', '').lower() == path_lower:
                return app

        return None

    def stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Statistics dictionary
        """
        locations = {}
        for app in self.apps:
            loc = app.get('location', 'unknown')
            locations[loc] = locations.get(loc, 0) + 1

        return {
            'total_apps': len(self.apps),
            'last_refresh': self.last_refresh.isoformat() if self.last_refresh else None,
            'locations': locations,
            'cache_file': str(self.cache_file),
        }

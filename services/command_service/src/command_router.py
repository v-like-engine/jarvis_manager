"""Route commands to appropriate modules."""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from modules.app_launcher import AppFinder, AppDatabase, AppLauncher, AppCloser
from modules.terminal import TerminalExecutor
from modules.file_ops import FileManager, DirectoryManager, FileBrowser
from modules.settings import StartupManager, LanguageManager, PreferencesManager
from modules.music_control import MusicController
from modules.system_info import SystemInfoManager
from modules.time_date import TimeDateManager
from modules.calculator import Calculator
from modules.screen_control import ScreenController

logger = logging.getLogger(__name__)


class CommandRouter:
    """
    Route commands to appropriate execution modules.

    This is the central dispatcher that knows which module handles which command type.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize command router.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

        # Initialize modules
        self.app_finder = AppFinder()
        self.app_database = AppDatabase()
        self.app_launcher = AppLauncher()
        self.app_closer = AppCloser()

        self.terminal_executor = TerminalExecutor()

        self.file_manager = FileManager()
        self.directory_manager = DirectoryManager()
        self.file_browser = FileBrowser()

        self.startup_manager = StartupManager()
        self.language_manager = LanguageManager()
        self.preferences_manager = PreferencesManager()

        self.music_controller = MusicController()

        self.system_info_manager = SystemInfoManager()
        self.time_date_manager = TimeDateManager()
        self.calculator = Calculator()
        self.screen_controller = ScreenController()

        # Load app database
        self._load_app_database()

        logger.info("Command router initialized")

    def _load_app_database(self):
        """Load or refresh app database."""
        # Try to load from cache
        if self.app_database.load_cache():
            # Check if refresh needed
            if self.app_database.needs_refresh():
                logger.info("App database cache is stale, refreshing...")
                self._refresh_app_database()
        else:
            # No cache, discover apps
            logger.info("No app database cache, discovering apps...")
            self._refresh_app_database()

    def _refresh_app_database(self):
        """Refresh app database by discovering apps."""
        try:
            apps = self.app_finder.discover_apps()
            self.app_database.update_apps(apps)
            logger.info(f"App database refreshed with {len(apps)} apps")
        except Exception as e:
            logger.error(f"Failed to refresh app database: {e}")

    def route(self, command_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route command to appropriate handler.

        Args:
            command_type: Type of command
            params: Command parameters

        Returns:
            Execution result
        """
        try:
            # App commands
            if command_type == 'app_launch':
                return self._handle_app_launch(params)
            elif command_type == 'app_close':
                return self._handle_app_close(params)

            # Terminal commands
            elif command_type in ['terminal', 'terminal_command']:
                return self._handle_terminal(params)

            # File commands
            elif command_type == 'file_create':
                return self._handle_file_create(params)
            elif command_type == 'file_delete':
                return self._handle_file_delete(params)
            elif command_type == 'file_read':
                return self._handle_file_read(params)
            elif command_type == 'file_copy':
                return self._handle_file_copy(params)
            elif command_type == 'file_move':
                return self._handle_file_move(params)

            # Directory commands
            elif command_type == 'dir_create':
                return self._handle_dir_create(params)
            elif command_type == 'dir_delete':
                return self._handle_dir_delete(params)
            elif command_type == 'dir_list':
                return self._handle_dir_list(params)
            elif command_type == 'dir_navigate':
                return self._handle_dir_navigate(params)

            # Music commands
            elif command_type == 'music_play':
                return self.music_controller.play()
            elif command_type == 'music_pause':
                return self.music_controller.pause()
            elif command_type == 'music_next':
                return self.music_controller.next_track()
            elif command_type == 'music_previous':
                return self.music_controller.previous_track()
            elif command_type == 'music_stop':
                return self.music_controller.stop()

            # Volume commands
            elif command_type == 'volume_up':
                return self.music_controller.volume_up(params.get('step', 5))
            elif command_type == 'volume_down':
                return self.music_controller.volume_down(params.get('step', 5))
            elif command_type == 'volume_set':
                return self.music_controller.set_volume(params.get('level', 50))
            elif command_type == 'volume_mute':
                return self.music_controller.toggle_mute()

            # Settings commands
            elif command_type == 'language_switch':
                return self.language_manager.switch_language()
            elif command_type == 'language_set':
                return self.language_manager.set_language(params.get('language', 'en'))
            elif command_type == 'startup_enable':
                return self.startup_manager.enable_startup_registry()
            elif command_type == 'startup_disable':
                return self.startup_manager.disable_startup_registry()
            elif command_type == 'settings_get':
                return {'success': True, 'preferences': self.preferences_manager.get_all()}
            elif command_type == 'settings_set':
                return self.preferences_manager.set(params.get('key'), params.get('value'))

            # Special commands
            elif command_type == 'get_running_apps':
                return {'success': True, 'apps': self.app_closer.get_running_apps()}
            elif command_type == 'get_installed_apps':
                return {'success': True, 'apps': self.app_database.get_all_apps()}

            # Character switching (routes to both ASR and LLM services)
            elif command_type == 'character_switch':
                return self._handle_character_switch(params)

            # System information commands
            elif command_type == 'system_info_computer_name':
                return self.system_info_manager.get_computer_name()
            elif command_type == 'system_info_memory':
                return self.system_info_manager.get_memory_info()
            elif command_type == 'system_info_cpu':
                return self.system_info_manager.get_cpu_usage()
            elif command_type == 'system_info_disk':
                return self.system_info_manager.get_disk_space(params.get('path', 'C:\\'))
            elif command_type == 'system_info_os':
                return self.system_info_manager.get_os_info()
            elif command_type == 'system_info_network':
                return self.system_info_manager.get_network_info()
            elif command_type == 'system_info_uptime':
                return self.system_info_manager.get_uptime()
            elif command_type == 'system_info_all':
                return self.system_info_manager.get_all_info()

            # Time and date commands
            elif command_type == 'time_get':
                return self.time_date_manager.get_current_time()
            elif command_type == 'date_get':
                return self.time_date_manager.get_current_date()
            elif command_type == 'datetime_get':
                return self.time_date_manager.get_current_datetime()
            elif command_type == 'weekday_get':
                return self.time_date_manager.get_weekday()
            elif command_type == 'alarm_set':
                return self.time_date_manager.set_alarm(
                    params.get('time'),
                    params.get('message', 'Alarm!')
                )
            elif command_type == 'alarm_list':
                return self.time_date_manager.list_alarms()
            elif command_type == 'alarm_cancel':
                return self.time_date_manager.cancel_alarm(params.get('alarm_id'))
            elif command_type == 'timer_start':
                return self.time_date_manager.start_timer(
                    params.get('minutes', 1),
                    params.get('message', 'Timer finished!')
                )

            # Calculator commands
            elif command_type == 'calculate':
                return self.calculator.calculate(params.get('expression', ''))
            elif command_type == 'calculate_add':
                return self.calculator.add(params.get('a'), params.get('b'))
            elif command_type == 'calculate_subtract':
                return self.calculator.subtract(params.get('a'), params.get('b'))
            elif command_type == 'calculate_multiply':
                return self.calculator.multiply(params.get('a'), params.get('b'))
            elif command_type == 'calculate_divide':
                return self.calculator.divide(params.get('a'), params.get('b'))

            # Screen control commands
            elif command_type == 'screen_lock':
                return self.screen_controller.lock_screen()
            elif command_type == 'screen_sleep':
                return self.screen_controller.sleep()
            elif command_type == 'screen_shutdown':
                return self.screen_controller.shutdown(
                    force=params.get('force', False),
                    timeout=params.get('timeout', 60)
                )
            elif command_type == 'screen_restart':
                return self.screen_controller.restart(
                    force=params.get('force', False),
                    timeout=params.get('timeout', 60)
                )
            elif command_type == 'screen_cancel_shutdown':
                return self.screen_controller.cancel_shutdown()
            elif command_type == 'screen_monitor_off':
                return self.screen_controller.turn_off_monitor()
            elif command_type == 'screen_monitor_on':
                return self.screen_controller.turn_on_monitor()
            elif command_type == 'screen_hibernate':
                return self.screen_controller.hibernate()
            elif command_type == 'screen_logoff':
                return self.screen_controller.log_off()

            else:
                return {
                    'success': False,
                    'error': f'Unknown command type: {command_type}'
                }

        except Exception as e:
            logger.error(f"Error routing command {command_type}: {e}")
            return {
                'success': False,
                'error': f'Command execution failed: {str(e)}'
            }

    def _handle_app_launch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle app launch command."""
        app_name = params['app_name']

        # Find app in database
        match = self.app_database.find_best_match(app_name)

        if not match:
            return {
                'success': False,
                'error': f'Application not found: {app_name}'
            }

        app_info, score = match
        logger.info(f"Found app: {app_info['name']} (match score: {score})")

        # Launch app
        return self.app_launcher.launch(
            app_info['exe_path'],
            args=params.get('args')
        )

    def _handle_app_close(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle app close command."""
        app_name = params['app_name']
        return self.app_closer.close_by_name(app_name, force=params.get('force', False))

    def _handle_terminal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle terminal command."""
        return self.terminal_executor.execute(
            params['terminal_command'],
            shell=params.get('shell'),
            timeout=params.get('timeout')
        )

    def _handle_file_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file create command."""
        return self.file_manager.create_file(
            params['file_path'],
            content=params.get('content', ''),
            overwrite=params.get('overwrite', False)
        )

    def _handle_file_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file delete command."""
        return self.file_manager.delete_file(params['file_path'])

    def _handle_file_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file read command."""
        return self.file_manager.read_file(params['file_path'])

    def _handle_file_copy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file copy command."""
        return self.file_manager.copy_file(
            params.get('source_path'),
            params.get('dest_path'),
            overwrite=params.get('overwrite', False)
        )

    def _handle_file_move(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file move command."""
        return self.file_manager.move_file(
            params.get('source_path'),
            params.get('dest_path'),
            overwrite=params.get('overwrite', False)
        )

    def _handle_dir_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle directory create command."""
        return self.directory_manager.create_directory(params['dir_path'])

    def _handle_dir_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle directory delete command."""
        return self.directory_manager.delete_directory(
            params['dir_path'],
            recursive=params.get('recursive', False)
        )

    def _handle_dir_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle directory list command."""
        return self.file_browser.list_directory(
            params.get('dir_path', '.'),
            show_hidden=params.get('show_hidden', False)
        )

    def _handle_dir_navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle directory navigate command."""
        return self.directory_manager.navigate(params['dir_path'])

    def _handle_character_switch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle character switching command.

        This command needs to be routed to both:
        - ASR Service (for voice recognition personality)
        - LLM Service (for response personality)

        Args:
            params: Contains 'character_name' key

        Returns:
            Dictionary with success status
        """
        character_name = params.get('character_name', '')

        if not character_name:
            return {
                'success': False,
                'error': 'No character name provided'
            }

        # Store character preference
        self.preferences_manager.set('current_character', character_name)

        logger.info(f"Character switched to: {character_name}")

        # Return success - the actual routing to ASR/LLM will be handled by the main orchestrator
        return {
            'success': True,
            'character_name': character_name,
            'message': f"Character switched to {character_name}",
            'requires_service_notification': True,  # Signal that ASR/LLM need to be notified
            'notify_services': ['asr_service', 'llm_service']
        }

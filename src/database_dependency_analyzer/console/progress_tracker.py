"""Progress tracking and display for long-running operations."""

import logging
import sys
import time
from contextlib import contextmanager
from typing import Optional

from tqdm import tqdm


class ProgressTracker:
    """Tracks and displays progress for long-running operations.

    This class provides progress tracking capabilities using tqdm for
    console output and supports nested progress tracking for complex operations.
    """

    def __init__(self, enabled: bool = True, verbose: bool = False):
        """Initialize the progress tracker.

        Args:
            enabled: Whether progress tracking is enabled.
            verbose: Whether to enable verbose output.
        """
        self.enabled = enabled
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self._current_progress: Optional[tqdm] = None
        self._start_time = 0.0

    def start_operation(self, total: int, description: str = "Processing") -> Optional[tqdm]:
        """Start tracking progress for an operation.

        Args:
            total: Total number of items to process.
            description: Description of the operation.

        Returns:
            tqdm progress bar instance, or None if disabled.
        """
        if not self.enabled:
            return None

        self._start_time = time.time()

        # Disable tqdm if output is redirected or not a tty
        disable = not sys.stdout.isatty()

        self._current_progress = tqdm(
            total=total,
            desc=description,
            unit="items",
            disable=disable,
            leave=True,
            ncols=80
        )

        return self._current_progress

    def update(self, n: int = 1) -> None:
        """Update progress by n steps.

        Args:
            n: Number of steps to advance.
        """
        if self._current_progress:
            self._current_progress.update(n)

    def set_description(self, description: str) -> None:
        """Update the progress bar description.

        Args:
            description: New description.
        """
        if self._current_progress:
            self._current_progress.set_description(description)

    def finish_operation(self) -> float:
        """Finish the current operation and return elapsed time.

        Returns:
            Elapsed time in seconds.
        """
        if self._current_progress:
            self._current_progress.close()
            self._current_progress = None

        elapsed = time.time() - self._start_time
        self._start_time = 0.0

        if self.verbose:
            self.logger.debug(f"Operation completed in {elapsed:.2f} seconds")

        return elapsed

    @contextmanager
    def track_operation(self, total: int, description: str = "Processing"):
        """Context manager for tracking an operation.

        Args:
            total: Total number of items to process.
            description: Description of the operation.

        Yields:
            tqdm progress bar instance.
        """
        progress_bar = self.start_operation(total, description)
        try:
            yield progress_bar
        finally:
            self.finish_operation()

    def log_progress(self, current: int, total: int, message: str = "") -> None:
        """Log progress information.

        Args:
            current: Current progress value.
            total: Total progress value.
            message: Optional message.
        """
        if not self.enabled:
            return

        percentage = (current / total * 100) if total > 0 else 0

        log_message = f"Progress: {current}/{total} ({percentage:.1f}%)"
        if message:
            log_message += f" - {message}"

        self.logger.info(log_message)

    def create_subtracker(self, total: int, description: str = "Sub-operation") -> 'ProgressTracker':
        """Create a sub-tracker for nested operations.

        Args:
            total: Total for the sub-operation.
            description: Description for the sub-operation.

        Returns:
            New ProgressTracker instance.
        """
        return ProgressTracker(
            enabled=self.enabled,
            verbose=self.verbose
        )

    def show_message(self, message: str, level: str = "info") -> None:
        """Display a message to the user.

        Args:
            message: Message to display.
            level: Log level (info, warning, error).
        """
        if not self.enabled:
            return

        # Clear current progress bar temporarily
        if self._current_progress:
            self._current_progress.clear()

        if level == "info":
            print(f"ℹ️  {message}")
        elif level == "warning":
            print(f"⚠️  {message}")
        elif level == "error":
            print(f"❌ {message}")
        else:
            print(message)

        # Refresh progress bar
        if self._current_progress:
            self._current_progress.refresh()
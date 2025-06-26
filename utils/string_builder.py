from typing import Any, List

class StringBuilder:
    """A Python analog to StringBuilder for efficient string concatenation."""
    def __init__(self, initial: str = ""):
        """Initialize with an optional initial string."""
        self._buffer: List[str] = [initial] if initial else []

    def append(self, value: Any) -> "StringBuilder":
        """Append a value to the buffer, converting it to a string."""
        self._buffer.append(str(value))
        return self

    def clear(self) -> "StringBuilder":
        """Clear the buffer."""
        self._buffer.clear()
        return self

    def to_string(self) -> str:
        """Join all parts and return the final string."""
        return "".join(self._buffer)

    def __len__(self) -> int:
        """Return the number of characters in the current buffer."""
        return sum(len(part) for part in self._buffer)

    def __str__(self) -> str:
        """Return the string representation of the buffer."""
        return self.to_string()

    def __repr__(self) -> str:
        """Return a debug representation of the StringBuilder."""
        return f"StringBuilder(buffer={self._buffer})"
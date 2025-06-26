import json
from typing import List, Optional

from aiogram import html
from aiogram.types.bot_command import BotCommand
from pydantic import BaseModel, field_validator

from utils import StringBuilder


class CommandModel(BaseModel):
    name: str
    description: str

    @field_validator("name")
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Ensure command starts with '/' and is alphanumeric."""
        if not v.startswith("/"):
            v = f"/{v}"
        if not v[1:].isalnum():
            raise ValueError("Command must be alphanumeric after '/'")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Ensure description is non-empty."""
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class CommandList:
    """Manages a singleton list of Telegram bot commands."""

    _instance = None

    def __new__(cls, commands: Optional[List[BotCommand]] = None):
        """Ensure only one instance is created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(CommandList, cls).__new__(cls)
            # Initialize commands only for the first instance
            cls._instance.commands = commands or []
        return cls._instance

    @classmethod
    def get_instance(cls) -> "CommandList":
        """
        Get the singleton instance of CommandList.

        Returns:
            CommandList: The single instance of the class.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_from_json(self, file_path: str = "command_list.json") -> None:
        """
        Load bot commands from a JSON file and populate self.commands.

        Args:
            file_path (str): Path to the JSON file (default: 'command_list.json').

        Raises:
            FileNotFoundError: If the JSON file is not found.
            ValueError: If the JSON is invalid or contains invalid command data.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")

        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of commands")

        # Validate and convert JSON data to BotCommand objects
        self.commands = []
        for item in data:
            command_data = CommandModel(**item)
            bot_command = BotCommand(
                command=command_data.name, description=command_data.description
            )
            self.commands.append(bot_command)

    @staticmethod
    def format_commands(commands: List[BotCommand], separator: str = "\n") -> str:
        """
        Format a list of commands into a string.

        Args:
            commands (List[BotCommand]): List of BotCommand objects to format.
            separator (str): Separator between commands (default: newline).

        Returns:
            str: Formatted string of commands and descriptions.
        """
        if not commands:
            return "No commands available"

        builder = StringBuilder()
        for i, cmd in enumerate(commands, 1):
            builder.append(f"{i}.\t{cmd.command}\t\t{html.italic(cmd.description)}")
            if i < len(commands):
                builder.append(separator)
        return builder.to_string()

    def to_string(self, separator: str = "\n") -> str:
        """
        Format the instance's commands into a string.

        Args:
            separator (str): Separator between commands (default: newline).

        Returns:
            str: Formatted string of commands and descriptions.
        """
        return self.format_commands(self.commands, separator)

    def get_commands(self) -> List[BotCommand]:
        """Return the list of BotCommand objects."""
        return self.commands

    def __len__(self) -> int:
        """Return the number of commands."""
        return len(self.commands)

    def __repr__(self) -> str:
        """String representation of the CommandList."""
        return f"CommandList(commands={len(self.commands)} commands)"

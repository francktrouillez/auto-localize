import json

from .base import BaseFile

class JsonFile(BaseFile):
  """
  Class to handle JSON files.
  """
  @staticmethod
  def read(file_path: str) -> dict:
    """
    Read the contents of a JSON file.

    :param file_path: The path to the JSON file to read.
    :raise ParseError: If the file cannot be parsed as JSON.
    :return: The contents of the JSON file.
    """
    with open(file_path, "r") as file:
      try:
        content = json.load(file)
        if content is None:
          return {}
        return content
      except json.JSONDecodeError as error:
        raise BaseFile.ParseError from error

  @staticmethod
  def write(file_path: str, data: dict) -> None:
    """
    Write the contents to a JSON file.

    :param file_path: The path to the JSON file to write.
    :param data: The data to write to the JSON file.
    """
    JsonFile._ensure_directories_exist(file_path)
    with open(file_path, "w") as file:
      json.dump(data, file, indent=2)

  @staticmethod
  def touch(file_path: str) -> None:
    """
    Create an empty JSON file at the given path.

    :param file_path: The path to the JSON file to create.
    """
    JsonFile._ensure_directories_exist(file_path)
    with open(file_path, "w") as file:
      json.dump({}, file, indent=2)

  # --- Protected methods ---

  @staticmethod
  def _extension() -> str:
    """
    Get the file extension for JSON files.

    :return: The file extension for JSON files.
    """
    return "json"

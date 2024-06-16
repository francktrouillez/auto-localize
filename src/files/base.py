import os
import glob

class BaseFile:
  """
  Base class for file handling. This class is meant to be inherited by other classes that need to read and write files.
  """
  class ParseError(Exception):
    pass

  @staticmethod
  def read(_file_path: str) -> dict:
    raise NotImplementedError

  @staticmethod
  def write(_file_path: str, _data: dict) -> None:
    raise NotImplementedError

  @staticmethod
  def touch(file_path: str) -> None:
    """
    Create an empty file at the given path.

    :param file_path: The path to the file to create.
    """
    BaseFile._ensure_directories_exist(file_path)
    with open(file_path, "w"):
      pass

  @classmethod
  def files_matching_path(cls, path: str) -> list[str]:
    """
    Get a list of files that match the given path.

    :param path: The path to the file(s) to get.
    :return: A list of files that match the given path.
    """
    if os.path.isdir(path):
      if path.endswith("/"):
        return glob.glob(f"{path}**/*.{cls._extension()}", recursive=True)
      return glob.glob(f"{path}/**/*.{cls._extension()}", recursive=True)
    return glob.glob(path)

  @staticmethod
  def file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.

    :param file_path: The path to the file to check.
    :return: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)

  @staticmethod
  def find_missing_keys(source_dict: dict, target_dict: dict, current_key_path: list[str] = []) -> list[str]:
    """
    Find the keys that are missing in the target dictionary compared to the source dictionary.

    Works recursively to find missing keys in nested dictionaries.

    :param source_dict: The source dictionary to compare.
    :param target_dict: The target dictionary to compare.
    :param current_key_path: The current key path.
    :return: A list of keys that are missing in the target dictionary.
    """
    missing_keys = []
    for key, value in source_dict.items():
      if value is None:
        continue
      if type(value) == dict:
        missing_keys.extend(BaseFile.find_missing_keys(value, target_dict.get(key, {}), current_key_path + [key]))
      else:
        if key not in target_dict:
          missing_keys.append(current_key_path + [key])
    return missing_keys

  # --- Protected methods ---

  @staticmethod
  def _extension() -> str:
    raise NotImplementedError

  @staticmethod
  def _ensure_directories_exist(file_path: str) -> None:
    """
    Ensure that the directories for the given file path exist.

    :param file_path: The path to the file.
    """
    directories = file_path.split("/")[:-1]
    if directories:
      directories = "/".join(directories)
      os.makedirs(directories, exist_ok=True)

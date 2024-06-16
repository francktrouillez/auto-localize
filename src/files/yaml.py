import yaml

from .base import BaseFile

class YamlFile(BaseFile):
  """
  Class to handle YAML files.
  """
  @staticmethod
  def read(file_path: str) -> dict:
    """
    Read the contents of a YAML file.

    :param file_path: The path to the YAML file to read.
    :raise ParseError: If the file cannot be parsed as YAML.
    :return: The contents of the YAML file.
    """
    with open(file_path, "r") as file:
      try:
        content = yaml.safe_load(file)
        if content is None:
          return {}
        return content
      except yaml.YAMLError as error:
        raise BaseFile.ParseError from error

  @staticmethod
  def write(file_path: str, data: dict) -> None:
    """
    Write the contents to a YAML file.

    :param file_path: The path to the YAML file to write.
    :param data: The data to write to the YAML file.
    """
    YamlFile._ensure_directories_exist(file_path)
    with open(file_path, "w") as file:
      yaml.dump(data, file, sort_keys=False, default_flow_style=False)

  # --- Protected methods ---

  @staticmethod
  def _extension() -> str:
    """
    Get the file extension for YAML files.

    :return: The file extension for YAML files.
    """
    return "yml"

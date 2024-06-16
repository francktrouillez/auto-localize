from .yaml import YamlFile
from .json import JsonFile

class FileFactory:
  """
  Factory class to create file objects based on the file type
  """
  class UnsupportedFileException(Exception):
    pass

  @staticmethod
  def for_type(file_type: str):
    """
    Factory method to create the appropriate file object based on the file type

    :param file_type: The type of file to create
    :return: The appropriate file object
    """
    if file_type == "yaml" or file_type == "yml":
      return YamlFile
    if file_type == "json":
      return JsonFile
    raise FileFactory.UnsupportedFileException(f"File type {file_type} is not supported")

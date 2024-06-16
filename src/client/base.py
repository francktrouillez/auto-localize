import requests
import re

class BaseClient:
  """
  Base class for all translation clients. This class is meant to be inherited by other classes that need to translate text.
  """
  class ClientError(Exception):
    pass
  class InvalidApiKeyError(ClientError):
    pass
  class UnsupportedLanguageError(ClientError):
    pass
  class TranslationError(ClientError):
    pass
  class UsageError(ClientError):
    pass

  __DEFAULT_VARIABLE_PATTERN_STRING = '%{(.*?)}'
  __FIRST_CAPTURED_GROUP_PATTERN = r"\(([^()]*?)\)"

  def __init__(self, api_key: str, variable_pattern: str = None) -> None:
    self._api_key = api_key
    self._is_api_key_validated = False
    self._variable_pattern = re.compile(self.__DEFAULT_VARIABLE_PATTERN_STRING if not variable_pattern else variable_pattern)
    self._replacement_pattern = self.__generate_replacement_pattern()

  @staticmethod
  def generate_clients(_api_keys: list[str], _variable_pattern: str = None) -> list['BaseClient']:
    raise NotImplementedError

  @staticmethod
  def best_client(_clients: list['BaseClient']) -> 'BaseClient':
    raise NotImplementedError

  def translate(self, _texts: list[str], _source_language, _target_language: str) -> list[str]:
    raise NotImplementedError

  def validate_api_key(self) -> bool:
    raise NotImplementedError

  def usage(self) -> int:
    raise NotImplementedError

  # --- Protected methods ---

  def _get(self, *args, **kwargs) -> requests.Response:
    """
    Wrapper around requests.get.

    :param args: Positional arguments for requests.get.
    :param kwargs: Keyword arguments for requests.get.
    :return: The response from requests.get.
    """
    return requests.get(*args, **kwargs)

  def _post(self, *args, **kwargs) -> requests.Response:
    """
    Wrapper around requests.post.

    :param args: Positional arguments for requests.post.
    :param kwargs: Keyword arguments for requests.post.
    :return: The response from requests.post.
    """
    return requests.post(*args, **kwargs)

  # --- Private methods ---

  def __generate_replacement_pattern(self) -> str:
    """
    Generates a replacement pattern for the variable pattern.

    :return: The replacement pattern.
    """
    return self._variable_pattern.pattern.replace(re.search(self.__FIRST_CAPTURED_GROUP_PATTERN, self._variable_pattern.pattern)[0], r"\1")


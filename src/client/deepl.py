import re
import json

from .base import BaseClient

class DeeplClient(BaseClient):
  """
  Client for the DeepL API.
  """
  __USAGE_ENDPOINT = "/v2/usage"
  __TRANSLATE_ENDPOINT = "/v2/translate"
  __FREE_HOST = "api-free.deepl.com"
  __PREMIUM_HOST = "api.deepl.com"
  __VARIABLE_XML_TAG = "x"

  __SUPPORTED_SOURCE_LANGUAGES = ["AR", "BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI", "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH"]
  __SUPPORTED_TARGET_LANGUAGES = ["AR", "BG", "CS", "DA", "DE", "EL", "EN", "EN-GB", "EN-US", "ES", "ET", "FI", "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT", "PT-BR", "PT-PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH"]

  def __init__(self, api_key: str, variable_pattern: str = None) -> None:
    super().__init__(api_key=api_key, variable_pattern=variable_pattern)
    self.__is_api_key_free = None
    self.__source_languages_dictionary = {}
    self.__target_languages_dictionary = {}
    self.__remaining_characters = None

  @staticmethod
  def generate_clients(api_keys: list[str], variable_pattern: str = None) -> list['DeeplClient']:
    """
    Generates a list of clients for the DeepL API.

    :param api_keys: The API keys to generate clients for.
    :param variable_pattern: The pattern to match variables in the texts.
    :return: The list of clients.
    """
    return list(map(lambda api_key: DeeplClient(api_key=api_key, variable_pattern=variable_pattern), api_keys))

  @staticmethod
  def best_client(clients: list['DeeplClient']) -> 'DeeplClient':
    """
    Returns the client with the most remaining characters.

    :param clients: The clients to choose from.
    :return: The client with the most remaining characters.
    """
    clients_with_remaining_characters = list(filter(lambda client: client.usage() > 0, clients))
    if len(clients_with_remaining_characters) == 0:
      raise BaseClient.UsageError("No clients have remaining characters.")
    return max(clients_with_remaining_characters, key=lambda client: client.usage())

  def translate(self, texts: list[str], source_language: str, target_language: str) -> list[str]:
    """
    Translates a list of texts from a source language to a target language.

    :param texts: The texts to translate.
    :param source_language: The language of the texts.
    :param target_language: The language to translate the texts to.
    :return: The translated texts.
    """
    self.validate_api_key()
    return list(map(lambda text: self.__post_translate(texts=[text], source_language=source_language, target_language=target_language)[0], texts))

  def validate_api_key(self) -> None:
    """
    Validates the API key.

    :raises BaseClient.InvalidApiKeyError: If the API key is invalid.
    """
    if self._is_api_key_validated:
      return
    self.__detect_api_key_type()
    self._is_api_key_validated = True

  def usage(self) -> int:
    """
    Returns the number of remaining characters.

    :raises BaseClient.InvalidApiKeyError: If the API key is invalid.
    :return: The number of remaining characters.
    """
    self.validate_api_key()
    if self.__remaining_characters is None:
      self.__remaining_characters = self.__get_usage()
    return self.__remaining_characters

  # Private methods

  def __detect_api_key_type(self) -> None:
    """
    Detects if the API key is free or premium.

    :raises BaseClient.InvalidApiKeyError: If the API key is invalid.
    """
    if self.__is_api_key_free is not None:
      return
    for is_api_key_free in [True, False]:
      try:
        self.__ping(is_api_key_free=is_api_key_free)
        self.__is_api_key_free = is_api_key_free
        return
      except BaseClient.InvalidApiKeyError:
        pass
    raise BaseClient.InvalidApiKeyError("The API key is invalid.")

  def __ping(self, is_api_key_free: bool) -> None:
    """
    Pings the DeepL API.

    :param is_api_key_free: Whether the API key is free.
    :raises BaseClient.InvalidApiKeyError: If the API key is invalid.
    """
    self.__get_usage(is_api_key_free=is_api_key_free)

  def __url(self, endpoint: str, is_api_key_free: bool) -> str:
    """
    Returns the URL for an endpoint.

    :param endpoint: The endpoint.
    :param is_api_key_free: Whether the API key is free.
    :return: The URL.
    """
    return f"https://{self.__FREE_HOST if is_api_key_free else self.__PREMIUM_HOST}{endpoint}"

  def __usage_url(self, is_api_key_free: bool) -> str:
    """
    Returns the URL for the usage endpoint.

    :param is_api_key_free: Whether the API key is free.
    :return: The URL for the usage endpoint.
    """
    return self.__url(endpoint=self.__USAGE_ENDPOINT, is_api_key_free=is_api_key_free)

  def __translate_url(self, is_api_key_free: bool) -> str:
    """
    Returns the URL for the translate endpoint.

    :param is_api_key_free: Whether the API key is free.
    :return: The URL for the translate endpoint.
    """
    return self.__url(endpoint=self.__TRANSLATE_ENDPOINT, is_api_key_free=is_api_key_free)

  def __header_for_api_key(self) -> dict:
    """
    Returns the header for the API key.

    :return: The header for the API key.
    """
    return { "Authorization": f"DeepL-Auth-Key {self._api_key}" }

  def __header_for_content_type(self) -> dict:
    """
    Returns the header for the content type.

    :return: The header for the content type.
    """
    return { "Content-Type": "application/json" }

  def __get_usage(self, is_api_key_free: bool = None) -> dict:
    """
    Returns the usage of the API key.

    :param is_api_key_free: Whether the API key is free.
    :return: The usage of the API key.
    """
    if is_api_key_free is None:
      is_api_key_free = self.__is_api_key_free
    headers = self.__header_for_api_key()
    response = self._get(self.__usage_url(is_api_key_free=is_api_key_free), headers=headers)
    json_response = self.__handle_json_response(response)
    count = int(json_response["character_count"])
    limit = int(json_response["character_limit"])
    return limit - count

  def __post_translate(self, texts: list[str], source_language, target_language: str) -> dict:
    """
    Translates a list of texts from a source language to a target language.

    :param texts: The texts to translate.
    :param source_language: The language of the texts.
    :param target_language: The language to translate the texts to.
    :return: The translated texts.
    """
    headers = self.__header_for_api_key() | self.__header_for_content_type()
    data = self.__generate_body_for_translate(texts=texts, source_language=source_language, target_language=target_language)
    characters_count = len("".join(data["text"]))
    if (self.usage() < characters_count):
      raise BaseClient.UsageError("The API key does not have enough characters remaining.")
    response = self._post(self.__translate_url(self.__is_api_key_free), headers=headers, data=json.dumps(data))
    json_response = self.__handle_json_response(response)
    translated_texts = map(lambda translation: self.__format_text_from_api(translation["text"]), json_response["translations"])
    self.__remaining_characters -= characters_count
    return list(translated_texts)

  def __generate_body_for_translate(self, texts: list[str], source_language: str, target_language: str) -> dict:
    """
    Generates the body for the translate endpoint.

    :param texts: The texts to translate.
    :param source_language: The language of the texts.
    :param target_language: The language to translate the texts to.
    :return: The body for the translate endpoint.
    """
    return {
      "text": list(map(lambda text: self.__format_text_for_api(text), texts)),
      "source_lang": self.__get_formatted_source_language_for_api(source_language),
      "target_lang": self.__get_formatted_target_language_for_api(target_language),
      "tag_handling": "xml",
      "ignore_tags": [self.__VARIABLE_XML_TAG]
    }

  def __format_text_for_api(self, text: str) -> str:
    """
    Formats the text for the API.

    :param text: The text to format.
    :return: The formatted text.
    """
    return re.sub(self._variable_pattern, lambda match: f"<{self.__VARIABLE_XML_TAG}>{match.group(1)}</{self.__VARIABLE_XML_TAG}>", text)

  def __format_text_from_api(self, text: str) -> str:
    """
    Formats the text from the API.

    :param text: The text to format.
    :return: The formatted text.
    """
    pattern = re.compile(f"<{self.__VARIABLE_XML_TAG}>(.*?)</{self.__VARIABLE_XML_TAG}>")
    return re.sub(pattern, self._replacement_pattern, text)

  def __get_formatted_target_language_for_api(self, language: str) -> str:
    """
    Returns the formatted target language for the API.

    :param language: The target language.
    :raises BaseClient.UnsupportedLanguageError: If the target language is not supported.
    :return: The formatted target language for the API.
    """
    if language not in self.__target_languages_dictionary:
      self.__target_languages_dictionary[language] = self.__format_target_language_for_api(language)
    return self.__target_languages_dictionary[language]

  def __format_target_language_for_api(self, language: str) -> str:
    """
    Formats the target language for the API.

    :param language: The target language.
    :raises BaseClient.UnsupportedLanguageError: If the target language is not supported.
    :return: The formatted target language for the API.
    """
    formatted_language = language.upper().replace("_", "-")
    if formatted_language in self.__SUPPORTED_TARGET_LANGUAGES:
      return formatted_language
    formatted_language = formatted_language.split("-")[0]
    if formatted_language in self.__SUPPORTED_TARGET_LANGUAGES:
      return formatted_language
    raise BaseClient.UnsupportedLanguageError(f"The target language '{language}' is not supported.")

  def __get_formatted_source_language_for_api(self, language: str) -> str:
    """
    Returns the formatted source language for the API.

    :param language: The source language.
    :raises BaseClient.UnsupportedLanguageError: If the source language is not supported.
    :return: The formatted source language for the API.
    """
    if language not in self.__source_languages_dictionary:
      self.__source_languages_dictionary[language] = self.__format_source_language_for_api(language)
    return self.__source_languages_dictionary[language]

  def __format_source_language_for_api(self, language: str) -> str:
    """
    Formats the source language for the API.

    :param language: The source language.
    :raises BaseClient.UnsupportedLanguageError: If the source language is not supported.
    :return: The formatted source language for the API.
    """
    formatted_language = language.upper().replace("_", "-")
    if formatted_language in self.__SUPPORTED_SOURCE_LANGUAGES:
      return formatted_language
    formatted_language = formatted_language.split("-")[0]
    if formatted_language in self.__SUPPORTED_SOURCE_LANGUAGES:
      return formatted_language
    raise BaseClient.UnsupportedLanguageError(f"The source language '{language}' is not supported.")

  def __handle_json_response(self, response) -> dict:
    """
    Handles a JSON response.

    :param response: The response.
    :raises BaseClient.InvalidApiKeyError: If the API key is invalid.
    :raises BaseClient.ClientError: If the client has an exception.
    :return: The JSON response.
    """
    if response.status_code == 403:
      raise BaseClient.InvalidApiKeyError
    if response.status_code != 200:
      raise BaseClient.ClientError(f"Client exception: {response.text}")
    return response.json()

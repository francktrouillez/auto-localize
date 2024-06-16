from .deepl import DeeplClient

class ClientFactory:
  """
  Factory class to create the appropriate client based on the API type
  """
  class UnsupportedClientError(Exception):
    pass

  @staticmethod
  def for_type(api_type: str):
    """
    Factory method to create the appropriate client based on the API type

    :param api_type: The type of client to create
    :return: The appropriate client
    """
    if api_type == "deepl":
      return DeeplClient
    raise ClientFactory.UnsupportedClientError(f"Client '{api_type}' is not supported")

from client.base import BaseClient

def generate_target_translation(source_translation: list[str] | str, source_file: str, source_language: str, target_language: str, target_translations: dict[str, str], client_class: BaseClient, clients: list['BaseClient']) -> list[str] | str:
  """
  Generate the target translation for the given source translation.

  :param source_translation: The source translation to generate the target translation for.
  :param source_file: The path to the source file.
  :param source_language: The source language of the translation.
  :param target_language: The target language of the translation.
  :param target_translations: The translations that have already been generated.
  :param client_class: The client class to use for translation.
  :param clients: The clients to use for translation.
  :return: The target translation for the given source translation.
  """
  if type(source_translation) == list:
    target_translation = []
    for value in source_translation:
      if value not in target_translations:
        print(f"[{source_file} - {target_language}] Translating '{value}' from '{source_language}' to {target_language}")
        target_translations[value] = client_class.best_client(clients).translate(texts=[value], source_language=source_language, target_language=target_language)[0]
      target_translation.append(target_translations[value])
  else:
    if source_translation not in target_translations:
      print(f"[{source_file} - {target_language}] Translating '{source_translation}' from '{source_language}' to {target_language}")
      target_translations[source_translation] = client_class.best_client(clients).translate(texts=[source_translation], source_language=source_language, target_language=target_language)[0]
    target_translation = target_translations[source_translation]
  return target_translation

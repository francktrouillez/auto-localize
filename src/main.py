import os
from functools import reduce

from client.factory import ClientFactory
from files.factory import FileFactory

from utils import generate_target_translation

# --- Environment variables ---

SOURCE_LANGUAGE = os.environ["SOURCE_LANGUAGE"]
TARGET_LANGUAGES = os.environ["TARGET_LANGUAGES"].split(",")
VARIABLE_PATTERN = os.environ["VARIABLE_PATTERN"]
SOURCE_FILES_DIRECTORY = os.environ["SOURCE_FILES_DIRECTORY"]
TARGET_FILES_DIRECTORY = os.environ["TARGET_FILES_DIRECTORY"]
API_KEYS = os.environ["API_KEYS"].split(",")
FILE_TYPE = os.environ["FILE_TYPE"]
API_TYPE = os.environ["API_TYPE"]

# --- Main script ---

client_class = ClientFactory.for_type(API_TYPE)
file_class = FileFactory.for_type(FILE_TYPE)

clients = client_class.generate_clients(api_keys=API_KEYS, variable_pattern=VARIABLE_PATTERN)
source_files = file_class.files_matching_path(SOURCE_FILES_DIRECTORY.replace("{language}", SOURCE_LANGUAGE))

for source_file in source_files:
  source_data = file_class.read(source_file)
  for target_language in TARGET_LANGUAGES:
    print(f"[{source_file} - {target_language}] Translating file '{source_file}' to '{target_language}'")
    target_file = source_file.replace(SOURCE_FILES_DIRECTORY.replace("{language}", SOURCE_LANGUAGE), TARGET_FILES_DIRECTORY.replace("{language}", target_language))
    if not file_class.file_exists(target_file):
      file_class.touch(target_file)
    target_data = file_class.read(source_file.replace(SOURCE_FILES_DIRECTORY.replace("{language}", SOURCE_LANGUAGE), TARGET_FILES_DIRECTORY.replace("{language}", target_language)))
    missing_keys = file_class.find_missing_keys(source_data, target_data)
    print(f"[{source_file} - {target_language}] Missing keys: {missing_keys}")
    target_translations = {}
    for keys in missing_keys:
      source_translation = reduce(lambda data, key: data[key], keys, source_data)
      target_translation = generate_target_translation(
        source_translation=source_translation,
        source_file=source_file,
        source_language=SOURCE_LANGUAGE,
        target_language=target_language,
        target_translations=target_translations,
        client_class=client_class,
        clients=clients
      )
      target_translation_data = target_data
      for key in keys[:-1]:
        if type(target_translation_data.get(key)) != dict:
          target_translation_data[key] = {}
        target_translation_data = target_translation_data.setdefault(key, {})
      target_translation_data[keys[-1]] = target_translation
    print(f"[{source_file} - {target_language}] Writing translations to '{target_file}'")
    file_class.write(target_file, target_data)

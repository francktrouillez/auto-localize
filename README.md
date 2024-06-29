# Auto-Localize Action

This action generates localized strings for a given project based on the source language. It first parses the source language localized files, then detect the missing keys in the target languages that will then be ingested by a translation API to generate the localized strings. Once the localized strings are generated, they are then saved in the target language files.

## Supported file formats
- JSON
- YAML

## Supported translation APIs
- [DeepL API](https://www.deepl.com/en/pro-api)

## Inputs

### `source_language`
**required** The source language of the text to translate.
### `target_languages`
**required** The target languages to translate the text to. Comma-separated if multiple languages are used.
### `source_files_directory`
**required** The directory containing the source files to translate. You can use `{language}` as a placeholder for the source language.
### `target_files_directory`
**required** The directory where the translated files will be saved. You can use `{language}` as a placeholder for the target language.
### `api_keys`
**required** The API key(s) for the API. Comma-separated if multiple keys are used.
### `api_type`
**optional**(default: `deepl`) The type of the translation API.
### `variable_pattern`
**optional**(default: `%{(.*?)}`) The pattern to use to identify the variables in the source files. **Use a regex group to capture the variable name**, like `%{(.*?)}` for instance.
### `file_type`
**optional**(default: `yaml`) The file type of the source files.
### `prune_useless_keys`
**optional**(default: `true`) Whether to prune the keys that are not present in the source language files.


## Example usage

```yaml
name: Localize
on:
  push:
    branches:
      - main

jobs:
  localize:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    - name: Localize
      uses: francktrouillez/auto-localize@v1
      with:
        source_language: 'en'
        target_languages: 'fr,de'
        source_files_directory: 'src/locales/{language}'
        target_files_directory: 'src/locales/{language}'
        api_keys: ${{ secrets.DEEPL_API_KEY }}
        api_type: 'deepl'
        variable_pattern: '%{(.*?)}'
        file_type: 'yaml'
        prune_useless_keys: 'true'
    - name: Commit and push
      run: |
        git config --local user.email "auto-localize@github-actions.com"
        git config --local user.name "Auto Localize Action"
        git add .
        git commit -m "[AL] Add localized strings"
        git push
```

## Troubleshooting

If you are having permission issues, make sure the [action has the permission to write in the repository](https://docs.github.com/en/actions/using-jobs/assigning-permissions-to-jobs).

## Contributions

Contributions are welcome! Feel free to open an issue or submit a pull request if you have any ideas or improvements for the action, or if you wanna add support for a new translation API or file format.

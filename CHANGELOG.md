# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2024-08-13

### Fixed

- Both personas messages were appended together.

## [0.4.3] - 2024-08-13

### Fixed

- Missing `tabulate` library.

## [0.4.2] - 2024-08-13

### Changed

- Create release before workflow

### Fixed

- Cloud run version variable error.

## [0.4.1] - 2024-08-13

### Fixed

- Cloud run version can only take dashes not dots.

## [0.4.0] - 2024-08-13

### Added

- Chatbot interface to Data Analyst persona.
- Logger setup.

### Fixed

- Push all tags to docker image in artifact registry.

### Changed

- Add tag to cloud run revision.

### Removed

- AutoViz for visualization.

## [0.3.0] - 2024-07-19

### Added

- New datasets onlinebehaviour.
- Chatbot functionality for business analyst persona.
- Unit tests for `schema_manager`, `query_formatter`, `chat_manager` classes.
- Examples for sql prompt.
- Metadata information in schema and dataset_info.

### Fixed

- Multiple system instruction calls.
- MultipleExplores, Dimension, Measure looker api calls.

### Changed

- Use streamlit for user interface instead of gradio
- Entry point to `Home.py`.

### Removed

- Unused notebooks Chatbot.ipynb, looker.ipynb.
- Version handler Gitversion.yml.

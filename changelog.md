# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.30] - 2025-12-10
### Added
- No adds.

### Changed
- No changes.

### Removed
- Remove payload from logging.

## [2.1.25] - 2025-09-10
### Added
- No adds.

### Changed
- Fix password validation error for empty passwords.

### Removed
- No removes

## [2.1.25] - 2025-09-10
### Added
- Add is_superuser and is_service_user policies.
- Function to create service registration base to be used on Auth App
  route registration on Kong.
- Add end-point to clear local diskcache.
- Add end-point to create new users by superuser admin.

### Changed
- Fix scope change when using Entra.

### Removed
- No removes

## [2.1.17] - 2025-09-10

### Added
- No add.

### Changed
- Fix scope change when using Entra.

### Removed
- No removes

## [2.1.13] - 2025-09-10

### Added
- No add.

### Changed
- Fix permission cache.

### Removed
- No removes

## [2.1.6] - 2025-09-10

### Added
- Add cache to permission and token check.

### Changed
- Refactor code.

### Removed
- No removes

## [2.1.5] - 2025-09-10

### Added
- Create migration to remove unique from kong_id.

### Changed
- No changes

### Removed
- No removes


## [2.0.X] - 2025-06-26

### Added
- Created model for fixtures testing row permission.

### Changed
- No changes

### Removed
- No removes

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.63] - 2026-08-26

### Fixed
- ``custom_exception_handler`` — wrap ``TreatPsycopg2Error.treat`` payload
  in a DRF ``Response`` (fixes ``AttributeError: 'dict' object has no
  attribute 'exception'`` on database errors).
- ``custom_exception_handler`` — return a ``Response`` for Django
  ``FieldError`` (previously fell through without a response).
- ``custom_exception_handler`` — use ``pump_exc.status_code`` when mapping
  DRF exceptions to PumpWood payloads.

### Changed
- ``custom_exception_handler`` — replace ``elif`` chain with independent
  ``if`` branches and delegate unhandled exceptions to DRF's default
  handler.

## [2.1.62-b.0] - 2026-08-20

### Changed
- ``SerializerUser`` — remove ``api_permission_set``,
  ``row_permission_set``, ``mfa_method_set``, ``mfa_token_set``, and
  ``recovery_codes_set`` from login payloads; effective permissions
  remain on nested ``user_profile.self_*`` fields.
- ``ApiPermissionAux``, ``RowPermissionAux``, ``UserProfile`` permission
  actions, and registration serializers — docstrings and return types
  aligned with actual behavior.

## [2.1.61-b.0] - 2026-08-20

### Added
- ``SerializerUserProfile`` — ``self_api_permissions`` and
  ``self_row_permissions`` resolved through ``UserProfile`` actions.

### Changed
- ``LoginView``, ``CodeLoginView``, and ``SSOLoginView`` — return full
  ``SerializerUser`` with ``foreign_key_fields``, ``related_fields``,
  and request context on successful authentication.
- ``retrieve_authenticated_user`` — aligned with the same serializer
  options.

### Fixed
- ``group_user_api_permissions.sql`` — remove invalid ``WHERE`` after
  ``GROUP BY`` and qualify ``user_m2m.user_id`` (broke
  ``UserProfile.user_api_permissions`` on ``create_user``).

### Removed
- Unreachable return block after ``PumpwoodMFAMethod.run_method`` raises
  for unimplemented MFA types.

## [2.1.60-b.0] - 2026-07-14

### Changed
- ``groups`` migration ``0005_pumpwoodusergroup_code`` — add ``code``
  field before backfill ``RunPython`` step.

## [2.1.59-b.0] - 2026-07-14

### Changed
- ``groups`` migration ``0005_pumpwoodusergroup_code`` — backfill
  ``PumpwoodUserGroup.code`` from slugified description and enforce
  unique non-blank codes.

## [2.1.58-b.0] - 2026-07-14

### Changed
- ``register_auth_kong_objects`` — call ``cls_fields_options()`` without
  ``translate=False`` when building Kong search options.
- Reformat ``changelog.md`` release history (image tags through
  ``2.1.57-b.0``).

## [2.1.57-b.0] - 2026-07-13
### Added
- ``aux.general.django_apps_ready`` helper for deferred local i18n.
- ``PumpwoodAuthActionRoleCache`` and ``PumpwoodAuthHasPermissionCache``
  dataclasses for permission cache keys.
- ``PumpwoodAuthTranslationCache`` dataclass for i18n cache keys.
- ``PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION``,
  ``PUMPWOOD_AUTH__TOKEN_CACHE_EXPIRATION``, and
  ``PUMPWOOD_AUTH__ROW_PERMISSION_CACHE_EXPIRATION`` configuration.

### Changed
- Permission and translation caches use ``default_cache`` from
  ``pumpwood-communication`` with typed dataclass keys.
- ``config`` initializes ``pumpwood_i8n`` with the local i18n model and
  ``django_apps_ready`` callback instead of the microservice backend.
- ``MapPathRoleAux`` prefers ``PumpwoodDjangoAppInspect`` local lookups
  before microservice calls.
- Rename application config class to ``PumpwoodDjangoAuthConfig``.
- Update README and package docstrings; remove Metabase references.

### Removed
- ``gunicorn_hooks`` module.
- ``pumpwood_djangoauth.i8n.translate`` compatibility shim.

## [2.1.56-b.0] - 2026-07-09
### Added
- No adds.

### Changed
- ``KongService`` model drops Metabase dashboard relations.

### Removed
- ``pumpwood_djangoauth.metabase`` app, template tags, migrations, and
  generated docs. Remove ``pumpwood_djangoauth.metabase`` from
  ``INSTALLED_APPS`` in consuming projects. Existing DB tables
  ``metabase__dashboard`` and ``metabase__dashboard_parameter`` are no
  longer managed by this package.

## [2.1.55-b.0] - 2026-07-09
### Added
- No adds.

### Changed
- ``MapPathRoleAux`` resolves actions locally via
  ``PumpwoodDjangoAppInspect.list_actions_local`` before calling the
  microservice.
- Raise ``PumpWoodObjectDoesNotExist`` when a model class is not
  registered locally or remotely.

### Removed
- No removes.

## [2.1.54-b.0] - 2026-07-09
### Added
- ``PumpwoodDjangoAuthConfig`` application config in ``apps.py``.
- ``gunicorn_hooks.post_fork`` calling ``reset_config_singletons``.

### Changed
- Migration ``0022`` backfills ``code`` on ``PumpwoodPermissionPolicy``
  and ``PumpwoodPermissionPolicyAction`` from slugified description or
  action names.

### Removed
- No removes.

## [2.1.53-b.0] - 2026-06-30
### Added
- ``LazyProxy`` for deferred singleton initialization.
- ``reset_config_singletons()`` for gunicorn worker fork lifecycle.
- ``DISKCACHE_SIZE_LIMIT`` and ``DISKCACHE_EXPIRATION`` configuration.

### Changed
- Wrap Kong, microservice, storage, RabbitMQ, disk cache, and i18n
  singletons in ``LazyProxy`` so network clients open on first use.

### Removed
- No removes.

## [2.1.52] - 2026-06-29
### Added
- No adds.

### Changed
- Allow `null=True` on `code` for `PumpwoodPermissionPolicy` and
  `PumpwoodPermissionPolicyAction`, and update migration `0022`.

### Removed
- No removes.

## [2.1.51] - 2026-06-26
### Added
- No adds.

### Changed
- Fix `register_auth_kong_objects` to initialise `temp_routes` from the
  routes argument before appending viewset routes.

### Removed
- No removes.

## [2.1.50] - 2026-06-26
### Added
- No adds.

### Changed
- Remove random startup delay from `register_auth_kong_objects`.

### Removed
- Remove `dev_build.sh`, `dev_requirements.txt` and `mk_docs.py`.

## [2.1.49] - 2026-06-18
### Added
- Add `service_registration` module with default auth service and route
  definitions.
- Add service admin actions to load, reload Kong services and generate API
  documentation spreadsheets.
- Add unique `code` field to `PumpwoodPermissionPolicy` and
  `PumpwoodPermissionPolicyAction`.
- Add groups and row permission module docstrings for pdocs.
- Add `pyproject_template.toml` and migrate package build to Poetry.

### Changed
- Update README with permission apps, URL includes and permission codes
  section.
- Fix `register_auth_kong_objects` to default missing route `extra_info`
  to an empty dict.
- Add legacy compatibility for Flask services.
- Adjust empty variable handling on Microsoft Entra SSO.
- Extend system models with route documentation generation support.

### Removed
- Remove `setup.py` and `setup_template.py` in favour of Poetry build.

## [2.1.43] - 2026-03-02
### Added
- Add unique `code` field to `PumpwoodUserGroup` model, serializer and admin.
- Document permission codes on README and model docstrings.

### Changed
- Expose `code` on user group and row permission admin screens.
- Correct `verbose_name` and `help_text` on `PumpwoodRowPermission.code`.

### Removed
- No removes.

## [2.1.42] - 2026-03-02
### Added
- Add full name to user serializer default fields and as display field for
  other ForeignKey.

### Changed
- No changes.

### Removed
- No removes.

## [2.1.41] - 2026-03-02
### Added
- Add full name to user serializer.

### Changed
- No changes.

### Removed
- No removes.

## [2.1.40] - 2026-03-02
### Added
- Add code to identify the row permission as unique.

### Changed
- No changes.

### Removed
- No removes.

## [2.1.39] - 2026-02-22
### Added
- Allow set proxy for OAuth2Session calls using `PUMPWOOD__SSO__PROXY_HTTP`
  and `PUMPWOOD__SSO__PROXY_HTTPS`.

### Changed
- No changes.

### Removed
- No removes.

## [2.1.38] - 2026-02-22
### Added
- No adds.

### Changed
- Correct doc generation.

### Removed
- No removes.

## [2.1.37] - 2026-02-19
### Added
- No adds.

### Changed
- Correct the logging of incorrect authentication.

### Removed
- No removes.

## [2.1.35] - 2026-02-15
### Added
- Add actions to route documentation.

### Changed
- No changes.

### Removed
- No removes.

## [2.1.35] - 2026-02-15
### Added
- Add actions to route documentation.

### Changed
- No changes.

### Removed
- No removes.

## [2.1.31] - 2026-02-15
### Added
- Add admin action to generate the documentation of the models.

### Changed
- Update pumpwood packages.

### Removed
- No removes.

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

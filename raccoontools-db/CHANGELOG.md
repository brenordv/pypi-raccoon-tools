# Changelog

## [1.1.0]

### Changed
- Dependencies updated: `psycopg[binary,pool]` 3.3.6, `simple-log-factory` 2.0.0, `idna` 3.20, and the optional
  `simple-log-factory-ext-otel` extras to 2.0.0. The `idna` security pin is now a floor (`>=`).
- Packaging uses an SPDX license expression (`license = "MIT"`); the deprecated license table and classifier are gone.
- Dev dependencies moved from the published `dev` extra to the `dev` dependency group, with ruff, mypy and pytest-cov.

### Fixed
- `PoolConfig`'s `repr` no longer includes `conn_info`, which usually carries the database password.
- `create_pool()` opens the pool explicitly (`open=False`, then `open()`), which avoids the psycopg_pool warning about
  implicit opening in the constructor. If `open()` fails, the module keeps no reference to the pool, so
  `get_pool()` reports that no pool exists and `create_pool()` can be called again.

## [1.0.1]
- Security update. Added `idna` as explicit dependency to address security vulnerabilities surfaced by the use of `requests`. Will remove as soon as `requests` catches up.

## [1.0.0]
- Initial version of the package

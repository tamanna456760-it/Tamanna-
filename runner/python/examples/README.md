# Legacy Python runner and examples

This is a legacy compatibility area, not the canonical application package. The supported product implementation is in the repository root and `tamanna_ai/`.

## Examples

Examples are side-effect free when imported. Run explicitly:

```sh
python runner/python/examples/api_client_demo.py
python runner/python/examples/tamanna_chaos_demo.py
```

The API demo makes outbound requests only when executed. It is not the production chat provider.

## Vendor-layout audit

The legacy folder contains roughly 1,020 Python files in a flat directory. Source headers identify third-party distributions including Requests, SQLAlchemy, wheel/setuptools and other packages mixed with Tamanna-specific prototypes. Package directories and relative-import boundaries are missing or flattened; some vendor files use package-relative imports that cannot resolve from this flat directory.

Do not bulk move these files or add this directory to the production import path. Reconstruct each third-party package from its upstream distribution and license metadata before vendoring it under a proper package directory. New production code belongs in `tamanna_ai/`, with dependencies declared in the root requirements files.

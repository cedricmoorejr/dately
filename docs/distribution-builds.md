# Distribution builds

`dately` contains seven Cython extensions. Each Windows wheel must therefore be
built for its target CPython ABI; a CPython 3.8 `.pyd` cannot be placed in a
3.9–3.13 wheel or advertised as `py3-none-any`.

## Supported downloads

The build configuration targets 64-bit Windows and CPython 3.8 through 3.14.
The `Build Python downloads` GitHub Actions workflow produces:

- `dately-<version>-cp38-cp38-win_amd64.whl`
- `dately-<version>-cp39-cp39-win_amd64.whl`
- `dately-<version>-cp310-cp310-win_amd64.whl`
- `dately-<version>-cp311-cp311-win_amd64.whl`
- `dately-<version>-cp312-cp312-win_amd64.whl`
- `dately-<version>-cp313-cp313-win_amd64.whl`
- `dately-<version>-cp314-cp314-win_amd64.whl`
- `dately-<version>.tar.gz`

The workflow installs and runs the regression suite against every wheel under its
matching interpreter. It also validates wheel and source metadata with `twine`
before uploading the artifacts.

## Building locally

Install a Windows C compiler compatible with the selected Python installation,
then run:

```console
python -m pip install build
python -m build
```

PEP 517 installs the appropriate Cython build dependency automatically. The
checked-in `.pyx` files are authoritative. Generated Cython C files and compiled
extension binaries are build artifacts and are not kept in the repository.

## Release procedure

Update `_version.py`, commit the release, and push the matching `v<version>` tag.
The workflow rejects tags that do not match the package version. Download each
workflow artifact, verify that all seven wheel filenames and the source archive
are present, and then upload those unchanged files to the release and PyPI.
Publishing credentials are intentionally not stored in this repository.

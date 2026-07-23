

# Publishing 

Publishing is done using [uv](https://docs.astral.sh/uv/) with the hatchling build backend.

reqs: 
 - uv installed and on path
   `pipx install uv`  (or see https://docs.astral.sh/uv/getting-started/installation/)

 - the `bump-my-version` tool is run on demand via `uvx bump-my-version`

 - a PyPI API token, provided via environment variable:
    - **PyPI test**
        - get token from https://test.pypi.org/manage/account/token/
        - publish with `uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-YYYYYYYY`
    - **PyPI Production**
        - get token from https://pypi.org/manage/account/token/
        - set `UV_PUBLISH_TOKEN=pypi-XXXXXXXX` (or pass `--token`)


 - bump version (updates the package source, `package.json` and `mip/*.json`)

    `uvx bump-my-version bump pre_release` 
    `uvx bump-my-version bump patch` 

 - build & publish 
    `uv build` 
    `uv publish --publish-url https://test.pypi.org/legacy/`   # test PyPI 
    `uv publish`                                                # production PyPI 



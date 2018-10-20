
# Docgenerator

Docgenerator processes all markdown files in a Git repository, creates a summary.md file, and optionally uses the PDF generator for GitBook to produce a PDF.

# install required components

```
js 'j.tools.docgenerator.install()'
```

- IMPORTANT: need to check if all right plugins are installed of caddy e.g. the filemanager, if not do it manually

# process the data

- [process](process.md)

# Metadata

## config.toml

- in root of each .doc directory there needs to be a config.toml
    - this config file is the hugo config file but also has some arguments for our own generation (see below)
- our own arguments
    - depends (will fetch & process other mentioned locations, can be subsection of a repo or full branch)
    - name is meaning full name of the Documentation part e.g js8_defs
    - description e.g. definitions of jumpscale

```toml
name = "js8_lots"
description = "some description"
depends = ["https://github.com/Jumpscale/jumpscale_core8/tree/8.1.2/docs",
    "https://github.com/Jumpscale/jscockpit",
    "https://github.com/Jumpscale/ays_jumpscale8/tree/8.2.0"]
theme = "hugo-future-imperfect"
```


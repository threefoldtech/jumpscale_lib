
# Docgenerator

Docgenerator processes all markdown files in a Git repository, creates a summary.md file, and optionally uses the PDF generator for GitBook to produce a PDF.

## Arguments

- outdirectory
- url of site where docs will be

## Preprocess

- Docgenerator walks over all directories below a dir
- Docgenerator remembers when a .git repository and gets the URL path
- Docgenerator identifies following types of dirs
    - macros
        - each dir called macros is considered to be a macros dir
    - documentation
        - file ```.docgenerator``` is in the root of such a dir
        - files in here can be definitions, documents, blogs, ...
        - config.yaml defines how to deal with the info in such a directory
    - the directories are remembered together with their git counterparts
- Now all macro's are loaded
- Now all filenames are remembered (this is to let the include work)

## Process per doc directory (as found in previous step)

- Walk over files in directory (recursive)
- When config.yaml overload previous one
- Copy files to outdirectory
    - $outdir/$sitename/src
- Walk over the files and for each file
    - make sure config.yaml as well as meta data info in file is loaded (is a big dict)
    - use mustache template engine to replace the arguments
    - execute the macro's & mustache again (recursive until no more macro's to be processed)
- Per site do the production step
    - lookup template used, copy inside $outdir/$sitename
    - use hugo or ... to generate the site

## Metadata

## config.yaml

- in root of each .docgenerator directory there can be a config.yaml
- depends (will fetch & process other mentioned locations, can be subsection of a repo or full branch)
- name is meaning full name of the Documentation part e.g js8_defs
- description e.g. definitions of jumpscale
```
name: js8_lots
depends:
    - https://github.com/Jumpscale/jumpscale_core9/tree/8.1.2/docs
    - https://github.com/Jumpscale/jscockpit
    - https://github.com/Jumpscale/ays_jumpscale9/tree/8.2.0
```

```
!!!
title = "Docgenerator"
date = "2017-04-08"
tags = []
```

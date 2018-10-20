# process

## arguments are

- outdirectory: ```j.tools.docgenerator.outdir=...```
- url of site where docs will be: ```j.tools.docgenerator.webserver=...```

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


## Process

- walk over files in directory (recursive)
- for each dir we will check
    - data.toml
    - default.md
- these are remembered and will be applied on each markdown document (so you have hugo template variables available)
- walk over the .md files and for each file
    - execute the macro's  (recursive until no more macro's to be processed)
    - the aggregated data (is a dict) is put as toml metadata at beginning of the markdown document
    - use jinja2 template engine to replace the arguments
- write resulting .md files to outdirectory/$sitename/content/...
    - this depends on the template used, std is a neutral template with no branding
- per site do the production step
    - lookup template used, copy inside $outdir/$sitename
    - use hugo or ... to generate the site (depends on the generate.py which is put in the template dir)


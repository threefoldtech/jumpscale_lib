
## macro's

are structured as code blocks in markdown

format:  !!!$macroname($args)

example:

```
!!!include("ays9:events")
```

the first line is the macroname with arguments

everything below is given as payload to the macro itself

it can also be in a code block, where first line is above and then the data below is given to the macro (raw)
so the macro can decide what to do with it.



## example of a macro

```python
def include(doc, name, **args):
    name = name.lower()

    if name.find(":") == -1:
        doc = doc.docsite.doc_get(name, die=False)
        if doc != None:
            doc.process()
            newcontent = doc.content
        else:
            newcontent = "ERROR: COULD NOT INCLUDE:%s (not found)" % name

    else:
        docsiteName, name = name.split(":")
        docsite = j.tools.docgenerator.docsite_get(docsiteName)
        doc = docsite.doc_get(name, die=False)
        if doc != None:
            doc.process()
            newcontent = doc.content
        else:
            newcontent = "ERROR: COULD NOT INCLUDE:%s:%s (not found)" % (docsiteName, name)
```

this is the include macro

the arguments to a macro are doc and then the arguments

in this case the first argument is the name, and the others are just caught on **args

you can also see how a document can be retrieved from the docsite




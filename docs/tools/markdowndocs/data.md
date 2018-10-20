## doc.data

data.toml or data.yaml can be in each level in the directory structure.

On each doc there will be a doc.data

this is the aggregated data off

- data in parent dirs
- data in the dir itself
- data in the document itself

## format of data block in a document

example

```toml
!!!data
something = 11
```

the first line with !!!data is important, this shows that this is data stored in a code block



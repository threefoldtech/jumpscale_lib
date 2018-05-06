# How to Use ByteProcessor


To compress a simple string using blosc compression:

```python
input = bytearray()
input.extend(map(ord, 'hello jumpscale'))
output = j.tools.byteprocessor.compress(input)
j.tools.byteprocessor.decompress(output)
```

Other compression algorithms are also available:

```python
j.tools.byteprocessor.compress
j.tools.byteprocessor.disperse
j.tools.byteprocessor.hashMd5
j.tools.byteprocessor.hashTiger192
j.tools.byteprocessor.decompress
j.tools.byteprocessor.getDispersedBlockObject
j.tools.byteprocessor.hashTiger160
j.tools.byteprocessor.undisperse
```

- compress/decompess: blosc compression (ultra fast,+ 250MB/sec)
- hashTiger... : ultra reliable hashing (faster than MD5 & longer keys)
- disperse/undiserpse: erasure coding (uses zfec: <https://pypi.python.org/pypi/zfec>)

```
!!!
title = "How To Use ByteProcessor"
date = "2017-04-08"
tags = ["howto"]
```

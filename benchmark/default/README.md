# Default benchmark

A full-featured comparison is not possible, because JSON and CSON don't accept complex numbers or special-types keys.

So this is a comparison of load time for a file with all the features that JSON, CSON, PyON and YAML can represent.

## Results

On my machine, a thousand iterations:

```
pyon: 4.59s
cson: 22.96s
json: 0.28s
yaml: 8.58s
```
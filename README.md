# ud-fi-ne

UD Finnish named entities

## Processing

```
for s in train dev test; do
    d=${s}-split
    (
	mkdir $d
	cd $d
	python3 ../scripts/split_by_document.py ../data/fi_tdt-ud-${s}.conllu
    )
done
```

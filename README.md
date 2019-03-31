# ud-fi-ne

UD Finnish named entities

## Processing

Split data into one .conllu file per document

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

Convert into brat-flavored standoff

```
for s in train dev test; do
    d=${s}-standoff;
    (
	mkdir $d
	cd $d
	for f in ../${s}-split/*.conllu; do
	    python3 ../scripts/ud_to_standoff.py $f
	done
    )
done
```

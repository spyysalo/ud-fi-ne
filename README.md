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

Get tokenized text

```
for s in train dev test; do
    mkdir ${s}-tokenized
    for f in ${s}-split/*.conllu; do
        python3 scripts/get_tokenized.py $f \
	    > ${s}-tokenized/$(basename $f .conllu).txt
    done
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

Get untokenized texts

```
for s in train dev test; do
    d=${s}-texts
    (
	mkdir $d
	cd $d
	for f in ../${s}-split/*.conllu; do
	    egrep '^# text = ' $f | perl -pe 's/^# text = //' \
	    	  > $(basename $f .conllu).txt
	done
    )
done
```

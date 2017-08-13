Example run

```
docker build -t contint-mediawiki-extensions-phan .
docker run \
    --rm --tty \
    --env ZUUL_URL=https://gerrit.wikimedia.org/r \
    --env ZUUL_PROJECT=mediawiki/extensions/TwoColConflict \
    --env ZUUL_COMMIT=eb57a0fb7be92ba8006dcb14322ff14c79fe12ec \
    --env ZUUL_REF=refs/zuul/master/Z1a964ddf253e4ec6b1d8d8fab076b616 \
    --env HOME=//var/lib/jenkins \
    --volume "./log://var/lib/jenkins/log" \
     contint-mediawiki-extensions-phan
```
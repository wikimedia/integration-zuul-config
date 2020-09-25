##Volumes

**/mediawiki**

This should be a copy of mediawiki.


## Example

To run phan for the ElectronPdfService extension:

```
docker run --rm \
    -e THING_SUBNAME=extensions/ElectronPdfService
    -v /dev/git/gerrit/mediawiki:/mediawiki \
    docker-registry.wikimedia.org/releng/mediawiki-phan:latest \
    --color
```

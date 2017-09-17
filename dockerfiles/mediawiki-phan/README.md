##Volumes

**/mediawiki**

This should be a copy of mediawiki.


## Example

To run phan for the ElectronPdfService extension:

```
docker run --rm \
-v /dev/git/gerrit/mediawiki:/mediawiki \
wmfreleng/mediawiki-phan:latest \
/mediawiki/extensions/ElectronPdfService -m checkstyle
```
## Volumes

**/mediawiki**

This should be a copy of mediawiki including the skin or extension you want to test.


## Example

To run seccheck for the AbuseFilter extension:

```
docker run --rm \
    --env THING_SUBNAME=extensions/AbuseFilter
    -v /dev/git/gerrit/mediawiki:/mediawiki \
    docker-registry.wikimedia.org/releng/mediawiki-phan-seccheck:latest \
    -m checkstyle
```

If you want to run a different variation of the seccheck plugin, you can set the
SECCHECK_MODE environment variable to e.g. `seccheck-slow-mwext`.

To run against skins, you would set the THING_SUBNAME environment variable to
something like `skins/MonoBook`.

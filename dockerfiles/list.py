import os

from docker_pkg.builder import DockerBuilder
from docker_pkg import dockerfile

base_dir = os.path.dirname(os.path.realpath(__file__))

dockerfile.TemplateEngine.setup({}, [])
build = DockerBuilder(base_dir, {})

build.scan()
images = build.all_images

preseed = {
    # Preseeded tree
    'scratch': None,
    'docker-registry.wikimedia.org/wikimedia-jessie': {'scratch'},
    'docker-registry.wikimedia.org/wikimedia-stretch': {'scratch'},
    'ci-jessie': {'docker-registry.wikimedia.org/wikimedia-jessie'},
    'ci-stretch': {'docker-registry.wikimedia.org/wikimedia-stretch'},
}
tree = preseed.copy()
errors = []
for image in images:
    # image is a docker_pkg.image.DockerImage object
    short_name = image.image.short_name
    tag = image.image.tag
    depends = image.image.depends

    #print('%s:%s <- %s' % (short_name, tag, ', '.join(depends)))
    if not depends and short_name not in preseed.keys():
        errors.append(short_name)

if errors:
    for error in errors:
        print('%s lacks Depends: field in control file' % error)

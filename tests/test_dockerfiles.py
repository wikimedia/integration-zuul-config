import os

DOCKERFILES_DIR = os.path.relpath(os.path.join(
    os.path.dirname(__file__),
    '../dockerfiles/'))

IMAGES_DIR = sorted([
    os.path.join(DOCKERFILES_DIR, d)
    for d in os.listdir(DOCKERFILES_DIR)
    if d != '__pycache__'
    and os.path.isdir(os.path.join(DOCKERFILES_DIR, d))
])


def assertImageHasFile(image_dir, filename):
    assert os.path.isfile(os.path.join(image_dir, filename)), \
        "Image directory %s has file %s" % (
            os.path.join(image_dir), filename)


def test_has_changelog():
    for image_dir in IMAGES_DIR:
        yield assertImageHasFile, image_dir, 'changelog'


def test_has_template():
    for image_dir in IMAGES_DIR:
        yield assertImageHasFile, image_dir, 'Dockerfile.template'


def assertChangelogPackage(image_dir):
    with open(os.path.join(image_dir, 'changelog')) as f:
        package = f.readline().split()[0]
    assert package == os.path.basename(image_dir), \
        'Package name %s matches directory name %s' % (
            package, os.path.basename(image_dir))


def test_changelog_has_proper_package():
    for image_dir in IMAGES_DIR:
        yield assertChangelogPackage, image_dir

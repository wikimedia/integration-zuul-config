import os

from debian.changelog import Changelog
from debian.deb822 import Deb822

DOCKERFILES_DIR = os.path.relpath(os.path.join(
    os.path.dirname(__file__),
    '../dockerfiles/'))

IMAGES_DIR = sorted([
    os.path.join(DOCKERFILES_DIR, d)
    for d in os.listdir(DOCKERFILES_DIR)
    if d not in ['__pycache__', '.tox']
    and os.path.isdir(os.path.join(DOCKERFILES_DIR, d))
])

IMAGES_NAME = set([os.path.basename(d) for d in IMAGES_DIR])


def assertImageHasFile(image_dir, filename):
    assert os.path.isfile(os.path.join(image_dir, filename)), \
        "Image directory %s must have a '%s' file" % (
            os.path.join(image_dir), filename)


def test_has_template():
    for image_dir in IMAGES_DIR:
        yield assertImageHasFile, image_dir, 'Dockerfile.template'


def test_has_changelog():
    for image_dir in IMAGES_DIR:
        yield assertImageHasFile, image_dir, 'changelog'


def test_has_control():
    for image_dir in IMAGES_DIR:
        yield assertImageHasFile, image_dir, 'control'


def assertChangelogPackage(changelog_filename):
    with open(changelog_filename) as f:
        package = Changelog(f).get_package()

    image_dir = os.path.basename(
        os.path.dirname(changelog_filename))

    assert package == image_dir, \
        'Changelog package name %s matches directory name %s' % (
            package, image_dir)


def test_changelog_has_proper_package():
    for image_dir in IMAGES_DIR:
        changelog_filename = os.path.join(image_dir, 'changelog')
        yield assertChangelogPackage, changelog_filename


def assertChangelogHasNoWarning(image_dir):
    with open(os.path.join(image_dir, 'changelog')) as f:
        # strict to raise an exception
        Changelog(f, strict=True)


def test_changelog_has_no_warning():
    for image_dir in IMAGES_DIR:
        yield assertChangelogHasNoWarning, image_dir


def assertControlFile(control_filename):
    control = None
    with open(control_filename) as f:
        control = Deb822(f)

    defined_deps = str(
        control.get('Depends', '') + control.get('Build-Depends', '')
        )
    if defined_deps == '':
        return

    deps = set(d.strip() for d in defined_deps.split(','))

    assert deps.issubset(IMAGES_NAME), 'control dependencies must exist'


def test_control_files():
    for image_dir in IMAGES_DIR:
        control_filename = os.path.join(image_dir, 'control')
        if os.path.isfile(control_filename):
            yield assertControlFile, control_filename

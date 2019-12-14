import os

from debian.changelog import Changelog
from debian.deb822 import Deb822

import pytest

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


@pytest.mark.parametrize('image_dir', IMAGES_DIR)
@pytest.mark.parametrize('filename',
                         ('Dockerfile.template', 'changelog', 'control'))
def test_has_files(image_dir, filename):
    assert os.path.isfile(os.path.join(image_dir, filename)), \
        "Image directory %s must have a '%s' file" % (
            os.path.join(image_dir), filename)


@pytest.mark.parametrize('image_dir', IMAGES_DIR)
def test_changelog_has_proper_package(image_dir):
    changelog_filename = os.path.join(image_dir, 'changelog')
    with open(changelog_filename) as f:
        package = Changelog(f).get_package()

    image_dir = os.path.basename(
        os.path.dirname(changelog_filename))

    assert package == image_dir, \
        'Changelog package name %s matches directory name %s' % (
            package, image_dir)


@pytest.mark.parametrize('image_dir', IMAGES_DIR)
def test_changelog_has_no_warning(image_dir):
    with open(os.path.join(image_dir, 'changelog')) as f:
        # strict to raise an exception
        Changelog(f, strict=True)


@pytest.mark.parametrize('image_dir', IMAGES_DIR)
def test_control_files(image_dir):
    control_filename = os.path.join(image_dir, 'control')
    if not os.path.isfile(control_filename):
        return

    with open(control_filename) as f:
        control = Deb822(f)

    defined_deps = str(
        control.get('Depends', '') + control.get('Build-Depends', '')
        )
    if defined_deps == '':
        return

    deps = set(d.strip() for d in defined_deps.split(','))

    assert deps.issubset(IMAGES_NAME), 'control dependencies must exist'

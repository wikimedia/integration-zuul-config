#
# Usage:
# $ pip3 install PyYAML
# $ python3 utils/zuul-layout-shaker.py zuul/layout.yaml
#
import re
import os
import yaml

def get_zuul_layout():
    filepath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../zuul/layout.yaml')
    with open(filepath) as file:
        layout = yaml.safe_load(file)
    return layout

def find_unused_job_overrides(layout):
    job_names = set()
    for template in layout['project-templates']:
        for key in template:
            if key != 'name':
                pipeline_job_names = template[key]
                job_names.update(pipeline_job_names)
    for project in layout['projects']:
        for key in project:
            if key != 'name' and key != 'template':
                pipeline_job_names = project[key]
                job_names.update(pipeline_job_names)

    # track which job name patterns and keys are used
    used = set()

    for job_name in job_names:
        properties = set()
        # iterate backwards because only the last match is used
        for job_override in reversed(layout['jobs']):
            if re.search(job_override['name'], job_name):
                for key in job_override:
                    if key != 'name':
                        if not key in properties:
                            used.add(job_override['name'] + '  key=' + key)
                            properties.add(key)

    unused = set()
    for job_override in layout['jobs']:
        for key in job_override:
            if key != 'name':
                usage_entry = job_override['name'] + '  key=' + key
                if not usage_entry in used:
                    unused.add(usage_entry)

    return unused

def find_unused_project_templates(layout):
    templates = set()

    # get them
    for obj in layout['project-templates']:
        templates.add(obj['name'])

    # remove them
    for project in layout['projects']:
        if 'template' in project:
            for template in project['template']:
                templates.discard(template['name'])

    return templates

def find_unused_pipelines(layout):
    pipelines = set()

    # get them
    for obj in layout['pipelines']:
        pipelines.add(obj['name'])

    # remove them
    for obj in layout['project-templates']:
        for key in obj:
            if key != 'name':
                pipelines.discard(key)
    for obj in layout['projects']:
        for key in obj:
            if key != 'name' and key != 'template':
                pipelines.discard(key)

    return pipelines

layout = get_zuul_layout()

print('')
print('### layout.yaml#jobs (overrides)')
unused = find_unused_job_overrides(layout)
if unused:
    print('Unused overrides:')
    print(unused)
else:
    print('No unused overrides.')

print('')
print('### layout.yaml#project-templates')
unused = find_unused_project_templates(layout)
if unused:
    print('Unused templates:')
    print(unused)
else:
    print('No unused templates.')

print('')
print('### layout.yaml#pipelines')
unused = find_unused_pipelines(layout)
if unused:
    print('Unused pipelines:')
    print(unused)
else:
    print('No unused pipelines.')

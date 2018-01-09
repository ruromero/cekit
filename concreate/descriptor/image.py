import concreate
import yaml

from concreate.descriptor import Descriptor, Label, Env, Port, Run, Modules, \
    Packages, Osbs, Volume

image_schema = yaml.safe_load("""
map:
  name: {type: str, required: True}
  version: {type: text, required: True}
  schema_version: {type: int}
  release: {type: text}
  from: {type: str}
  description: {type: text}
  labels: {type: any}
  envs:  {type: any}
  ports: {type: any}
  run: {type: any}
  artifacts: {type: any}
  modules: {type: any}
  packages: {type: any}
  osbs: {type: any}
  volumes: {type: any}""")


class Image(Descriptor):
    def __init__(self, descriptor, directory):
        self.directory = directory
        self.schemas = [image_schema.copy()]

        super(Image, self).__init__(descriptor)
        self._prepare()

    def _prepare(self):
        """Updates self._descriptor with objects and prepare sane label"""

        self._descriptor['labels'] = self._descriptor.get('labels', [])
        # The description key available in image descriptor's
        # root is added as labels to the image
        key = 'description'

        # If we define the label in the image descriptor
        # we should *not* override it with value from
        # the root's key
        if key in self._descriptor and not self.label(key):
            value = self._descriptor[key]
            self._descriptor['labels'].append({'name': key, 'value': value})

        # Last - if there is no 'summary' label added to image descriptor
        # we should use the value of the 'description' key and create
        # a 'summary' label with it's content. If there is even that
        # key missing - we should not add anything.
        description = self.label('description')

        if not self.label('summary') and description:
            self._descriptor['labels'].append(
                {'name': 'summary', 'value': description['value']})

        self._descriptor['labels'] = [Label(x) for x in self._descriptor.get('labels', [])]
        self._descriptor['envs'] = [Env(x) for x in self._descriptor.get('envs', [])]
        self._descriptor['ports'] = [Port(x) for x in self._descriptor.get('ports', [])]
        if 'run' in self._descriptor:
            self._descriptor['run'] = Run(self._descriptor['run'])
        self._descriptor['artifacts'] = [concreate.resource.Resource.new(a)
                                        for a in self._descriptor.get('artifacts', [])]
        if 'modules' in self._descriptor:
            self._descriptor['modules'] = Modules(self._descriptor['modules'])
        if 'packages' in self._descriptor:
            self._descriptor['packages'] = Packages(self._descriptor['packages'])
        if 'osbs' in self._descriptor:
            self._descriptor['osbs'] = Osbs(self._descriptor['osbs'])
        self._descriptor['volumes'] = [Volume(x) for x in self._descriptor.get('volumes', [])]

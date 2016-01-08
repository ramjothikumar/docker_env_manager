#!/usr/bin/env python

'''
To be run on the docker daemon.

Dependencies: docker-py (install using `pip install docker-py`)
'''
import argparse
import json
import logging
import sys

from docker import Client

REMOVE_EXISTING = 'remove_existing'
STARTUP_CMD = 'tail -f /dev/null'
DEFAULT_CHARS = ['/', ':']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-config-file', type=str, required=True,
                        help='Config file to create containers.'
                        ' See sample_config.json file for example.')
    return parser.parse_args()


def main():
    args = parse_args()
    config_file = args.config_file
    C = Client(base_url='unix://var/run/docker.sock')
    with open(config_file) as data_file:
        data = json.load(data_file)

    def get_image(image_name):
        for line in C.pull(image_name, stream=True):
            logging.debug(json.dumps(json.loads(line), indent=4))

    def remove_chars(word, chars=DEFAULT_CHARS):
        for char in chars:
            word = ''.join(word.split(char))
        return word

    def create_container(image_name, mode):
        if mode == REMOVE_EXISTING:
            for container in C.containers():
                if container.get('Image') == image_name:
                    logging.info('Deleting container - %s' %
                                 container.get('Names')[0])
                    C.remove_container(container=container.get('Id'),
                                       force=True)
        name = '%s_test' % remove_chars(image_name)
        container = C.create_container(image=image_name, hostname=name,
                                       name=name, command=STARTUP_CMD)
        logging.info('Created container - Image: %s | Name: %s | Id: %s'
                     % (image_name, name, container.get('Id')))
        return container

    for item in data['create_containers']['containers']:
        image_name = item['RepoTags']
        get_image(image_name)
        container = create_container(
            image_name, data['create_containers']['mode'])
        C.start(container=container.get('Id'))
        for cmd in item['cmds']:
            logging.debug('Executing command %s on Container %s' %
                          (cmd, container.get('Id')))
            C.execute(container=container.get('Id'), cmd=cmd)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()

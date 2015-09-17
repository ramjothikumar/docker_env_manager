#!/usr/bin/env python

'''
To be run on the docker daemon.

Dependencies: docker-py (install using `pip install docker-py`)
'''

from docker import Client
import json
import logging
import sys

REMOVE_EXISTING = 'remove_existing'
STARTUP_CMD = 'tail -f /dev/null'
DEFAULT_CHARS = ['/', ':']

def main(config_file):
    c = Client(base_url='unix://var/run/docker.sock')
    with open(config_file) as data_file:    
        data = json.load(data_file)

    def get_image(image_name):
        for line in c.pull(image_name, stream=True):
            logging.debug(json.dumps(json.loads(line), indent=4))

    def remove_chars(word, chars=DEFAULT_CHARS): 
        for char in chars:
            word = ''.join(word.split(char))
        return word

    def create_container(image_name, mode):
        if mode == REMOVE_EXISTING:
            for container in c.containers():
                if container.get('Image') == image_name:
                    logging.info('Deleting container - %s' % container.get('Names')[0])
                    c.remove_container(container=container.get('Id'), force=True)
        name = '%s_test' % remove_chars(image_name)
        container = c.create_container(image=image_name, hostname=name, name=name, command=STARTUP_CMD)
        logging.info('Created container - Image: %s | Name: %s | Id: %s' % (image_name, name, container.get('Id')))
        return container

    for item in data['create_containers']['containers']:
        image_name = item['RepoTags']
        get_image(image_name)
        container = create_container(image_name, data['create_containers']['mode'])
        c.start(container=container.get('Id'))
        for cmd in item['cmds']:
            logging.debug('Executing command %s on Container %s' % (cmd, container.get('Id')))
            c.execute(container=container.get('Id'), cmd=cmd) 

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == '--h' or sys.argv[1] == '--help':
        print 'Usage: %s <config_file_in_json>' % sys.argv[0]
        exit()
    filename = sys.argv[1]
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main(filename)

from packaging import version


protocols = []


def _create_empty_input(mimetype, info, destination, type_):
    return {
            'mimetype': mimetype,
            'info': info,
            'destination': destination,
            'value': None,
            'type': type_,
        }


def _create_empty_identifier_file(mimetype, info, destination):
    return _create_empty_input(mimetype, info, destination, 'identifier_file')


def _create_empty_directory(info, destination):
    return _create_empty_input('inode/directory', info, destination, 'directory')


def _create_empty_dict(info, destination):
    return {
        'type': 'dict',
        'info': info,
        'destination': destination,
        'value': None,
    }


scaffold_protocol = {
    'id': 'sds-protocol',
    'version': '0.1.0',
    'name': 'SimpleScaffold',
    'info': 'This protocol defines the required files to create a Scaffold based SPARC dataset.',
    'inputs': [
        _create_empty_identifier_file('application/json', 'Scaffold creator step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'Argon viewer step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'Scene exporter webGL step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'Scene exporter thumbnail  step configuration file.', 'primary'),
        _create_empty_directory('WebGL output directory', 'derivative'),
        _create_empty_dict('JSON serializable Python dict containing provenance information.', 'primary/provenance.json')
    ]
}

protocols.append(scaffold_protocol)


def is_sds_protocol(protocol):
    if not isinstance(protocol, dict):
        return False

    if not ('id' in protocol and 'version' in protocol):
        return False

    if protocol['id'] != 'sds-protocol':
        return False

    try:
        version.parse(protocol['version'])
    except version.InvalidVersion:
        return False

    return True


def _populate_scaffold_protocol(protocol, data):
    if len(protocol['inputs']) != len(data):
        return False

    for index, d in enumerate(data):
        protocol['inputs'][index]['value'] = d

    return True


def populate_protocol(protocol, data):
    if not is_sds_protocol(protocol):
        return False

    if protocol['name'] == 'SimpleScaffold':
        return _populate_scaffold_protocol(protocol, data)

    return False


def get_protocol_by_name(name):
    for p in protocols:
        if p['name'] == name:
            return p

    return None

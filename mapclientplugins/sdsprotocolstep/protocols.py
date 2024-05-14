import os.path

from packaging import version


protocols = []


def _create_empty_input(mimetype, info, destination, type_, optional=False):
    return {
            'mimetype': mimetype,
            'info': info,
            'destination': destination,
            'value': None,
            'type': type_,
            'optional': optional,
        }


def _create_empty_identifier_file(mimetype, info, destination):
    return _create_empty_input(mimetype, info, destination, 'identifier_file')


def _create_empty_optional_identifier_file(mimetype, info, destination):
    return _create_empty_input(mimetype, info, destination, 'identifier_file', True)


def _create_empty_directory(info, destination):
    return _create_empty_input('inode/directory', info, destination, 'directory')


def _create_empty_dict(info, destination):
    return {
        'type': 'dict',
        'info': info,
        'destination': destination,
        'value': None,
        'optional': False
    }


scaffold_protocol = {
    'id': 'sds-protocol',
    'version': '0.1.0',
    'name': 'SimpleScaffold',
    'info': """
    This protocol defines the required files to create a Scaffold based SPARC dataset.
    This protocol uses four configuration files to create a Scaffold based dataset.
    The four configuration files expected are from the following steps; Scaffold Creator,
     Argon Viewer, and Scene Exporter.  This protocol expects two Scene Exporter configuration
     files, one for the WebGL output and one for the thumbnail output."""
    ,
    'inputs': [
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_optional_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_optional_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
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


def _is_valid_identifier_file(d):
    return os.path.isfile(d)


def _is_valid_directory(d):
    return os.path.isdir(d)


def _is_valid_input(obj, d):
    if obj['type'] == 'identifier_file':
        return _is_valid_identifier_file(d)
    elif obj['type'] == 'directory':
        return _is_valid_directory(d)
    elif obj['type'] == 'dict':
        return isinstance(d, dict)

    return False


def _is_optional_input(obj):
    return obj['optional']


def _populate_scaffold_protocol(protocol, data):
    if len(data) > len(protocol['inputs']):
        return False

    i = 0
    j = 0
    protocol_input_map = {}
    while i < len(protocol['inputs']):
        obj = protocol['inputs'][i]
        d = data[j]
        protocol_input_map[i] = j
        if not _is_valid_input(obj, d) and not _is_optional_input(obj):
            return False
        elif not _is_valid_input(obj, d) and _is_optional_input(obj):
            j += 1
        else:
            i += 1
            j += 1

    for input_index, data_index in protocol_input_map.items():
        protocol['inputs'][input_index]['value'] = data[data_index]

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

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
    'version': '0.2.0',
    'name': 'SimpleScaffold',
    'type': 'computational',
    'info': """
    This protocol defines the required files to create a Scaffold based SPARC dataset.
    This protocol uses four configuration files to create a Scaffold based dataset.
    The four configuration files expected are from the following steps; Scaffold Creator,
     Argon Viewer, and Scene Exporter.  This protocol expects two Scene Exporter configuration
     files, one for the WebGL output and one for the thumbnail output."""
    ,
    'inputs': [
        _create_empty_directory('Output dataset root directory', '.'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_optional_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_optional_identifier_file('application/json', 'MAP Client step configuration file.', 'primary'),
        _create_empty_directory('WebGL output directory', 'derivative'),
        _create_empty_dict('JSON serializable Python dict containing provenance information.',
                           'primary/provenance.json')
    ]
}

vagus_protocol = {
    'id': 'sds-protocol',
    'version': '0.2.0',
    'name': 'ScaffoldedVagus',
    'type': 'computational',
    'info': """
    This protocol defines the required files to create a SPARC dataset for Vagus scaffolds.
    This protocol uses one directory location to generate the general dataset information, including:
     * Dataset description,
     * Number of subjects, and,
     * Number of samples.
    """
    ,
    'inputs': [
        _create_empty_directory('Output dataset root directory', '.'),
    ]
}

protocols.append(scaffold_protocol)
protocols.append(vagus_protocol)


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
    """
    Populates the protocol inputs by matching them with a list of data.

    This function "zips" the data list to the protocol inputs,
    intelligently skipping optional inputs.
    """

    # We can't have more data items than we have protocol inputs.
    if len(data) > len(protocol['inputs']):
        print(f"Error: {len(data)} data items provided, but only {len(protocol['inputs'])} protocol inputs exist.")
        return False

    i = 0  # Current protocol input index
    j = 0  # Current data item index

    # This map will store the successful assignments: {protocol_index: data_index}
    assignment_map = {}

    # Loop through every protocol input slot
    while i < len(protocol['inputs']):
        obj = protocol['inputs'][i]

        # Check if we still have data items left to assign
        if j < len(data):
            d = data[j]

            # Case 1: The data item is valid for the protocol input
            if _is_valid_input(obj, d):
                # Assign this data item to this protocol input
                assignment_map[i] = j
                i += 1  # Move to the next protocol input
                j += 1  # Move to the next data item

            # Case 2: The data is NOT valid, BUT the protocol input is optional
            elif _is_optional_input(obj):
                # Skip this optional protocol input.
                # DO NOT increment j. The current data item
                # will be tested against the *next* protocol input.
                i += 1

            # Case 3: The data is NOT valid, and the input is NOT optional
            else:
                # We have a mandatory input that doesn't match the data.
                print(f"Error: Data item '{d}' is not valid for mandatory input {i} ('{obj.get('name', 'N/A')}')")
                return False

        # Case 4: We have run out of data, but still have protocol inputs left
        else:
            # This is only okay if the remaining protocol inputs are all optional.
            if not _is_optional_input(obj):
                # We've hit a mandatory input but have no data left.
                print(f"Error: Ran out of data. Mandatory input {i} ('{obj.get('name', 'N/A')}') was not provided.")
                return False

            # This input is optional, and we have no data, so just skip it.
            i += 1

    # After the loop, all protocol inputs are accounted for.
    # We must also check if we have any *unused* data items left over.
    if j < len(data):
        print(f"Error: {len(data) - j} data item(s) were left over (too much data provided).")
        return False

    # If we made it here, the mapping is valid. Apply the assignments.
    for protocol_index, data_index in assignment_map.items():
        protocol['inputs'][protocol_index]['value'] = data[data_index]

    return True


def populate_protocol(protocol, data):
    if not is_sds_protocol(protocol):
        return False

    if protocol['name'] == 'SimpleScaffold':
        return _populate_scaffold_protocol(protocol, data)

    if protocol['name'] == 'ScaffoldedVagus':
        return _populate_scaffold_protocol(protocol, data)

    return False


def get_protocol_by_name(name):
    for p in protocols:
        if p['name'] == name:
            return p

    return None

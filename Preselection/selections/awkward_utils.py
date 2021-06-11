import awkward
import vector
import numpy

def missing_fields(array, fields):
    """
    Check if every field of fields is present in a given array.
    Fields of records (e.g. Photon.pt) should be passed as tuples: ("Photon", "pt")
    :param array: array to be checked
    :type array: awkward array
    :param fields: list of fields
    :type fields: list of str or tuple
    :return: list of missing fields in array
    :rtype: list
    """

    missing_fields = []

    for field in fields:
        if isinstance(field, str):
            if field not in array.fields:
                missing_fields.append(field)
        elif isinstance(field, tuple):
            sub_array = array
            for sub_field in field:
                if sub_field not in sub_array.fields:
                    missing_fields.append(field)
                    break
                sub_array = sub_array[sub_field]

        else:
            message = "Each entry in the <fields> argument should be either a str or tuple, not %s which is the type of entry %s" % (str(type(field)), str(field))
            raise TypeError(message)

    return missing_fields


def construct_jagged_array(offsets, contents):
    """
    Use numpy arrays of the offsets and contents to create a jagged awkward array.
    See: https://awkward-array.readthedocs.io/en/latest/ak.layout.ListOffsetArray.html

    :param offsets: specifies the starting and stopping index of each list
    :type offsets: numpy.array
    :param contents: underlying data for all lists
    :type contents: numpy.array
    :return: awkward array with unequal-length lists
    :rtype: awkward.layout.ListOffsetArray
    """
    array = awkward.Array(
        awkward.layout.ListOffsetArray64(
            awkward.layout.Index64(offsets),
            awkward.layout.NumpyArray(contents)
        )
    )
    return array


def add_field(events, name, data, overwrite = False):
    """
    Add a field or record to an awkward array.
    Checks if the field is already present and returns the existing field if so,
    unless the overwrite option is selected (be careful using this option!).

    :param events: base events array which you want to add a field to
    :type events: awkward.highlevel.Array
    :param name: name of the field or record you want to add
    :type name: str or tuple
    :param data: either a dictionary of subfields : awkward array (for creating a nested record) or a single awkward array (for creating a single field)
    :type data: dict or awkward.highlevel.Array or numpy.ndarray
    :param overwrite: whether to overwrite this field in events (only applicable if it already exists)
    :type overwrite: bool
    :return: events array with field or record added
    :rtype: awkward.highlevel.Array
    """

    already_present = len(missing_fields(events, [name])) == 0
    if already_present and not overwrite:
        return events[name]

    if isinstance(data, awkward.highlevel.Array) or isinstance(data, numpy.ndarray):
        events[name] = data
        return events[name]
    elif isinstance(data, dict):
        return create_record(events, name, data, overwrite)
    else:
        message = "[awkward_utils.py : add_field] argument <data> should be either an awkward.highlevel.Array (in the case of adding a single field) or a dictionary (in the case of creating a record), not %s as you have passed." % (str(type(data)))
        raise TypeError(message)
    

def create_record(events, name, data, overwrite):
    """
    Adds a nested record to events array.
    If there are any fields containing "p4", this is assumed to be an array of <vector> objects and the pt/eta/phi/mass will be added as top-level fields in the record for easier access. 

    :param name: name of the record to be added 
    :type name: str or tuple
    :param data: dictionary of subfields : awkward array 
    :type data: dict
    :param overwrite: whether to overwrite this field in events (only applicable if it already exists)
    :type overwrite: bool
    :return: events array with record added
    :rtype: awkward.highlevel.Array 
    """
   
    # If there is a field named "p4", save its properties as additional fields for easier access
    additional_fields = {}
    for key, array in data.items():
        if "p4" in key:
            additional_fields[key.replace("p4", "pt")] = array.pt
            additional_fields[key.replace("p4", "eta")] = array.eta
            additional_fields[key.replace("p4", "phi")] = array.phi
            additional_fields[key.replace("p4", "mass")] = array.mass

    for key, array in additional_fields.items():
        data[key] = array

    events[name] = awkward.zip(data)

    return events[name]


def create_four_vectors(events, offsets, contents):
    """
    Zip four vectors as record in awkard array.
    Record these as `Momentum4D` vector objects so all typical
    four vector properties and methods can be called on them.
    The contents must be given as a numpy array with 4 indicies in the last
    dimension, in the order: pt, eta, phi, mass

    :param events: awkward array of events
    :type events: awkward array
    :param offsets: offsets describing the object locations
    :type offsets: numpy array
    :param contents: pt, eta, phi, mass of the object to be zipped
    :type contents: numpy array
    :return: awkward array of the four momentums 
    :rtype: awkward array of Momentum4D vector
    """

    # First convert from awkward.layout.Index & awkward.layout.Array -> to awkward array
    objects = {}
    for idx, field in enumerate(["pt", "eta", "phi", "mass"]):
        objects[field] = construct_jagged_array(
                offsets,
                contents[:,idx]
        )

    # Second, convert to awkward array of Momentum4D vector objects
    objects_p4 = vector.awk(
            {
                "pt" : objects["pt"],
                "eta" : objects["eta"],
                "phi" : objects["phi"],
                "mass" : objects["mass"]
            },
            with_name = "Momentum4D"
    )

    return objects_p4


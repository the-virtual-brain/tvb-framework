
class GenericAttributes(object):
    """
    Model class to hold generic attributes that we want to keep on all H5 file that correspond to a datatype.
    It is used by the H5File in order to populate the corresponding H5 attributes (meta-data).
    """
    invalid = False
    is_nan = False
    subject = ''
    state = ''
    type = ''
    user_tag_1 = ''
    user_tag_2 = ''
    user_tag_3 = ''
    user_tag_4 = ''
    user_tag_5 = ''
    visible = False
from .base_predicates import *

# crx 0118
VALIDATE_PREDICATE_FN_DICT = {
    'true': TruePredicateFn(),
    'false': FalsePredicateFn(),
    'in': In(),
    'notin': NotIn(),
    'incontact': InContactPredicateFn(),
    'on': On(),
    'noton': NotOn(),
    'up': Up(),
    'printjointstate': PrintJointState(),
    'open': Open(),
    'close': Close(),
    'turnon': TurnOn(),
    'turnoff': TurnOff(),
    'collide': Collide(),
    'fall': Fall(),
    'checkgripperforce': CheckGripperForce(),
    'checkforce': CheckForce(),
    'incontactpart': InContactPart(),
    'checkpartiallycontain': CheckPartiallyContain(),
    'checkpartpartiallycontain': CheckPartPartiallyContain(),
    'checkrobotcontact': CheckRobotContact(),
    'checkgrippercontact': CheckGripperContact(),
    'checkcontact': CheckContact(),
    'checkgrippercontactpart': CheckGripperContactPart(),
}


# TEMPORAL_PREDICATE_FN_LIST = [
#     'incontact',
#     'on',
#     'up',
#     'stack',
#     'checkforce',
#     'incontactpart',
#     'checkcontact',
#     'checkpartiallycontain',
#     'checkpartpartiallycontain',
#     'checkgrippercontact',
#     'checkgrippercontactpart',
# ]


def update_predicate_fn_dict(fn_key, fn_name):
    VALIDATE_PREDICATE_FN_DICT.update({fn_key: eval(fn_name)()})


def eval_predicate_fn(predicate_fn_name, *args):
    assert predicate_fn_name in VALIDATE_PREDICATE_FN_DICT
    return VALIDATE_PREDICATE_FN_DICT[predicate_fn_name](*args)


def get_predicate_fn_dict():
    return VALIDATE_PREDICATE_FN_DICT


def get_predicate_fn(predicate_fn_name):
    return VALIDATE_PREDICATE_FN_DICT[predicate_fn_name.lower()]


# def check_temporal_predicate(predicate_fn_name):
#     return predicate_fn_name.lower() in TEMPORAL_PREDICATE_FN_LIST

from .base_predicates import *


# VALIDATE_PREDICATE_FN_DICT = {
#     "true": TruePredicateFn(),
#     "false": FalsePredicateFn(),
#     "in": In(),
#     # "incontact": InContactPredicateFn(),
#     "on": On(),
#     "up": Up(),
#     # "stack":     Stack(),
#     # "temporal":  TemporalPredicate(),
#     "printjointstate": PrintJointState(),
#     "open": Open(),
#     "close": Close(),
#     "turnon": TurnOn(),
#     "turnoff": TurnOff(),
# }

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
    # "stack":     Stack(),
    # "temporal":  TemporalPredicate(),
    'printjointstate': PrintJointState(),
    'open': Open(),
    'close': Close(),
    'turnon': TurnOn(),
    'turnoff': TurnOff(),
    'collide': Collide(),
    'fall': Fall(),
    'checkforce': CheckForce(),
    'checkdistance': CheckDistance(),
    'incontactpart': InContactPart(),
    'checkpartiallycontain': CheckPartiallyContain(),
    'checkpartpartiallycontain': CheckPartPartiallyContain(),
    'checkgrippercontact': CheckGripperContact(),
    'checkcontact': CheckContact(),
    'checkgrippercontactpart': CheckGripperContactPart(),
    'checkgripperdistance': CheckGripperDistance(),
    'checkgripperdistancepart': CheckGripperDistancePart(),
}


TEMPORAL_PREDICATE_FN_LIST = [
    'incontact',
    'on',
    'up',
    'stack',
    'checkforce',
    'incontactpart',
    'checkdistance',
    'checkcontact',
    'checkpartiallycontain',
    'checkpartpartiallycontain',
    'checkgrippercontact',
    'checkgrippercontactpart',
    'checkgripperdistance',
    'checkgripperdistancepart',
]


def update_predicate_fn_dict(fn_key, fn_name):
    VALIDATE_PREDICATE_FN_DICT.update({fn_key: eval(fn_name)()})


def eval_predicate_fn(predicate_fn_name, *args):
    assert predicate_fn_name in VALIDATE_PREDICATE_FN_DICT
    return VALIDATE_PREDICATE_FN_DICT[predicate_fn_name](*args)


def get_predicate_fn_dict():
    return VALIDATE_PREDICATE_FN_DICT


def get_predicate_fn(predicate_fn_name):
    return VALIDATE_PREDICATE_FN_DICT[predicate_fn_name.lower()]


def check_temporal_predicate(predicate_fn_name):
    return predicate_fn_name.lower() in TEMPORAL_PREDICATE_FN_LIST

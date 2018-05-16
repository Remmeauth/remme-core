import ujson

from .constants import Status


def serialize(payload):
    return ujson.dumps(payload)


def deserialize(payload):
    return ujson.loads(payload)


def create_res_payload(status, data, id, type):
    payload = {
        'type': type,
        'status': status.name.lower(),
    }
    if id:
        payload['id'] = id
    if type == 'message':
        payload['data'] = data
        del payload['status']
    if type == 'error':
        payload['description'] = data
    return serialize(payload)


def validate_payload(payload):
    if not payload.get('type'):
        return Status.MISSING_TYPE
    elif not payload.get('action'):
        return Status.MISSING_ACTION
    elif not payload.get('entity'):
        return Status.MISSING_ENTITY
    elif not payload.get('id'):
        return Status.MISSING_ID
    elif not payload.get('parameters'):
        return Status.MISSING_PARAMETERS

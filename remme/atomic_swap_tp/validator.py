from remme.protos.atomic_swap_pb2 import AtomicSwapInitPayload


def atomic_swap_validator(payload):
    if isinstance(payload, AtomicSwapInitPayload):
        return

def validate_swap_init(payload):
    pass
# AtomicSwapApprovePayload
# AtomicSwapExpirePayload
# AtomicSwapSetSecretLockPayload
# AtomicSwapClosePayload
# AtomicSwapInfo)

import logging
from contextlib import suppress

from google.protobuf.message import DecodeError
from sawtooth_sdk.messaging.exceptions import ValidatorConnectionError

from sawtooth_sdk.protobuf.client_list_control_pb2 import ClientPagingControls
from sawtooth_sdk.protobuf.client_state_pb2 import (
    ClientStateGetRequest, ClientStateGetResponse,
    ClientStateListRequest, ClientStateListResponse,
)
# TODO: No such protobug, investigate
# from sawtooth_sdk.protobuf.client_status_pb2 import (
#     ClientStatusGetRequest, ClientStatusGetResponse
# )
from sawtooth_sdk.protobuf.client_peers_pb2 import (
    ClientPeersGetRequest, ClientPeersGetResponse
)
from sawtooth_sdk.protobuf.client_receipt_pb2 import (
    ClientReceiptGetRequest, ClientReceiptGetResponse
)
from sawtooth_sdk.protobuf.client_batch_submit_pb2 import (
    ClientBatchSubmitRequest, ClientBatchSubmitResponse,
    ClientBatchStatusRequest, ClientBatchStatusResponse,
)
from sawtooth_sdk.protobuf.client_batch_pb2 import (
    ClientBatchListRequest, ClientBatchListResponse,
    ClientBatchGetRequest, ClientBatchGetResponse,
)
from sawtooth_sdk.protobuf.client_transaction_pb2 import (
    ClientTransactionListRequest, ClientTransactionListResponse,
    ClientTransactionGetRequest, ClientTransactionGetResponse,
)
from sawtooth_sdk.protobuf.client_block_pb2 import (
    ClientBlockGetByIdRequest, ClientBlockGetResponse,
    ClientBlockListRequest, ClientBlockListResponse,
)
from sawtooth_sdk.protobuf.validator_pb2 import Message

from remme.shared.utils import (
    get_paging_controls,
    get_head_id,
    get_filter_ids,
    get_sorting_message,
    make_paging_message,
    expand_batch,
    expand_block,
    expand_transaction,
    validate_id,
    drop_empty_props,
    drop_id_prefixes,
    message_to_dict,
)
from remme.shared.exceptions import (
    ClientException, KeyNotFound, ValidatorNotReadyException
)


LOGGER = logging.getLogger(__name__)


class Router:

    def _handle_response(self, msg_type, resp_proto, req):
        self._stream.wait_for_ready()

        future = self._stream.send(
            message_type=msg_type,
            content=req.SerializeToString())

        resp = resp_proto()

        try:
            resp.ParseFromString(future.result().content)
        except (DecodeError, AttributeError):
            raise ClientException(
                'Failed to parse "content" string from validator')
        except ValidatorConnectionError as vce:
            raise ClientException(
                'Failed with ZMQ interaction: {0}'.format(vce))

        data = message_to_dict(resp)

        # NOTE: Not all protos have this status
        with suppress(AttributeError):
            if resp.status == resp_proto.NO_RESOURCE:
                raise KeyNotFound("404")

        if resp.status != resp_proto.OK:
            LOGGER.error(f'The response indicated a not successful '
                         f'request: {data}')
            if hasattr(resp_proto, 'NOT_READY') and \
               resp_proto.NOT_READY == resp.status:
                raise ValidatorNotReadyException()
            raise ClientException(f"Error: {data}")

        return data

    @classmethod
    def _get_metadata(cls, response, head=None):
        head = response.get('head_id', head)
        metadata = {}
        if head is not None:
            metadata['head'] = head
        return metadata

    @staticmethod
    def _wrap_response(data=None, metadata=None):
        envelope = metadata or {}

        if data is not None:
            envelope['data'] = data

        return envelope

    @classmethod
    def _wrap_paginated_response(cls, response, controls, data, head=None):
        paging_response = response['paging']
        if head is None:
            head = response['head_id']

        paging = {
            'limit': controls.get('limit'),
            'start': controls.get('start'),
            'next': paging_response.get('next'),
        }
        return cls._wrap_response(
            data=data,
            metadata={
                'head': head,
                'paging': paging
            })

    def _head_to_root(self, block_id):
        if block_id:
            resp = self._handle_response(
                Message.CLIENT_BLOCK_GET_BY_ID_REQUEST,
                ClientBlockGetResponse,
                ClientBlockGetByIdRequest(block_id=block_id)
            )
            block = expand_block(resp['block'])
        else:
            resp = self._handle_response(
                Message.CLIENT_BLOCK_LIST_REQUEST,
                ClientBlockListResponse,
                ClientBlockListRequest(
                    paging=ClientPagingControls(limit=1)
                )
            )
            block = expand_block(resp['blocks'][0])
        return (
            block['header_signature'],
            block['header']['state_root_hash'],
        )

    def list_state(self, address, start=None, limit=None, head=None,
                   reverse=None):
        paging_controls = get_paging_controls(start, limit)
        head, root = self._head_to_root(head)

        response = self._handle_response(
            Message.CLIENT_STATE_LIST_REQUEST,
            ClientStateListResponse,
            ClientStateListRequest(
                state_root=root,
                address=address,
                sorting=get_sorting_message(reverse, "default"),
                paging=make_paging_message(paging_controls)
            )
        )
        return self._wrap_paginated_response(
            response=response,
            controls=paging_controls,
            data=response.get('entries', []),
            head=head
        )

    def fetch_state(self, address, head=None):
        head, root = self._head_to_root(head)

        response = self._handle_response(
            Message.CLIENT_STATE_GET_REQUEST,
            ClientStateGetResponse,
            ClientStateGetRequest(
                state_root=root, address=address
            )
        )
        return self._wrap_response(
            data=response['value'],
            metadata=self._get_metadata(response, head=head)
        )

    def list_blocks(self, block_ids=None, start=None, limit=None, head=None,
                    reverse=None):
        paging_controls = get_paging_controls(start, limit)
        id_query = ','.join(block_ids) if block_ids else None

        response = self._handle_response(
            Message.CLIENT_BLOCK_LIST_REQUEST,
            ClientBlockListResponse,
            ClientBlockListRequest(
                head_id=get_head_id(head),
                block_ids=get_filter_ids(id_query),
                sorting=get_sorting_message(reverse, 'block_num'),
                paging=make_paging_message(paging_controls)
            )
        )
        return self._wrap_paginated_response(
            response=response,
            controls=paging_controls,
            data=[expand_block(b) for b in response['blocks']]
        )

    def fetch_block(self, block_id):
        validate_id(block_id)

        response = self._handle_response(
            Message.CLIENT_BLOCK_GET_BY_ID_REQUEST,
            ClientBlockGetResponse,
            ClientBlockGetByIdRequest(
                block_id=block_id
            )
        )
        return self._wrap_response(
            data=expand_block(response['block']),
            metadata=self._get_metadata(response)
        )

    def list_batches(self, batch_ids=None, start=None, limit=None, head=None,
                     reverse=None):
        paging_controls = get_paging_controls(start, limit)
        id_query = ','.join(batch_ids) if batch_ids else None

        response = self._handle_response(
            Message.CLIENT_BATCH_LIST_REQUEST,
            ClientBatchListResponse,
            ClientBatchListRequest(
                head_id=get_head_id(head),
                batch_ids=get_filter_ids(id_query),
                sorting=get_sorting_message(reverse, 'default'),
                paging=make_paging_message(paging_controls)
            )
        )
        return self._wrap_paginated_response(
            response=response,
            controls=paging_controls,
            data=[expand_batch(b) for b in response['batches']]
        )

    def fetch_batch(self, batch_id):
        validate_id(batch_id)

        response = self._handle_response(
            Message.CLIENT_BATCH_GET_REQUEST,
            ClientBatchGetResponse,
            ClientBatchGetRequest(
                batch_id=batch_id
            )
        )
        return self._wrap_response(
            data=expand_batch(response['batch']),
            metadata=self._get_metadata(response)
        )

    def list_transactions(self, transaction_ids=None, start=None, limit=None,
                          head=None, reverse=None):
        paging_controls = get_paging_controls(start, limit)
        id_query = ','.join(transaction_ids) if transaction_ids else None

        response = self._handle_response(
            Message.CLIENT_TRANSACTION_LIST_REQUEST,
            ClientTransactionListResponse,
            ClientTransactionListRequest(
                head_id=get_head_id(head),
                transaction_ids=get_filter_ids(id_query),
                sorting=get_sorting_message(reverse, 'default'),
                paging=make_paging_message(paging_controls)
            )
        )
        data = [expand_transaction(t) for t in response['transactions']]

        return self._wrap_paginated_response(
            response=response,
            controls=paging_controls,
            data=data
        )

    def fetch_transaction(self, transaction_id):
        validate_id(transaction_id)

        response = self._handle_response(
            Message.CLIENT_TRANSACTION_GET_REQUEST,
            ClientTransactionGetResponse,
            ClientTransactionGetRequest(
                transaction_id=transaction_id
            )
        )
        return self._wrap_response(
            data=expand_transaction(response['transaction']),
            metadata=self._get_metadata(response)
        )

    def list_receipts(self, transaction_ids):
        id_query = ','.join(transaction_ids) if transaction_ids else None
        response = self._handle_response(
            Message.CLIENT_RECEIPT_GET_REQUEST,
            ClientReceiptGetResponse,
            ClientReceiptGetRequest(
                transaction_ids=get_filter_ids(id_query)
            )
        )
        data = drop_id_prefixes(drop_empty_props(response['receipts']))
        return self._wrap_response(
            data=data,
            metadata=self._get_metadata(response)
        )

    def fetch_peers(self):
        response = self._handle_response(
            Message.CLIENT_PEERS_GET_REQUEST,
            ClientPeersGetResponse,
            ClientPeersGetRequest()
        )
        return self._wrap_response(
            data=response['peers'],
            metadata=self._get_metadata(response)
        )

    # def fetch_status(self):
    #     response = self._handle_response(
    #         Message.CLIENT_STATUS_GET_REQUEST,
    #         ClientStatusGetResponse,
    #         ClientStatusGetRequest()
    #     )
    #     return self._wrap_response(
    #         data={
    #             'peers': response['peers'],
    #             'endpoint': response['endpoint']
    #         },
    #         metadata=self._get_metadata(response)
    #     )

    def submit_batches(self, batches):
        self._handle_response(
            Message.CLIENT_BATCH_SUBMIT_REQUEST,
            ClientBatchSubmitResponse,
            ClientBatchSubmitRequest(batches=batches)
        )

        id_string = ','.join(b.header_signature for b in batches)
        return self._wrap_response(
            data=id_string
        )

    def list_statuses(self, batch_ids):
        id_query = ','.join(batch_ids) if batch_ids else None
        response = self._handle_response(
            Message.CLIENT_BATCH_STATUS_REQUEST,
            ClientBatchStatusResponse,
            ClientBatchStatusRequest(
                batch_ids=get_filter_ids(id_query)
            )
        )
        data = drop_id_prefixes(drop_empty_props(response['batch_statuses']))
        return self._wrap_response(
            data=data,
            metadata=self._get_metadata(response)
        )

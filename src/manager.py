from twisted.internet import defer, reactor, endpoints
from twisted.internet.protocol import ClientCreator

from .protocol import DummyProtocol


class ClientProtocolManager(object):
    """
    CProtocol manager.
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ClientProtocolManager, cls).__new__(cls)

            # initialization
            cls.instance._protocol_buffer = {}
            cls.instance._protocol_deferred = {}
            cls.instance._request_protocol = {}
            cls.instance._protocol = DummyProtocol

        return cls.instance

    def _create_protocol(self, connection_str):
        """
        Create connection with provided connection string (protocol:ip:port)
        """

        if connection_str not in self._protocol_deferred:

            def _created(protocol):
                protocol.conn_str = connection_str
                protocol.manager = self

                # add created protocol to buffer
                self._protocol_buffer[connection_str] = protocol

                # sent result to deferred requests
                for request_deferred in self._request_protocol[connection_str]:
                    request_deferred.callback(protocol)

                # clean request defered buffers
                del self._request_protocol[connection_str]
                del self._protocol_deferred[connection_str]

            def _failed(error):
                # sent exception to deferred requests
                for request_deferred in self._request_protocol[connection_str]:
                    request_deferred.errback(error)

                # clean request defered buffers
                del self._request_protocol[connection_str]
                del self._protocol_deferred[connection_str]

            host, port = connection_str.split(':')[1:3]
            # create protocol deferred
            client_defer = ClientCreator(reactor, self._protocol)
            proto_defer = client_defer.connectTCP(host=host, port=int(port), timeout=1)

            proto_defer.addCallback(_created)
            proto_defer.addErrback(_failed)

            self._protocol_deferred[connection_str] = proto_defer

            # create request's empty list
            self._request_protocol[connection_str] = []

        self._request_protocol[connection_str].append(defer.Deferred())
        return self._request_protocol[connection_str][-1]

    @defer.inlineCallbacks
    def get_protocol(self, connection_str):
        """
        Get protocol with provided connection string
        (protocol:ip:port:username:password)
        """

        if connection_str not in self._protocol_buffer:
            request_protocol = yield self._create_protocol(connection_str)
            defer.returnValue(request_protocol)
        else:
            defer.returnValue(self._protocol_buffer[connection_str])

    def kill_protocol(self, connection_str):
        """
        Remove protocol from buffer by connection string (protocol:ip:port)
        """
        if connection_str in self._protocol_buffer:
            del self._protocol_buffer[connection_str]

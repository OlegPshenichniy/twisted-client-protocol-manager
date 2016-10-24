# Client protocol creation manager
Async manager for creating/retrieving client protocols

## Example of usage

```python
def response_error(failure):
    print "Fail", failure


def check_response_0(response):
    print 'resp0', response


def check_response_1(response):
    print 'resp1', response


def check_response_2(response):
    print 'resp2', response


def check_response_3(response):
    print 'resp3', response


manager_instance_0 = ClientProtocolManager()
proto0 = manager_instance_0.get_protocol('tcp:188.188.188.188:2014')
proto1 = manager_instance_0.get_protocol('tcp:188.188.188.188:2015')

manager_instance_1 = ClientProtocolManager()
proto2 = manager_instance_1.get_protocol('tcp:188.188.188.188:2016')
proto3 = manager_instance_1.get_protocol('tcp:199.199.199.199:2017')

proto0.addCallback(check_response_0)
proto0.addErrback(response_error)
proto1.addCallback(check_response_1)
proto1.addErrback(response_error)

proto2.addCallback(check_response_2)
proto2.addErrback(response_error)
proto3.addCallback(check_response_3)
proto3.addErrback(response_error)

reactor.run()
```

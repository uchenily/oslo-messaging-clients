#!/usr/bin/env python
#
import optparse, sys, time

from oslo.config import cfg
from oslo import messaging


def main(argv=None):

    _usage = """Usage: %prog [options] <method> [<arg-name> <arg1-value>]*"""
    parser = optparse.OptionParser(usage=_usage)
    parser.add_option("--exchange", action="store", default="my-exchange")
    parser.add_option("--topic", action="store", default="my-topic")
    parser.add_option("--server", action="store", default="my-server-name")
    parser.add_option("--namespace", action="store", default="my-namespace")
    parser.add_option("--fanout", action="store_true")
    parser.add_option("--timeout", action="store", type="int")
    parser.add_option("--cast", action="store_true")
    parser.add_option("--version", action="store", default="1.1")

    opts, extra = parser.parse_args(args=argv)
    print "Calling server, name=%s exchange=%s topic=%s namespace=%s fanout=%s" % (
        opts.server, opts.exchange, opts.topic, opts.namespace,
        str(opts.fanout))

    method = None
    args = None
    if extra:
        method = extra[0]
        extra = extra[1:]
        args = dict([(extra[x], extra[x+1]) for x in range(0, len(extra)-1, 2)])
        print "Method=%s, args=%s" % (method, str(args))

    transport = messaging.get_transport(cfg.CONF, url="qpid://localhost:5672")

    target = messaging.Target(exchange=opts.exchange,
                              topic=opts.topic,
                              namespace=opts.namespace,
                              server=opts.server,
                              fanout=opts.fanout,
                              version=opts.version)

    client = messaging.RPCClient(transport, target,
                                 timeout=opts.timeout,
                                 version_cap=opts.version)

    test_context = {"application": "my-client",
                    "time": time.ctime(),
                    "cast": opts.cast}

    if opts.cast:
        client.cast( test_context, method, **args )
    else:
        rc = client.call( test_context, method, **args )
        print "Return value=%s" % str(rc)

    # endpoints = [
    #     TestEndpoint01(),
    #     TestEndpoint02(),
    #     ]
    # server = messaging.get_rpc_server(transport, target, endpoints)
    # server.start()
    # server.wait()
    return 0

if __name__ == "__main__":
    sys.exit(main())
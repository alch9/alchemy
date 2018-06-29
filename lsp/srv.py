from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher


@dispatcher.add_method
def foobar(**kwargs):
    return kwargs["foo"] + kwargs["bar"]

class T:
    def __init__(self):
        pass

    def aa(self):
        return {
                'a': 1,
                }

@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b
    t = T()
    dispatcher["init"] = t.aa

    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, application)

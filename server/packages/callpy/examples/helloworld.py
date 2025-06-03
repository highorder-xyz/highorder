from callpy import CallPy
from basepy.asynclog import logger

logger.add('stdout')

app = CallPy('helloworld')

@app.route('/')
@app.route('/<foo>/bar')
async def hello_world(request, foo):
    return 'Hello World!'

@app.route('/<foo2>/noarg')
async def hello_world2(request, foo2):
    return 'Hello World!'

@app.route('/<int:number>/num')
async def hello_world3(request, number):
    return 'Hello World! %s'%(number)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000)
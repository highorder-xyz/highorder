from callpy import CallPy

app = CallPy()

@app.route('/')
async def hello(request):
    return 'ok'

app.static('/static', '.')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000)
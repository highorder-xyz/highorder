from basepy.asynclog import logger
from basepy.more.rich_console import install_rich_console
install_rich_console()

from callpy import CallPy

app = CallPy()

@app.route('/')
async def static(request):
    return 'static ok'

app.static('/static/<sub_dir>', './{sub_dir}/', html=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)
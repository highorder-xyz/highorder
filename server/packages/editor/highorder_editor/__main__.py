
from basepy.asynclog import logger
import os
import dataclass_factory
import sys

factory = dataclass_factory.Factory()

logger.add("stdout")

def main(folder, port):
    www_dir = None
    from highorder_editor.view import start_view
    start_view(folder, port, www_dir)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Error: AppFolder not providered.')
        print('python highorder_editor <AppFolder> <Port>')
        sys.exit(-1)
    folder = os.path.abspath(sys.argv[1])
    port = int(sys.argv[2])
    main(folder, port)
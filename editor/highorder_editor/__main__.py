
from basepy.config import settings
from basepy.asynclog import logger
import os
import importlib
import importlib.resources
import dataclass_factory
import sys

factory = dataclass_factory.Factory()

logger.add("stdout")

def main(folder, port):
    www_dir = None
    with importlib.resources.path('highorder_editor', '__init__.py') as f:
        www_dir = os.path.join(os.path.dirname(f), 'www')
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
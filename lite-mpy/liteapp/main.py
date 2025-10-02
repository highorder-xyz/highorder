
from usr.boot import bootup
from usr.render import PageRender
from usr.core import HighOrderCore


def main():
    width, height = bootup()
    core = HighOrderCore(screen_size = (width, height))
    render = PageRender(core)
    render.register()
    core.session_start()


if __name__ == '__main__':
    main()


from wavegui import Q, ui
from urllib.parse import urlparse


def render_layout_main(q:Q, right_panel=False, content_header=True, content_footer=False):
    content_zones = [
        ui.zone('content', direction=ui.ZoneDirection.COLUMN, justify="start"),
    ]
    if content_header:
        content_zones.insert(0, ui.zone('content_header', direction=ui.ZoneDirection.ROW, justify="start"))
    if content_footer:
        content_zones.append(ui.zone('content_footer', direction=ui.ZoneDirection.ROW, justify="start"))
    body_zones = [
        ui.zone('sidebar_body', size='280px', direction=ui.ZoneDirection.COLUMN, justify="start", zones=[
            ui.zone('header'),
            ui.zone('sidebar', direction=ui.ZoneDirection.COLUMN, justify="start"),
        ]),

        ui.zone('content_body', direction=ui.ZoneDirection.COLUMN, zones = content_zones)
    ]
    if right_panel:
        body_zones.append(
            ui.zone('sidebar_right', size='420px', direction=ui.ZoneDirection.COLUMN, zones = [
                ui.zone('content_header_right', direction=ui.ZoneDirection.ROW, justify="start"),
                ui.zone('content_right', direction=ui.ZoneDirection.COLUMN, justify="start"),
            ])
        )
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xl',
            width = '99%',
            zones=[
                # ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=body_zones),
                ui.zone('footer'),
            ]
        )
    ])

def render_layout_simple(q:Q):
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            breakpoint='xl',
            width='99%',
            max_width='400px',
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.COLUMN,size="400px", zones=[
                    ui.zone('simple_header', direction=ui.ZoneDirection.COLUMN),
                    ui.zone('simple_content', direction=ui.ZoneDirection.COLUMN),
                ]),
                ui.zone('footer'),
            ]
        )],
        stylesheets = [
            ui.stylesheet(path='/editor/static/editor.css')
        ]
    )


def get_root_url(q:Q):
    origin = q.headers['origin']
    parsed = urlparse(origin)
    root_url = f'{parsed.scheme}://{parsed.netloc}'
    return root_url


def render_header(q:Q):
    items = []

    q.page['header'] = ui.header_card(
        box = 'simple_header',
        title='HighOrder Editor',
        subtitle='instant build, instant run',
        image="/editor/static/images/highorder_logo.png",
        items=items,
        color="card"
    )

def render_compact_header(q:Q):
    commands = []
    commands.extend([
        ui.command(name='#logout', label='Logout', icon='SignOut')
    ])
    items = []
    items.append(ui.menu(icon="", name="user_menu", items=commands))

    q.page['header'] = ui.header_card(
        box = 'header',
        title='HighOrder',
        subtitle='instant build/run',
        image="/editor/static/images/highorder_logo.png",
        items=items,
        color="card"
    )

def goto_page(q:Q, slash_url:str):
    if not slash_url.startswith('#'):
        raise Exception("slash_url must start with #.")
    q.page['meta'] = ui.meta_card(box='', redirect = slash_url)


def popup_internal_error(q:Q):
    q.page['meta'].dialog = ui.dialog(title="HighOrder Internal ERROR!",
        items=[
            ui.separator(),
            ui.text(content='UNKNOWN INTERNAL ERROR, PLEASE CONTACT ADMIN.', size='l')
        ],
        closable=True
    )

def popup_wrong_page_error(q:Q):
    hash_url = q.args['#']
    q.page['meta'] = ui.meta_card(box='',
        notification_bar =  ui.notification_bar(text=f' URL Not Found ERROR!\nThe page "{hash_url}" not found.',
            type="error",
            position="top-center"
            )
    )


def popup_exception(q:Q, ex:Exception):
    q.page['meta'].notification_bar =  ui.notification_bar(
        text=f'Unhandle Exception: {str(ex)}',
        type="error",
        position="top-center"
    )

def popup_error_msg(q:Q, msg:str):
    q.page['meta'].notification_bar =  ui.notification_bar(
        text=f'{msg}',
        type="error",
        position="top-center"
    )
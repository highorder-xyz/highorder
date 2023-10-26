
import traceback
from highorder_editor.service import Session, User
from wavegui import Q, ui

async def load_user(session_id, q):
    session = await Session.load(session_id=session_id)
    if session:
        user = await User.load(user_id=session.user_id)
        if user:
            q.user['user_id'] = user.user_id
            q.user['email'] = user.email
            q.user['nickname'] = user.nickname
            q.user['instance'] = user
            return True
    return False


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
            zones=[
                ui.zone('header'),
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    ui.zone('sidebar', size='20%'),
                    ui.zone('content', size='60%', direction=ui.ZoneDirection.COLUMN, justify="start"),
                    ui.zone('sidebar_right', size='20%'),
                ]),
                ui.zone('footer'),
            ]
        )
    ])

def render_header(q:Q):
    user_commands = [
        ui.command(name='#profile', label='Profile', icon='Contact'),
        ui.command(name='#logout', label='Logout', icon='SignOut')
    ]

    items = []
    items.append(ui.button(name="#home", icon="Home", label="Home"))
    if 'nickname' in q.user:
        items.append(ui.menu(icon="Contact", name="user_menu", items=user_commands))

    q.page['header'] = ui.header_card(
        box = 'header',
        title='HighOrder Editor',
        subtitle='instant build, instant run',
        image="/editor/static/images/highorder_logo.png",
        items=items,
        color="card"
    )

def render_compact_header(q:Q):
    commands = []
    commands.extend([
        ui.command(name='#home', label='Go Home', icon='Home'),
        ui.command(name='#home', label='Switch App', icon='AllApps')
    ])
    items = []
    if 'nickname' in q.user:
        commands.extend([
            ui.command(name='#profile', label='Profile', icon='Contact'),
            ui.command(name='#logout', label='Logout', icon='SignOut')
        ])
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
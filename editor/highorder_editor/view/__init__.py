
import traceback
from highorder_editor.base.helpers import ApplicationFolder
from wavegui import app, Q, ui, on, handle_on, WaveServer
from basepy.asynclog import logger
from basepy.config import settings
import os
import importlib
import importlib.resources
from highorder_editor.service import Auth, Session
from highorder_editor.service.user import User
from .common import popup_exception, render_header, goto_page, render_layout_simple, popup_wrong_page_error
from . import application, auth
from starlette.responses import FileResponse
from highorder_editor.model import db

def boot_components():
    """Initialize database connection"""
    # SQLite database is already configured in model.py
    from highorder_editor.model import init_db
    init_db()

def load_user(session_id, q):
    """Load user from database session"""
    session = Session.load(session_id)
    if session:
        user = User.load(session.user_id)
        q.user = {
            'user_id': user.user_id,
            'instance': user
        }
        return True
    else:
        q.user = {
            'user_id': None,
            'instance': None
        }
        return False

def render_login_form(email=None, password=None, email_error=None, password_error=None):
    return ui.form_card(box='simple_content', items=[
                ui.textbox(name='email', label='Name or Email', error=email_error, value= email, required=True),
                ui.textbox(name='password', label='Password', password=True, error=password_error, value=password, required=True),
                ui.buttons(justify="center", items=[
                    ui.button(name='login_submit', label='Login', primary=True)
                ])
            ])


@app('/editor')
async def editor_home(q: Q):
    async def try_handle_on(q):
        try:
            if not await handle_on(q):
                popup_wrong_page_error(q)
        except Exception as ex:
            popup_exception(q, ex)
            await logger.error(traceback.format_exc())

    # Use database authentication (SQLite)
    load_user(q.session.session_id, q)
    user = q.user['instance']
    
    if not q.args['#']:
        goto_page(q, '#application')
        await q.page.save()
        return

    if not user:
        if q.args['#'] not in ['login', 'resetpass']:
            goto_page(q, '#login')
        else:
            await try_handle_on(q)
    else:
        await try_handle_on(q)

    await q.page.save()


@on('login_submit')
async def login_submit(q:Q):
    session_id = q.session.session_id
    if q.args.email and q.args.password:
        success, user = Auth.check_pass(q.args.email, q.args.password)

        if success:
            Session.create(session_id=session_id, user_id=user.user_id)

        if success:
            q.page.drop()
            q.page['meta'] = ui.meta_card(box='', redirect = '#')
        else:
            q.page['login'] = render_login_form(q.args.email, q.args.password,
                email_error='email not found' if not user else None,
                password_error= 'password not correct.' if user else None)
    else:
        q.page.drop()
        q.page['meta'] = ui.meta_card(box='', redirect = '#login')
    await q.page.save()

@on('#login')
async def login(q:Q):
    q.page.drop()
    render_layout_simple(q)
    render_header(q)
    q.page['login'] = render_login_form()
    await q.page.save()

@on('#logout')
async def logout(q:Q):
    session_id = q.session.session_id
    Session.delete(session_id)
    goto_page(q, '#')
    q.page['meta'] = ui.meta_card(box='', script=ui.inline_script(content="location.reload(true);"))
    await q.page.save()


async def handle_appfile(request):
    file_path = request.path_params['file_path']
    local_file_path = os.path.join(ApplicationFolder.root_folder, file_path)
    return FileResponse(local_file_path)

def setup_editor(appfolder, www_dir=None):
    if www_dir is None:
        with importlib.resources.path('highorder_editor', '__init__.py') as f:
            www_dir = os.path.join(os.path.dirname(f), 'www')
    app.setup_static(www_dir, 'static')
    app.setup_handler(handle_appfile, 'appfile')
    app.setup_info(name="HighOrder Editor", description="The Editor of HighOrder",
        icon="/editor/static/favicon.ico",
        logo="/editor/static/highorder192.png",
        manifest="/editor/static/manifest.json")


    ApplicationFolder.set_root(appfolder)
    upload_dir = os.path.abspath(ApplicationFolder.get_upload_dir())

    simulator_dir = None
    with importlib.resources.path('highorder_editor', '__init__.py') as f:
        simulator_dir = os.path.join(os.path.dirname(f), 'simulator')
    
    # Initialize database on startup
    boot_components()
    
    server = WaveServer.setup(init_options=dict(upload_dir=upload_dir), on_startup = [], static_dirs ={
        'simulator': simulator_dir
    })
    return server

def start_view(appfolder, port, www_dir=None):
    server = setup_editor(appfolder, www_dir=www_dir)
    server.run_forever(port=port)
    # app.run(on_startup = [], init_options=dict(upload_dir=upload_dir), port=port)
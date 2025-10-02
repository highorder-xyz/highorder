
from wavegui import Q, ui, on
from highorder_editor.service.auth import Auth, Session
from .common import popup_exception, render_header, goto_page, render_layout_simple

def render_login_form(email=None, password=None, email_error=None, password_error=None):
    return ui.form_card(box='simple_content', items=[
                ui.textbox(name='email', label='Name or Email', error=email_error, value= email, required=True),
                ui.textbox(name='password', label='Password', password=True, error=password_error, value=password, required=True),
                ui.buttons(justify="center", items=[
                    ui.button(name='login_submit', label='Login', primary=True)
                ])
            ])

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
    q.page['additonal'] = ui.form_card(box='simple_content', items=[
        ui.label(label="Use CLI to create user first"),
        ui.label(label="python -m highorder_editor.cli create-user email@example.com password")
    ])
    await q.page.save()

@on('#logout')
async def logout(q:Q):
    session_id = q.session.session_id
    Session.delete(session_id)
    q.page['meta'] = ui.meta_card(box='', script=ui.inline_script(content="location.reload(true);"))
    await q.page.save()

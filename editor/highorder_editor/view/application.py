
import re
from highorder_editor.service.application import Application, ApplicationContentService, ApplicationDataFileService, ApplicationSetupService
from wavegui import Q, ui, on
from wavegui.types import Label
from .common import get_root_url, popup_error_msg, popup_exception, render_compact_header, render_header, goto_page, popup_internal_error, render_layout_main
from highorder_editor.base.helpers import get_readable_date, get_readable_filesize, random_string
import json
import datetime
import os
from highorder.base.compiler import Compiler
import asyncio
from urllib.parse import urlparse

from basepy.asynclog import logger

DEVICE_SIZE_MAP = {
    'tv_app': (1920, 1080),
    'desktop_app': (1200, 800),
    'laptop_app': (960, 800),
    'pad_app': (600, 960),
    'mobile_app': (375, 667),
    'miniprogram_app': (375, 667),
    'lite_app': (240, 320)
}

DEVICE_PLATFORM_MAP = {
    'tv_app': 'web',
    'desktop_app': 'web',
    'laptop_app': 'web',
    'pad_app': 'mobile',
    'mobile_app': 'mobile',
    'miniprogram_app': 'miniprogram',
    'lite_app': 'lite'
}

def get_simulator_params(appkey, device_name):
    platform = DEVICE_PLATFORM_MAP[device_name]
    page_size = DEVICE_SIZE_MAP[device_name]
    return f'app_id={appkey["app_id"]}' \
        f'&client_key={appkey["client_key"]}' \
        f'&client_secret={appkey["client_secret"]}' \
        f'&platform={platform}' \
        f'&page_size={page_size[0]}x{page_size[1]}'


def render_sidenav(q:Q, app:Application, selected=None):
    items = [
            ui.nav_group('Base', items=[
                ui.nav_item(name=f'#application/{app.app_id}/app', label='General', icon="Settings"),
                ui.nav_item(name=f'#application/{app.app_id}/clientkeys', label='Client Keys', icon="Permissions")
            ]),
            ui.nav_group('Hola', items=[
                ui.nav_item(name=f"#application/{app.app_id}/content", label="Content", icon="OfflineStorage"),
                ui.nav_item(name=f"#application/{app.app_id}/datafile", label="Data File", icon="PageData"),
                ui.nav_item(name=f'#application/{app.app_id}/hola_editor', label='Hola Editor', icon="CoffeeScript"),
            ]),
            ui.nav_group('Setup', items=[
                ui.nav_item(name=f'#application/{app.app_id}/setup', label='Setup', icon="Onboarding")
            ])
        ]
    q.page['nav'] = ui.nav_card(
        box=ui.box(zone='sidebar'),
        title=f'{app.name}',
        subtitle=f'{app.description}',
        items= items if selected else [],
        value= f'#application/{app.app_id}/{selected}' if selected else None,
        secondary_items= []
    )

def reset_page_container(q:Q, app:Application, page_name=None, right_panel=True,
                         content_header=True, content_footer=False, compact_header=True):
    keys = q.page.data.keys()
    for key in filter(lambda x: x not in ['header', 'nav'], keys):
        del q.page[key]

    render_layout_main(q, right_panel=right_panel, content_header=content_header, content_footer=content_footer)

    q.page['meta'].stylesheets = [
        ui.stylesheet(path='/editor/static/editor.css')
    ]

    # if 'header' not in keys:
    if compact_header:
        render_compact_header(q)
    else:
        render_header(q)
    render_sidenav(q, app, selected=page_name)

def get_status_widget(text, status='normal'):
    return ui.markup(name="status_markup", content=f'''<div class="hola_status_text status_text_{status}">{text}</div>''')

def render_hola_editor(q, hola_content):
    random_id = random_string(6)
    scripts = [ui.script(path='/editor/static/hola/codemirror_hola_editor.iife.js')]
    stylesheets =  [
        ui.stylesheet(path='/editor/static/editor.css')
    ]
    script  =  ui.inline_script(content=f'''
    var inited = 0
    function init_hola_editor() {{
        console.log("try init hola editor")
        inited += 1
        if(inited > 20){{
            return
        }}
        if( !window.hola_editor) {{
            console.log("hola editor not found.")
            return
        }}
        if( !document.getElementById("hola_editor{random_id}")) {{
            console.log("hola_editor{random_id} div not found.")
            return
        }}
        window.hola_editor.hola_editor({{
            code: `{hola_content}`,
            parent_id: "hola_editor{random_id}",
            changed_cb: (code) => {{
                console.log("changed. sync to server.")
                wave.emit("hola_editor", "codechange", code)
            }}
        }})
        clearInterval(hola_editor_initer)
    }}
    var hola_editor_initer = setInterval(() => {{ init_hola_editor() }}, 1000)
    ''',  targets=[f'#hola_editor{random_id}'])

    meta = q.page['meta']
    meta.scripts = scripts
    meta.script = script
    meta.stylesheets = stylesheets

    q.page['hola_editor'] = ui.markup_card(
        box='content',
        title='',
        compact=True,
        content=f'<div class="hola_editor_container"><div id="hola_editor{random_id}" class="hola_editor"></div></div>'
    )

def get_editor_root(origin):
    parsed = urlparse(origin)
    return f'{parsed.scheme}://{parsed.netloc}/editor'

@on('#application')
async def application_home(q:Q):
    q.page.drop()
    render_layout_main(q)
    render_header(q)
    view = ApplicationSummaryView(q)
    await view.handle()
    await q.page.save()

class ApplicationSummaryView:
    def __init__(self, q:Q):
        self.q = q
        self.show_create = True

    async def handle(self):
        q = self.q
        if q.args.create_app_submit:
            await self.create_app()
        elif q.args.create_app_action:
            self.show_create = True
            await self.render()
        else:
            await self.render()

    async def create_app(self):
        q = self.q
        name, description = q.args.name, q.args.description
        name_error = None
        description_error = None
        if not name or len(name) <= 3:
            name_error = 'The length of name must be greater than 3.'
        if not description or len(description) <= 3:
            description_error = 'The length of description must be greater than 3.'

        if name_error or description_error:
            self.show_create = True
            await self.render(name_error=name_error, description_error=description_error)
            return

        user = self.q.user['instance']
        app = await Application.create(name, description, user.user_id)
        if app:
            goto_page(q, f'#application/{app.app_id}/app')
        else:
            popup_internal_error(q)

    def render_action(self):
        return [
            ui.inline(items=[
                ui.label(label=">> To create new App, please "),
                ui.button(name="create_app_action", label="Create Application", primary=True)
            ])
        ]

    def render_app_create(self, name_error=None, description_error=None):
        q = self.q
        return [
            ui.label(label=f'Create Application'),
            ui.textbox(name='name', label='Name of new Application', error=name_error, value=q.args.name, required=True),
            ui.textbox(name='description', label='Description of Application', multiline=True, error=description_error, value=q.args.description, required=True),
            ui.buttons(justify="center", items=[
                ui.button(name='create_app_submit', label='Create Application', primary=True)
            ])
        ]

    def render_apps(self):
        items = []
        items.append(ui.separator())
        user = self.q.user['instance']
        applications = user.list_applications()
        if applications:
            for app in applications:
                items.append(
                    ui.link(label=f"--> {app.name} ({app.description})", path=f"#application/{app.app_id}/app")
                )
        else:
            items.append(
                ui.label(label="No applications, please create one first.")
            )
            self.show_create = True
        return items

    async def render(self, **kwargs):
        items = []
        if self.show_create:
            items.extend(self.render_app_create(name_error=kwargs.get('name_error'), description_error=kwargs.get('description_error')))
        else:
            items.extend(self.render_action())
        items.extend(self.render_apps())
        self.q.page['application_summary'] = ui.form_card(
            box='content',
            title='',
            items=items
        )

class ApplicationGeneralView:
    def __init__(self, q:Q, app:Application):
        self.q = q
        self.app = app

    async def handle(self):
        q = self.q
        app = self.app
        if q.args.application_profile_save:
            name = q.args.application_name
            description = q.args.application_description
            await app.save_profile(name, description)
            await self.render_profile()
        else:
            await self.render_all()

    async def render_profile(self, **kwargs):
        q = self.q
        items = []
        name = self.app.name
        description = self.app.description
        items.append(ui.textbox(name='application_name', label='Application Name',
            value=f"{name}", required=True, trigger=False))
        items.append(ui.textbox(name='application_description', label='Application Description',
            value=f"{description}", required=True, trigger=False))
        q.page['profile'] = ui.form_card(box='content', items=items)

    async def render_app_info(self, **kwargs):
        q = self.q
        app = self.app
        q.page['appinfo'] = ui.tall_info_card(
            box=ui.box(zone='content', size="0"),
            name='info_card',
            title=f'App: {app.name}',
            caption=f'{app.description}',
            category=f'app_id: {app.app_id}',
        )
        q.page['appinfo_copy'] = ui.form_card(
            box=ui.box(zone='content', size="0"),
            items=[
                ui.copyable_text(label='Application ID', value=f'{app.app_id}')
            ]
        )

    async def render_all(self):
        q = self.q
        reset_page_container(q, self.app, page_name='app', right_panel=True)
        await self.render_app_info()
        await self.render_profile()


    @on('#application/{application_id:str}/app')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        view = ApplicationGeneralView(q, app)
        await view.handle()
        await q.page.save()

class ClientKeysView:
    def __init__(self, q, clientkeys):
        self.q = q
        self.clientkeys = clientkeys

    def render_clientkeys(self):
        q = self.q
        clientkeys = self.clientkeys
        if not clientkeys:
            return
        rows = []
        for idx, clientkey in enumerate(clientkeys):
            rows.append(
                ui.table_row(name=f"{clientkey['client_key']}", cells=[clientkey['client_key'], clientkey['client_secret']])
            )
        commands = [
            ui.command(name='copy_client_key_secret', label='Copy Client Key & Secret', icon='Copy'),
        ]
        q.page['clientkeys'] = ui.form_card(box='content', items=[
            ui.table(
                name='table',
                columns=[
                    ui.table_column(name="client_key", label="Client Key"),
                    ui.table_column(name="client_secret", label="Client Secret",  max_width="400px",),
                    ui.table_column(name='actions', label='Actions', max_width="80px", cell_type=ui.menu_table_cell_type(name='commands', commands=commands))],
                rows=rows
            )
        ])


    def render_toolbar(self):
        self.q.page['toolbar'] = ui.toolbar_card(
            box=ui.box(zone='content', height="48px"),
            items=[
                ui.command( name='new', label='New', icon='Add', items=[
                        ui.command(name='new_client_key', label='Create New Client Key Pair', icon=''),
                    ]
                )
            ],
        )

    def render(self):
        self.render_toolbar()
        self.render_clientkeys()

    @on('#application/{application_id:str}/clientkeys')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        if q.args.copy_client_key_secret:
            client_key = q.args.copy_client_key_secret
            client_secret = await app.get_client_secret(client_key)
            v = {
                "appId": application_id,
                "clientKey": client_key,
                "clientSecret": client_secret
            }
            q.page['meta'].dialog = ui.dialog(title='Copy Client Keys', closable=True, items=[
                ui.copyable_text(label='', value=json.dumps(v, indent=4), multiline=True, height="160px"),
            ])
            await q.page.save()
            return
        reset_page_container(q, app, page_name='clientkeys')
        if q.args['new_client_key'] == True:
            await app.create_client_key()
        clientkeys = await app.get_valid_clientkeys()
        view = ClientKeysView(q, clientkeys)
        view.render()
        await q.page.save()


class ApplicationContentView:
    def __init__(self, app, q, collection='main'):
        self.app = app
        self.q = q
        self.collection = collection
        self.service = None

    async def get_service(self):
        if self.service == None:
            self.service = await ApplicationContentService.load(self.app.app_id)
        return self.service

    async def get_collections(self):
        service = await self.get_service()
        return service.get_collections()

    async def save_content(self, contents):
        service = await self.get_service()
        await service.save_files(self.collection, contents)


    async def get_contents(self, page=1):
        service = await self.get_service()
        return await service.get_files(self.collection, page=page)

    async def delete_content(self, content_file):
        service = await self.get_service()
        await service.delete_file(self.collection, content_file)

    async def show_new_collection_dialog(self):
        self.q.page['meta'].dialog = ui.dialog(title='Create new collection',
            items=[
                ui.textbox(
                    name="collection_name",
                    label= "Please enter name for collection.",
                    required = True
                ),
                ui.buttons([ui.button(name='new_collection_submit', label='Create Collection', primary=True)])
            ],
            closable = True,
            blocking = True
        )

    async def show_content_info_dialog(self, collection, name):
        ext = os.path.splitext(name)[-1]
        items=[
            ui.text(content=name),
        ]
        url_root = get_editor_root(self.q.headers['origin'])
        link = f'{url_root}/appfile/APP_{self.app.app_id}/content/{collection}/{name}'
        if ext.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
            items.append(
                ui.image(title=name, path=link, width="400px")
            )
        items.append(ui.link(label = "Open in New Tab", path=link, download=True, button=True, target='_blank'))
        self.q.page['meta'].dialog = ui.dialog(title='',
            items = items,
            closable = True,
            blocking = True
        )

    async def new_collection(self, collection_name):
        if not collection_name or len(collection_name) < 3:
            return
        service = await self.get_service()
        await service.add_collection(collection_name)

    async def render(self):
        await self.render_collection_bar()
        await self.render_upload()
        await self.render_content()


    async def render_content(self):
        rows = []
        contents = await self.get_contents() or []
        for filerecord in contents:
            rows.append(
                ui.table_row(
                    name = filerecord.name,
                    cells = [filerecord.name,
                        get_readable_filesize(filerecord.size),
                        filerecord.media_type,
                        get_readable_date(filerecord.uploaded)
                    ]
                )
            )
        commands = [
            ui.command(name='delete_content', label='Delete', icon='Cancel'),
        ]
        self.q.page['content_table'] = ui.form_card(
            box=ui.box(zone='content', size='0'),
            items=[
                ui.table(
                    name='content_tableview',
                    columns=[
                        ui.table_column(name='name', label='Name', min_width='200px', sortable=True, searchable = True),
                        ui.table_column(name='size', label='Size', min_width='60px', sortable=True),
                        ui.table_column(name='media_type', min_width='80px', label='Data Type'),
                        ui.table_column(name='uploaded_at', min_width='120px', label='Uploaded Date', sortable=True),
                        ui.table_column(name='actions', label='Actions', min_width="80px",
                            cell_type=ui.menu_table_cell_type(name='commands', commands=commands))
                    ],
                    rows = rows,
                    events = ['sort']
                )
        ])

    async def render_upload(self):
        self.q.page['content_upload'] = ui.form_card(
            box=ui.box(zone='content', size='0'),
            items=[
                ui.text_xl(f'Upload files to collection {self.collection}'),
                ui.file_upload(name='content_files', height='150px', label='Upload Now', multiple=True),
        ])


    async def render_collection_bar(self):
        collections = await self.get_collections()
        items = [
            ui.inline(items = [
                ui.dropdown(
                    name='content_collection',
                    choices=[
                        ui.choice(name=f'{name}', label=f'{name}') for name in collections
                    ],
                    value = self.collection,
                    width = '240px',
                    required = True,
                    trigger = True
                ),
                ui.button(name='new_content_collection', label='New Content Collection')
            ])

        ]
        self.q.page['content_collection_header'] = ui.form_card(
            box=ui.box(zone='content_header'),
            title="Current Collection Name",
            items=items
        )


    @on('#application/{application_id:str}/content')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        collection = q.args.content_collection or 'main'
        contentview = ApplicationContentView(app, q, collection)
        reset_page_container(q, app, page_name='content')
        content_files = q.args.content_files
        delete_content = q.args.delete_content
        if q.args.new_collection_submit:
            collection_name = q.args.collection_name
            await contentview.new_collection(collection_name)
        elif q.args.new_content_collection:
            await contentview.show_new_collection_dialog()
        elif delete_content:
            await contentview.delete_content(delete_content)
        elif content_files and isinstance(content_files, (list, tuple)):
            await contentview.save_content(content_files)
        elif q.args.content_tableview:
            await contentview.show_content_info_dialog(q.args.content_collection, q.args.content_tableview[0])
        await contentview.render()
        await q.page.save()


class ApplicationDataFileView:
    def __init__(self, app, q):
        self.app = app
        self.q = q
        self.service = None

    async def get_service(self):
        if self.service == None:
            self.service = await ApplicationDataFileService.load(self.app.app_id)
        return self.service

    async def save_datafile(self, data_files):
        df = await self.get_service()
        await df.save_files(data_files)


    async def get_datafiles(self, page=1):
        df = await self.get_service()
        return await df.get_files(page=page)

    async def delete_datafile(self, datafile):
        df = await self.get_service()
        await df.delete_file(datafile)

    async def render(self):
        await self.render_upload()
        await self.render_content()


    async def show_content_info_dialog(self, name):
        ext = os.path.splitext(name)[-1]
        items=[
            ui.text(content=name),
        ]
        url_root = get_editor_root(self.q.headers['origin'])
        link = f'{url_root}/appfile/APP_{self.app.app_id}/datafile/{name}'
        items.append(ui.link(label = "Open in New Tab", path=link, download=True, button=True, target='_blank'))
        self.q.page['meta'].dialog = ui.dialog(title='',
            items = items,
            closable = True,
            blocking = True
        )

    async def render_content(self):
        files = await self.get_datafiles()
        rows = []
        for filerecord in files:
            rows.append(
                ui.table_row(
                    name = filerecord.name,
                    cells = [filerecord.name,
                        get_readable_filesize(filerecord.size),
                        filerecord.media_type,
                        get_readable_date(filerecord.uploaded)
                    ]
                )
            )
        commands = [
            ui.command(name='delete_datafile', label='Delete', icon='Cancel'),
        ]
        self.q.page['datafile_tableview'] = ui.form_card(
            box=ui.box(zone='content'),
            items=[
                ui.table(
                    name='datafile_table',
                    columns=[
                        ui.table_column(name='name', label='Name', min_width='200px', sortable=True),
                        ui.table_column(name='size', label='Size', min_width='60px',sortable=True),
                        ui.table_column(name='media_type',min_width='100px', label='Data Type'),
                        ui.table_column(name='uploaded_at', label='Uploaded Date', min_width='120px', sortable=True),
                        ui.table_column(name='actions', label='Actions', min_width="80px",
                            cell_type=ui.menu_table_cell_type(name='commands', commands=commands))
                    ],
                    rows = rows,
                    events = ['sort']
                )
        ])

    async def render_upload(self):
        self.q.page['datafile_upload'] = ui.form_card(
            box=ui.box(zone='content', size='0'),
            items=[
                ui.text_xl(f'Upload some json data files'),
                ui.file_upload(name='datafile_files',
                        label='Upload Now',
                        file_extensions=['.json'],
                        height='150px',
                        multiple=True),
        ])


    @on('#application/{application_id:str}/datafile')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        dataview = ApplicationDataFileView(app, q)
        reset_page_container(q, app, page_name='datafile')
        data_files = q.args.datafile_files
        delete_datafile = q.args.delete_datafile
        if delete_datafile:
            await dataview.delete_datafile(delete_datafile)
        elif data_files and isinstance(data_files, (list, tuple)):
            await dataview.save_datafile(data_files)
        elif q.args.datafile_table:
            await dataview.show_content_info_dialog(q.args.datafile_table[0])
        await dataview.render()
        await q.page.save()

class ApplicationHolaEditorView:
    def __init__(self, q:Q, app:Application):
        self.q = q
        self.app = app

    async def handle(self):
        q = self.q
        app = self.app
        if q.events.hola_editor:
            new_code = q.events.hola_editor['codechange']
            if new_code:
                try:
                    c = Compiler()
                    json_obj = c.compile(new_code)
                    await app.save_hola_code(new_code)
                    await app.save_hola_json(json_obj)
                except Exception as ex:
                    await self.update_status(f'Not Saved (Syntax ERROR).', 'failed')
                    await logger.exception(ex)
                else:
                    now = get_readable_date(datetime.datetime.now(), short=True)
                    await self.update_status(f'Saved ({now}).', 'succeed')
            return
        elif q.args.refresh_simulator:
            await self.render_simulator(q.args.simulator_selected)
            return
        elif q.args.simulator_selected:
            await self.render_simulator(q.args.simulator_selected)
        else:
            await self.render_all()

    async def update_status(self, text, status='normal'):
        status_widget = get_status_widget(text, status)
        await self.render_header(status_widget)

    async def render_simulator(self, device_name:str = "mobile_app"):
        q = self.q
        app = self.app
        valid_keys = await app.get_valid_clientkeys()
        if not valid_keys:
            return
        appkey = valid_keys[0]
        url_root = self.q.headers['origin']
        editor_root = f'{url_root}/editor'
        simulator_param = get_simulator_params(appkey, device_name)
        simulator_link = f'{url_root}/simulator/?{simulator_param}'
        q.page['simulator_action'] = ui.form_card(
            box=ui.box(zone='content_header_right', size='0'),
            title="",
            items=[
                ui.inline([
                    ui.button(name='refresh_simulator', label='Refresh'),
                    ui.dropdown(name='simulator_selected', width="160px", label='', trigger=True, choices=[
                        ui.choice(name='mobile_app', label='Android/iOS'),
                        ui.choice(name='miniprogram_app', label='Wechat MP'),
                        ui.choice(name='lite_app', label='Watch/Lite'),
                    ], value=f"{device_name}"),
                    ui.button(name='open_standalone_simulator', label='Web/Desktop', icon="OpenInNewWindow",
                            path=f'{editor_root}#application/{app.app_id}/simulator')
                ], justify="start")

            ]
        )

        device_size = DEVICE_SIZE_MAP[device_name]
        q.page['simulator_view'] = ui.form_card(
            box=ui.box(zone='content_right'),
            title='',
            items = [
                ui.frame(
                    height=f'{device_size[1]}px',
                    width=f'{device_size[0]}px',
                    path=simulator_link,
                    visible=True
                )
            ]
        )

    async def render_header(self, status_widget = None):
        q = self.q
        app = self.app
        url_root = self.q.headers['origin']
        editor_root = f'{url_root}/editor'
        _status_widget = status_widget or ui.markup(name='status_markup', content='''''')
        _dir1_value = q.args.hola_dir1 or 'root'
        _file_value = q.args.hola_file or 'main.hola'
        q.page['hola_header'] = ui.form_card(
            box='content_header',
            items=[
                ui.inline([
                    ui.dropdown(name='hola_dir1', width="160px", label='', trigger=True, choices=[
                        ui.choice(name='root', label='--')
                    ], value=f"{_dir1_value}"),
                    ui.dropdown(name='hola_file', width="200px", label='', trigger=True, choices=[
                        ui.choice(name='main.hola', label='main.hola'),
                    ], value=f"{_file_value}"),
                    ui.button(name='open_astview', label='AST', icon="OpenInNewWindow",
                            path=f'{editor_root}#application/{app.app_id}/astview'),
                    _status_widget
                ], justify="start")
            ]
        )

    async def render_hola_editor(self, hola_content = None):
        render_hola_editor(self.q, hola_content)


    async def render_all(self):
        q = self.q
        app = self.app
        code = await app.get_hola_code()
        reset_page_container(q, app, page_name='hola_editor',
                            right_panel=True, content_header=True, content_footer=False)
        await self.render_header()
        await self.render_hola_editor(code)
        await self.render_simulator()


    @on('#application/{application_id:str}/hola_editor')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        view = ApplicationHolaEditorView(q, app)
        await view.handle()
        await q.page.save()


class ApplicationSimulatorView:
    def __init__(self, q:Q, app:Application):
        self.q = q
        self.app = app

    async def handle(self):
        q = self.q
        app = self.app
        await self.render_all()


    async def render_simulator_header(self, device_name: str = 'desktop_app'):
        q = self.q
        app = self.app
        q.page['simulator_action'] = ui.form_card(
            box=ui.box(zone='simulator_header', size='0'),
            title="",
            items=[
                ui.inline([
                    ui.inline([
                        ui.label(label='HighOrder Simulator')
                    ]),
                    ui.inline([
                        ui.button(name='refresh_simulator', label='Refresh'),
                        ui.dropdown(name='simulator_selected', width="300px", label='', trigger=True, choices=[
                            ui.choice(name='tv_app', label='TV XXLarge Screen'),
                            ui.choice(name='desktop_app', label='Web/Desktop XLarge Screen'),
                            ui.choice(name='laptop_app', label='Web/Laptop/Desktop Large Screen'),
                            ui.choice(name='pad_app', label='Web/Pad Medium Screen'),
                            ui.choice(name='mobile_app', label='Web/Android/iOS'),
                            ui.choice(name='miniprogram_app', label='Wechat MiniProgram'),
                            ui.choice(name='lite_app', label='Watch/Lite'),
                        ], value=f"{device_name}"),
                    ], justify="center"),
                    ui.inline([
                        ui.label(label=f'APP: {app.name}'),
                    ])
                ], justify="between")
            ]
        )

    async def render_simulator(self, device_name: str = 'desktop_app'):
        q = self.q
        app = self.app
        valid_keys = await app.get_valid_clientkeys()
        if not valid_keys:
            return
        appkey = valid_keys[0]
        url_root = self.q.headers['origin']
        simulator_param = get_simulator_params(appkey, device_name)
        simulator_link = f'{url_root}/simulator/?{simulator_param}'

        device_size = DEVICE_SIZE_MAP[device_name]
        q.page['simulator_view'] = ui.form_card(
            box=ui.box(zone='simulator'),
            title='',
            items = [
                ui.frame(
                    height=f'{device_size[1]}px',
                    width=f'{device_size[0]}px',
                    path=simulator_link,
                    visible=True
                )
            ]
        )

    async def render_all(self):
        q = self.q
        device_name = 'desktop_app'
        if q.args.simulator_selected:
            device_name = q.args.simulator_selected
        # reset_page_container(q, self.app, page_name='setup', right_panel=False)
        q.page.drop()
        q.page['meta'] = ui.meta_card(box='',
            layouts=[
                ui.layout(
                    breakpoint='xl',
                    width = '100%',
                    zones=[
                        ui.zone('simulator_header'),
                        ui.zone('simulator', direction=ui.ZoneDirection.COLUMN)
                    ]
            )],
            stylesheets =  [
                ui.stylesheet(path='/editor/static/editor.css')
            ]
        )
        await self.render_simulator_header(device_name)
        await self.render_simulator(device_name)

    @on('#application/{application_id:str}/simulator')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        view = ApplicationSimulatorView(q, app)
        await view.handle()
        await q.page.save()


class ApplicationASTView:
    def __init__(self, q:Q, app:Application):
        self.q = q
        self.app = app

    async def handle(self):
        q = self.q
        app = self.app
        await self.render_all()

    async def render_header(self):
        q = self.q
        app = self.app
        q.page['astview_action'] = ui.form_card(
            box=ui.box(zone='astview_header', size='0'),
            title="",
            items=[
                ui.inline([
                    ui.inline([
                        ui.label(label='HighOrder AST View')
                    ]),
                    ui.inline([
                        ui.dropdown(name='hola_dir1', width="160px", label='', trigger=True, choices=[
                            ui.choice(name='root', label='--')
                        ], value="root"),
                        ui.dropdown(name='hola_file', width="200px", label='', trigger=True, choices=[
                            ui.choice(name='main.hola', label='main.hola'),
                        ], value="main.hola")
                    ], justify="center"),
                    ui.inline([
                        ui.label(label=f'APP: {app.name}'),
                    ])
                ], justify="between")
            ]
        )

    async def render_ast_json_editor(self, json_content = None):
        q = self.q
        app = self.app
        jsoncontent = json.dumps(json_content or {})
        random_id = random_string(6)
        scripts = [ui.script(path='/editor/static/jsoneditor/jsoneditor.min.js')]
        stylesheets =  [ui.stylesheet(path='/editor/static/jsoneditor/jsoneditor.min.css'),
                    ui.stylesheet(path='/editor/static/editor.css')
                ]
        script  =  ui.inline_script(content=f'''
                var inited = 0
                function init_json_editor() {{
                    inited += 1
                    if(inited > 20){{
                        return
                    }}
                    if( !window.JSONEditor) {{
                        return
                    }}
                    if(window.jsoneditor){{
                        window.jsoneditor.destroy();
                        window.jsoneditor = undefined;
                    }}
                    window.jsoneditor = new JSONEditor(document.getElementById("jsonviewer{random_id}"), {{
                        modes: ["view", "code"]
                    }}, {jsoncontent})
                    window.jsoneditor.expandAll()
                    clearInterval(json_initer)
                }}
                var json_initer = setInterval(init_json_editor, 1000)

            ''',  targets=[f'#jsonviewer{random_id}'])

        meta = q.page['meta']
        meta.scripts = scripts
        meta.script = script
        meta.stylesheets = stylesheets

        q.page['jsonviewer'] = ui.markup_card(
            box='astview',
            title='',
            compact=True,
            content=f'<div id="jsonviewer{random_id}" class="custom-json-viewer"></div>'
        )


    async def render_all(self):
        q = self.q
        app = self.app
        config = await app.get_hola_json()
        q.page.drop()
        q.page['meta'] = ui.meta_card(box='',
            layouts=[
                ui.layout(
                    breakpoint='xl',
                    width = '100%',
                    zones=[
                        ui.zone('astview_header'),
                        ui.zone('astview', direction=ui.ZoneDirection.COLUMN,
                                    justify="center", align="center")
                    ]
            )],
            stylesheets =  [
                ui.stylesheet(path='/editor/static/editor.css')
            ]
        )
        await self.render_header()
        await self.render_ast_json_editor(config)


    @on('#application/{application_id:str}/astview')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        view = ApplicationASTView(q, app)
        await view.handle()
        await q.page.save()


class ApplicationSetupView:
    def __init__(self, q:Q, app:Application):
        self.q = q
        self.app = app

    async def load_setup_service(self):
        root_url = get_root_url(self.q)
        svc = await ApplicationSetupService.load(self.app.app_id, root_url)
        return svc


    async def handle(self):
        q = self.q
        app = self.app
        if q.events.hola_editor:
            new_code = q.events.hola_editor['codechange']
            if new_code:
                try:
                    c = Compiler()
                    json_obj = c.compile(new_code)
                    setup_svc = await self.load_setup_service()
                    await setup_svc.save_setup_hola(new_code)
                except Exception as ex:
                    await self.update_status(f'Not Saved (Syntax ERROR).', 'failed')
                    await logger.exception(ex)
                else:
                    now = get_readable_date(datetime.datetime.now(), short=True)
                    await self.update_status(f'Saved ({now}).', 'succeed')
            return
        elif q.args.run_setup:
            await self.show_setup_process_dialog()
            await self.render_header()
            q.page['meta'].notification_bar = None
            await q.page.save()
            try:
                setup_svc = await self.load_setup_service()
                await setup_svc.run_setup()
                await asyncio.sleep(1.0)
                status_widget = get_status_widget(f'Setup OK', 'succeed')
                await self.render_header(status_widget)
            except Exception as ex:
                status_widget = get_status_widget(f'Setup Failed.', 'failed')
                await self.render_header(status_widget)
                popup_exception(q, ex)
            await self.close_dialog()
        else:
            await self.render_all()

    async def show_setup_process_dialog(self):
        self.q.page['meta'].dialog = ui.dialog(title='Setup Server',
            items=[
                ui.text(f'Setup Server... It may take several minutes')
            ],
            closable = False,
            blocking = True
        )

    async def close_dialog(self):
        self.q.page['meta'].dialog = None

    async def update_status(self, text, status='normal'):
        status_widget = get_status_widget(text, status)
        await self.render_header(status_widget)

    async def render_header(self, status_widget=None):
        q = self.q
        app = self.app
        _staus_widget = status_widget or ui.markup(content="")
        q.page['setup_action'] = ui.form_card(
            box=ui.box(zone='content_header'),
            title="",
            items=[
                ui.inline([
                    ui.button(name='run_setup', label='Run Setup'),
                    _staus_widget
                ], justify="start")
            ]
        )


    async def render_setup(self):
        setup_svc = await self.load_setup_service()
        hola_code = setup_svc.hola
        render_hola_editor(self.q, hola_code)

    async def render_all(self):
        q = self.q
        reset_page_container(q, self.app, page_name='setup',
                            right_panel=True, content_header=True, content_footer=False)
        await self.render_header()
        await self.render_setup()


    @on('#application/{application_id:str}/setup')
    @staticmethod
    async def service(q:Q, application_id:str):
        app = await Application.load(application_id)
        view = ApplicationSetupView(q, app)
        await view.handle()
        await q.page.save()

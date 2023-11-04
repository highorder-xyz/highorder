
from postmodel import Postmodel
from basepy.config import settings
from highorder.base.model import DB_NAME

async def boot_components():
    db_url = settings.server.db_url
    await Postmodel.init(db_url, name=DB_NAME, modules = ["highorder.hola.model"])
    await Postmodel.generate_schemas()
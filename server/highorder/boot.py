
from postmodel import Postmodel
from basepy.config import settings

async def boot_components():
    db_url = settings.server.db_url
    await Postmodel.init(db_url, name='default',
        modules = ["highorder.account.model", "highorder.hola.model"])
    await Postmodel.generate_schemas()
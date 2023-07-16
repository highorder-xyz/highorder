
from postmodel import Postmodel
from basepy.config import settings

async def boot_components():
    db_url = settings.app.db_url
    await Postmodel.init(db_url,
        modules = ["highorder.account.model", "highorder.hola.model"])
    await Postmodel.generate_schemas()
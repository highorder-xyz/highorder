from postmodel import Postmodel
from basepy.config import settings
from highorder.base.model import DB_NAME

async def boot_components():
    db_url = settings.db_url
    await Postmodel.init(db_url, name=DB_NAME, modules = ["highorder.hola.model", "highorder.base.instant_db"])
    # await Postmodel.generate_schemas()
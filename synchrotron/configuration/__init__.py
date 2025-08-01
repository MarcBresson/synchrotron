from pydantic import BaseModel, TypeAdapter

from .comparaison import AllComparaisonDiscriminator
from .filter import Filters
from .storage import Storage
from .synchronisation import Synchronisation


class OneConfig(BaseModel):
    filters: Filters
    synchronisation: Synchronisation
    comparaison: AllComparaisonDiscriminator
    left: Storage
    right: Storage


Configs = TypeAdapter(list[OneConfig])

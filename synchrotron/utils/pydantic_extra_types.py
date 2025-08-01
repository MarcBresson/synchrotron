from datetime import timedelta
from typing import Annotated

from isodate import parse_duration
from pydantic import BeforeValidator

type Duration = Annotated[timedelta, BeforeValidator(parse_duration)]

from __future__ import annotations

import datetime as _dt
from dateutil import tz


def utc_today() -> _dt.date:
    return _dt.datetime.now(tz=tz.UTC).date()


def iso(d: _dt.date) -> str:
    return d.isoformat()

from datetime import datetime

import pytest
import pytz

from app.utils import get_utc_datetime, get_utc_offset


# ======================== Test get_utc_offset ========================
@pytest.mark.asyncio
async def test_get_utc_offset():
    # Create a know date and time zone
    time_zone = pytz.timezone("America/Merida")
    datetime_test = datetime.now(time_zone)
    offset = get_utc_offset(time_zone.zone, datetime_test)
    # Offset between America/Merida and UTC is -6 hours (-21600 seconds)
    assert offset == -21600


@pytest.mark.asyncio
async def test_get_utf_offset_no_date():
    # Test with no date
    time_zone = pytz.timezone("America/Merida")
    offset = get_utc_offset(time_zone.zone)
    # Offset between America/Merida and UTC is -6 hours (-21600 seconds)
    assert offset == -21600


@pytest.mark.asyncio
async def test_get_utc_to_utc():
    # Test with UTC time zone
    time_zone = pytz.timezone("UTC")
    datetime_test = datetime.now(time_zone)
    offset = get_utc_offset(time_zone.zone, datetime_test)
    # Offset between UTC and UTC is 0 hours (0 seconds)
    assert offset == 0


# ======================== Test get_utc_datetime ========================
@pytest.mark.asyncio
async def test_get_utc_datetime():
    # Create a know date and time zone
    time_zone = pytz.timezone("America/Merida")
    datetime_test = datetime(
        year=2024, month=1, day=1, hour=0, minute=0, second=0
    )
    utc_datetime = get_utc_datetime(time_zone.zone, datetime_test)
    # Offset between America/Merida and UTC is -6 hours (-21600 seconds)
    assert utc_datetime == datetime(
        year=2024,
        month=1,
        day=1,
        hour=6,
        minute=0,
        second=0,
        tzinfo=pytz.utc,
    )

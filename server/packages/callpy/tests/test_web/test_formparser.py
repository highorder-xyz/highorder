
from callpy.web.formparsers import QueryStringParser, MultiPartParser, FormParser
import pytest

def test_query_strint_parser():
    p = QueryStringParser()
    p.feed(b'a=b&b=c')
    p.feed(b'')
    msgs = p.gets()
    assert len(msgs) == 2
    assert msgs[0] == ('a', 'b')
    assert msgs[1] == ('b', 'c')

def test_query_strint_parser2():
    p = QueryStringParser()
    p.feed(b'token=VFPBO5V7Lzk2x4yK7BGTHUGu&team_id=TPU6WMS2U&team_domain=pyflowspace&channel_id=CPU6WMW48&channel_name=dev_test_for_will&user_id=UPFEHE9DY&user_name=zeaphoo&command=%2Fteamflow_dev&text=&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FTPU6WMS2U%2F1208522101956%2FunuW2bmpPBoUtyEvxP8lSXr2&trigger_id=1202550422931.810234740096.00f7c7953f5531ba3695bafdc81db72d')
    p.feed(b'')
    msgs = p.gets()
    assert len(msgs) == 11
    msgs = dict(msgs)
    assert msgs['token'] == 'VFPBO5V7Lzk2x4yK7BGTHUGu'
    assert msgs['text'] == ''
    assert msgs['response_url'] == 'https://hooks.slack.com/commands/TPU6WMS2U/1208522101956/unuW2bmpPBoUtyEvxP8lSXr2'

async def form_data_stream():
    yield b'a=b&b=c'
    yield b''
    return

@pytest.mark.asyncio
async def test_query_form_parser():
    p = FormParser(None, form_data_stream())
    msgs = await p.parse()
    assert len(msgs) == 2
    assert msgs['a'] == 'b'
    assert msgs['b'] == 'c'


simple_field_form = b'''------WebKitFormBoundaryTkr3kCBQlBe1nrhc\r
Content-Disposition: form-data; name="field"\r
\r
This is a test.\r
------WebKitFormBoundaryTkr3kCBQlBe1nrhc--'''

@pytest.mark.asyncio
async def test_form_data_parser():
    p = MultiPartParser(None, None)
    boundary = b'----WebKitFormBoundaryTkr3kCBQlBe1nrhc'
    p.boundary = boundary
    await p.feed(simple_field_form)
    await p.feed('')
    assert len(p.parts) == 1
    part = p.parts[0]
    assert part.get() == ('field', "This is a test.")
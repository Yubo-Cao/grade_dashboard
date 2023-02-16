import asyncio
import json
from contextlib import asynccontextmanager
from typing import Literal

import aiohttp
from lxml.etree import HTML
from yarl import URL

from .exception import SpiderIOException
from .utils import (
    cached,
    chunked,
    find,
    first,
    get_var,
    identifier,
    submit,
)


@cached
async def cookie():
    return aiohttp.CookieJar(unsafe=True)


@cached
async def session():
    return aiohttp.ClientSession(
        cookie_jar=await cookie(),
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        },
    )


async def on_exit():
    await (await session()).close()


DASHBOARD_URL = URL("https://apps.gwinnett.k12.ga.us/")


def resolve_url(url: str | URL, base_url: URL) -> URL:
    return (
        URL(url)
        if URL(url).is_absolute()
        else URL(base_url / url)
        if isinstance(url, str)
        else base_url.join(url)
    )


@cached
async def login(username: str, password: str) -> bool:
    s = await session()
    async with s.post(
        DASHBOARD_URL / "pkmslogin.form",
        data={
            "forgotpass": "p0/IZ7_3AM0I440J8GF30AIL6LB453082=CZ6_3AM0I440J8GF30AIL6LB4530G6=LA0=OC=Eaction!ResetPasswd==/#Z7_3AM0I440J8GF30AIL6LB453082",
            "login-form-type": "pwd",
            "username": username,
            "password": password,
        },
    ) as r:
        return r.ok


@cached
async def apps() -> list[tuple[str, URL]]:
    s = await session()
    url = DASHBOARD_URL / "dca" / "student" / "dashboard"
    async with s.get(url) as r:
        text = await r.text()
        html = HTML(text)
        apps = [
            (
                identifier(name),
                resolve_url(href, DASHBOARD_URL),
            )
            for name, href in [
                (first(li.xpath("a/span/text()")), first(li.xpath("a/@href")))
                for li in html.xpath(
                    '//*[text()="MY eCLASS Apps"]/following-sibling::ul/li'
                )
            ]
            if href and name
        ]
        return apps


@cached
async def vue_url() -> URL:
    return find(await apps(), "my_student_vue")


@cached
async def vue():
    s = await session()
    async with s.get(await vue_url()) as r:
        text = await r.text()
    async with submit(s, text) as r:
        return r.url.parent, await r.text()


@cached
async def vue_base_url():
    VUE_BASE_URL, _ = await vue()
    return VUE_BASE_URL


@cached
async def vue_script():
    _, html_raw = await vue()
    html = HTML(html_raw.encode("utf-8"))
    script = html.xpath("//head/script[1]/text()")[0]
    return script


@cached
async def grade_book_url():
    return find(await navigations(), "grade_book")


@cached
async def navigations():
    return [
        (
            identifier(nav.get("description")),
            resolve_url(URL(nav.get("url")), await vue_base_url()),
        )
        for nav in get_var("PXP.NavigationData", await vue_script())["items"]
    ]


@cached
async def grade_book():
    s = await session()
    async with s.get(await grade_book_url()) as r:
        text = await r.text()
        return HTML(text.encode("utf-8"))


@cached
async def courses():
    html = await grade_book()
    rows = chunked(
        html.xpath(
            '//div[@id="gradebook-content"]'
            '//div[contains(@class, "header")]'
            '/following-sibling::div[div[contains(@class, "row")]]'
            "/div"
        ),
        2,
    )
    return [
        dict(
            course=first(header.xpath("div[1]/button/text()")),
            teacher=first(
                header.xpath('.//span[contains(@class, "teacher")]//a/text()')
            ),
            grade=first(content.xpath('.//span[contains(@class, "mark")]/text()')),
            params=json.loads(first(header.xpath(".//button/@data-focus"))),
        )
        for header, content in rows
    ]


async def load_control(control_name: str, params: dict[str, any]) -> dict:
    s = await session()
    url = (await vue_base_url()) / "service" / "PXP2Communication.asmx" / "LoadControl"
    data = dict(request=dict(control=control_name, parameters=params))
    async with s.post(
        url,
        json=data,
        headers={"X-Requested-With": "XMLHttpRequest"},
    ) as r:
        if not r.ok:
            raise SpiderIOException(f'Failed to load "{control_name}"', r)
        return await r.json()


async def load_course(course):
    await load_control(
        course["params"]["LoadParams"]["ControlName"],
        course["params"]["FocusArgs"],
    )


course_lock = asyncio.Lock()


@asynccontextmanager
async def course(course: dict[str, any] | int | str):
    if isinstance(course, int):
        course = (await courses())[course]
    elif isinstance(course, str):
        course = first(
            (
                c
                for c in await courses()
                if course.lower() in c.get("course", "").lower()
            )
        )
    if not course:
        raise ValueError("No course found")
    async with course_lock:
        await load_course(course)
        yield


async def call_api(action: str, data: dict[str, any]) -> dict:
    s = await session()
    url = (
        (await vue_base_url()) / "api" / "GB" / "ClientSideData" / "Transfer"
    ).with_query(action=action)
    headers = {
        "CURRENT_WEB_PORTAL": "StudentVUE",
        "X-Requested-With": "XMLHttpRequest",
    }
    async with s.post(url, json=data, headers=headers) as r:
        if not r.ok:
            name = data.get("FriendlyName", "Unknown")
            raise SpiderIOException(f'Failed to call "{name}"', r)
        return await r.json()


async def get_class_data():
    return await call_api(
        "genericdata.classdata-GetClassData",
        {
            "FriendlyName": "genericdata.classdata",
            "Method": "GetClassData",
            "Parameters": "{}",
        },
    )


async def get_items(
    sort: str = "due_date",
    group_by: Literal["Week", "Subject", "AssignmentType", "Unit", "Date"] = "Week",
):
    return await call_api(
        "pxp.course.content.items-LoadWithOption",
        {
            "FriendlyName": "pxp.course.content.items",
            "Method": "LoadWithOptions",
            "Parameters": json.dumps(
                {
                    "loadOptions": {
                        "sort": [{"selector": sort, "desc": False}],
                        "filter": [["isDone", "=", False]],
                        "group": [{"Selector": group_by, "desc": False}],
                        "requireTotalCount": True,
                        "userData": {},
                    },
                    "clientState": {},
                }
            ),
        },
    )


async def fetch(username: str, password: str):
    await login(username, password)

    async def fetch_course(c) -> tuple[dict, dict]:
        async with course(c):
            return await asyncio.gather(get_class_data(), get_items())

    return await asyncio.gather(*(fetch_course(c) for c in await courses()))

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, Literal

import aiohttp
from lxml.etree import HTML
from yarl import URL

from .constants import DASHBOARD_URL
from .exception import SpiderIOException
from .utils import cached, chunked, find, first, get_var, identifier, submit

multicached = cached(128)


def resolve_url(url: str | URL, base_url: URL) -> URL:
    return (
        URL(url)
        if URL(url).is_absolute()
        else URL(base_url / url)
        if isinstance(url, str)
        else base_url.join(url)
    )


@multicached
async def apps(s: aiohttp.ClientSession) -> list[tuple[str, URL]]:
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


@multicached
async def vue_url(s: aiohttp.ClientSession) -> URL:
    return find(await apps(s), "my_student_vue")


async def vue(s: aiohttp.ClientSession):
    async with s.get(await vue_url(s)) as r:
        text = await r.text()
    async with submit(s, text) as r:
        return r.url.parent, await r.text()


@multicached
async def vue_base_url(s: aiohttp.ClientSession):
    VUE_BASE_URL, _ = await vue(s)
    return VUE_BASE_URL


async def vue_script(s: aiohttp.ClientSession):
    _, html_raw = await vue(s)
    html = HTML(html_raw.encode("utf-8"))
    script = html.xpath("//head/script[1]/text()")[0]
    return script


@multicached
async def grade_book_url(s: aiohttp.ClientSession):
    return find(await navigations(s), "grade_book")


@multicached
async def navigations(s: aiohttp.ClientSession):
    return [
        (
            identifier(nav.get("description")),
            resolve_url(URL(nav.get("url")), await vue_base_url(s)),
        )
        for nav in get_var("PXP.NavigationData", await vue_script(s))["items"]
    ]


@multicached
async def grade_book(s: aiohttp.ClientSession):
    async with s.get(await grade_book_url(s)) as r:
        text = await r.text()
        return HTML(text.encode("utf-8"))


@multicached
async def courses(s: aiohttp.ClientSession):
    html = await grade_book(s)
    rows = chunked(
        html.xpath(
            '//div[@id="gradebook-content"]'
            '//div[contains(@class, "header")]'
            '/following-sibling::div[div[contains(@class, "row")]]'
            "/div"
        ),
        2,
    )
    result = [
        dict(
            course=first(header.xpath("div[1]/button/text()")),
            teacher=first(
                header.xpath('.//span[contains(@class, "teacher")]//a/text()')
            ),
            grade=first(content.xpath('.//span[contains(@class, "mark")]/text()')),
            params=(params := json.loads(first(header.xpath(".//button/@data-focus")))),
            id=params["FocusArgs"]["classID"],
        )
        for header, content in rows
    ]
    return result


async def load_control(
    s: aiohttp.ClientSession,
    control_name: str,
    params: dict[str, Any],
) -> dict:
    url = (await vue_base_url(s)) / "service" / "PXP2Communication.asmx" / "LoadControl"
    data = dict(request=dict(control=control_name, parameters=params))
    async with s.post(
        url,
        json=data,
        headers={"X-Requested-With": "XMLHttpRequest"},
    ) as r:
        if not r.ok:
            raise SpiderIOException(f'Failed to load "{control_name}"', r)
        return await r.json()


async def load_course(s: aiohttp.ClientSession, course):
    await load_control(
        s,
        course["params"]["LoadParams"]["ControlName"],
        course["params"]["FocusArgs"],
    )


course_lock = asyncio.Lock()


@asynccontextmanager
async def course(s: aiohttp.ClientSession, course: dict[str, any] | int | str):
    course = await resolve_course(s, course)
    if not course:
        raise ValueError("No course found")
    async with course_lock:
        await load_course(s, course)
        yield


async def resolve_course(
    s: aiohttp.ClientSession,
    course: dict[str, any] | int | str,
    type: Literal["auto", "index", "id", "name"] = "auto",
):
    if isinstance(course, dict):
        return course
    match type:
        case "auto":
            if isinstance(course, int):
                course = (await courses(s))[course]
            elif isinstance(course, str):
                course = first(
                    (c for c in await courses() if course == str(c.get("id")))
                ) or first(
                    (
                        c
                        for c in await courses(s)
                        if course.lower() in c.get("course", "").lower()
                    )
                )
        case "index":
            course = (await courses(s))[course]
        case "id":
            course = first((c for c in await courses(s) if course == c.get("id")))
        case "name":
            course = first(
                (
                    c
                    for c in await courses(s)
                    if course.lower() in c.get("course").lower()
                )
            )
        case _:
            raise ValueError(f"Unknown type {type}")
    if not course:
        raise ValueError("No course found")
    return course


async def call_api(s: aiohttp.ClientSession, action: str, data: dict[str, Any]) -> dict:
    url = (
        (await vue_base_url(s)) / "api" / "GB" / "ClientSideData" / "Transfer"
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


async def get_class_data(s: aiohttp.ClientSession):
    return await call_api(
        s,
        "genericdata.classdata-GetClassData",
        {
            "FriendlyName": "genericdata.classdata",
            "Method": "GetClassData",
            "Parameters": "{}",
        },
    )


async def get_items(
    s: aiohttp.ClientSession,
    sort: str = "due_date",
    group_by: Literal["Week", "Subject", "AssignmentType", "Unit", "Date"] = "Week",
):
    return await call_api(
        s,
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


async def get_course_data(s: aiohttp.ClientSession, c) -> tuple[dict, dict]:
    async with course(s, c):
        return await asyncio.gather(get_class_data(s), get_items(s))


@multicached
async def get_courses_data(s: aiohttp.ClientSession):
    return await asyncio.gather(*(get_course_data(s, c) for c in await courses(s)))

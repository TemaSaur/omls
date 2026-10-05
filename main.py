import random
import sqlite3
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, HttpUrl

import storage

app = FastAPI()

with storage.get_db_session() as con:
	storage.init_db(con)


def add_scheme(link: str) -> str:
	if link.startswith(("https://", "http://")):
		return link
	return f"https://{link}"


def normalize_url(link: str) -> str:
	host = HttpUrl(link).host or ""
	if "." not in host:
		raise ValueError("URL must include a domain with a TLD")
	return str(HttpUrl(link))


HttpStr = Annotated[str, BeforeValidator(add_scheme), AfterValidator(normalize_url)]


class ShortenModel(BaseModel):
	link: HttpStr = Field(title="link", max_length=1024, min_length=3)


class ShortenResponse(BaseModel):
	status: str
	new_link: str = Field(title="newLink")


@app.get("/")
def index() -> dict[str, str]:
	return {"status": "ok"}


@app.post("/shorten")
def shorten(
	body: ShortenModel, req: Request, con: sqlite3.Connection = Depends(storage.get_db)
) -> ShortenResponse:
	short = get_random_word()

	url = body.link

	target = HttpUrl(url)
	if target.host == req.url.hostname and target.port == req.base_url.port:
		raise HTTPException(400, "Can't use shortener urls")

	storage.create_link(con, storage.Link(short=short, long=url))

	return ShortenResponse(status="ok", new_link=short)


@app.get("/{link}")
def longen(
	link: str, con: sqlite3.Connection = Depends(storage.get_db)
) -> RedirectResponse:
	res = storage.get_link(con, link)
	if res is None:
		raise HTTPException(404, "link not found")
	storage.increment_link(con, link)
	return RedirectResponse(res.long, status_code=302)


@app.get("/status/{link}")
def get_status(
	link: str, con: sqlite3.Connection = Depends(storage.get_db)
) -> storage.Link:
	res = storage.get_link(con, link)
	if res is None:
		raise HTTPException(404, "link not found")
	return res


def get_random_word(length: int = 4) -> str:
	alphabet = "qwertyuiopasdfghjklzxcvbnm"
	alphabet += alphabet.upper()
	return "".join([random.choice(alphabet) for _ in range(length)])

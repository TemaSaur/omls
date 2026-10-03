import random
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, HttpUrl

app = FastAPI()


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


class Link(BaseModel):
	short: str
	long: HttpStr
	count: int = 0


@app.get("/")
def index() -> dict[str, str]:
	return {"status": "ok"}


links: dict[str, Link] = {}


@app.post("/shorten")
def shorten(body: ShortenModel, req: Request) -> ShortenResponse:
	short = get_random_word()

	url = body.link

	target = HttpUrl(url)
	if target.host == req.url.hostname and target.port == req.base_url.port:
		raise HTTPException(400, "Can't use shortener urls")

	links[short] = Link(short=short, long=url)

	return ShortenResponse(status="ok", new_link=short)


@app.get("/{link}")
def longen(link: str) -> RedirectResponse:
	if link not in links:
		raise HTTPException(404, "link not found")
	obj = links[link]
	obj.count += 1
	return RedirectResponse(obj.long, status_code=302)


@app.get("/status/{link}")
def get_status(link: str) -> Link:
	if link not in links:
		raise HTTPException(404, "link not found")
	obj = links[link]
	return obj


def get_random_word(length: int = 4) -> str:
	alphabet = "qwertyuiopasdfghjklzxcvbnm"
	alphabet += alphabet.upper()
	return "".join([random.choice(alphabet) for _ in range(length)])

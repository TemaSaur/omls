import random

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

app = FastAPI()


class ShortenModel(BaseModel):
	link: str = Field(title="link", max_length=1024, min_length=3)


class ShortenResponse(BaseModel):
	status: str
	new_link: str = Field(title="newLink")


class Link(BaseModel):
	short: str
	long: str
	count: int

	def __init__(self, short: str, long: str):
		super().__init__(short=short, long=long, count=0)


@app.get("/")
def index() -> dict[str, str]:
	return {"status": "ok"}


links: dict[str, Link] = {}


@app.post("/shorten")
def shorten(req: ShortenModel) -> ShortenResponse:
	short = get_random_word()

	if not req.link.startswith("https:"):
		url = f"https://{req.link}"
	else:
		url = req.link

	links[short] = Link(short, url)

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

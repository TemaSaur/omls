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


@app.get("/")
def index() -> dict[str, str]:
	return {"status": "ok"}


links: dict[str, str] = {}


@app.post("/shorten")
def shorten(req: ShortenModel) -> ShortenResponse:
	if req.link in links:
		return ShortenResponse(status="ok", new_link=links[req.link])

	link = get_random_word()

	if not req.link.startswith("https:"):
		url = f"https://{req.link}"
	else:
		url = req.link
	links[link] = url

	return ShortenResponse(status="ok", new_link=link)


@app.get("/{link}")
def longen(link: str) -> RedirectResponse:
	if link not in links:
		raise HTTPException(404, "link not found")
	return RedirectResponse(links[link], status_code=302)


def get_random_word(length: int = 4) -> str:
	alphabet = "qwertyuiopasdfghjklzxcvbnm"
	alphabet += alphabet.upper()
	return "".join([random.choice(alphabet) for _ in range(length)])

import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()


class ShortenModel(BaseModel):
	link: str = Field(title="link", max_length=1024, min_length=3)


class ShortenResponse(BaseModel):
	status: str
	new_link: str = Field(title="newLink")


class LongenResponse(BaseModel):
	status: str
	link: str


@app.get("/")
def index() -> dict[str, str]:
	return {"status": "ok"}


links: dict[str, str] = {}


@app.post("/shorten")
def shorten(req: ShortenModel) -> ShortenResponse:
	if req.link in links:
		return ShortenResponse(status="ok", new_link=links[req.link])

	link = get_random_word()
	links[link] = req.link
	return ShortenResponse(status="ok", new_link=link)


@app.get("/{link}")
def longen(link: str) -> LongenResponse:
	print(links)
	if link in links:
		return LongenResponse(status="ok", link=links[link])
	raise HTTPException(404, LongenResponse(status="not found", link=""))


def get_random_word(length: int = 5) -> str:
	alphabet = "qwertyuiopasdfghjklzxcvbnm"
	return "".join([random.choice(alphabet) for _ in range(length)])

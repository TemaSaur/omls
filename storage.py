import sqlite3
from contextlib import contextmanager
from typing import Any

from pydantic import BaseModel


class Link(BaseModel):
	short: str
	long: str
	count: int = 0


def dict_factory(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> dict[str, Any]:
	fields = [column[0] for column in cursor.description]
	return {key: value for key, value in zip(fields, row)}


def get_db():
	con = sqlite3.connect("database.db")
	con.row_factory = dict_factory
	try:
		yield con
	finally:
		con.close()


@contextmanager
def get_db_session():
	con = sqlite3.connect("database.db")
	con.row_factory = dict_factory
	try:
		yield con
	finally:
		con.close()


def init_db(con: sqlite3.Connection) -> None:
	with con:
		_ = con.execute("""
		CREATE TABLE IF NOT EXISTS links (
			short TEXT PRIMARY KEY,
			long TEXT NOT NULL,
			count INTEGER NOT NULL DEFAULT 0
		);""")


def create_link(con: sqlite3.Connection, link: Link) -> None:
	with con:
		_ = con.execute(
			"""
		INSERT INTO links (
			short
			, long
		) VALUES (
			?
			, ?
		);""",
			(
				link.short,
				link.long,
			),
		)


def get_link(con: sqlite3.Connection, short: str):
	with con:
		res = con.execute(
			"""
		SELECT
			short
			, long
			, count
		FROM links
		WHERE
			short = ?
		LIMIT 1
		;""",
			(short,),
		)
		row = res.fetchone()
		return Link(**row) if row else None


def increment_link(con: sqlite3.Connection, short: str):
	with con:
		_ = con.execute(
			"""
		UPDATE links
		SET count = count + 1
		WHERE
			short = ?
		;""",
			(short,),
		)

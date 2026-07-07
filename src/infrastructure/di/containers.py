"""FastAPI dependency_overrides wiring."""

from fastapi import FastAPI


def setup_di(app: FastAPI) -> None: ...

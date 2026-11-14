"""Regression checks for the supported backend launch entry points."""

from fastapi import FastAPI


def test_run_server_exports_the_primary_fastapi_application():
    import Main
    import run_server

    assert isinstance(run_server.app, FastAPI)
    assert run_server.app is Main.app

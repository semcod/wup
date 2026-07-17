"""Tests for the pluggable endpoint-discovery adapters."""

from __future__ import annotations

from pathlib import Path

import pytest

from wup.dependency_mapper import DependencyMapper
from wup.discovery import SourceIndex, detect_frameworks, discover_endpoints

# (framework, filename, source) fixtures — one per adapter.
FIXTURES = {
    "fastapi": (
        "api.py",
        "from fastapi import APIRouter\nrouter = APIRouter()\n"
        '@router.get("/users")\ndef u(): ...\n@router.post("/users")\ndef c(): ...\n',
        {"/users"},
    ),
    "flask": (
        "views.py",
        "from flask import Blueprint\nbp = Blueprint('a', __name__)\n"
        '@bp.route("/login")\ndef login(): ...\n',
        {"/login"},
    ),
    "django": (
        "urls.py",
        'from django.urls import path\nurlpatterns = [path("admin/", v), path("home/", v)]\n',
        {"admin/", "home/"},
    ),
    "nestjs": (
        "users.controller.ts",
        "import { Controller, Get } from '@nestjs/common';\n"
        "@Controller('users')\nclass C { @Get('/list') l(){} @Post('/create') c(){} }\n",
        {"/list", "/create"},
    ),
    "express": (
        "routes.js",
        "const express = require('express')\nconst router = express.Router()\n"
        "router.get('/api/users', h)\nrouter.post('/api/users', h)\n",
        {"/api/users"},
    ),
    "fastify": (
        "server.ts",
        "import Fastify from 'fastify'\nconst f = Fastify()\n"
        "f.get('/health', h)\nf.post('/items', h)\n",
        {"/health", "/items"},
    ),
    "hono": (
        "app.ts",
        "import { Hono } from 'hono'\nconst app = new Hono()\n"
        "app.get('/ping', c)\napp.delete('/items/:id', c)\n",
        {"/ping", "/items/:id"},
    ),
    "go": (
        "main.go",
        'package main\nimport "github.com/gin-gonic/gin"\n'
        'func main(){ r := gin.Default(); r.GET("/ping", h); r.POST("/users", h) }\n',
        {"/ping", "/users"},
    ),
    "openapi": (
        "openapi.yaml",
        "openapi: 3.0.0\npaths:\n  /pets:\n    get: {}\n    post: {}\n  /pets/{id}:\n    delete: {}\n",
        {"/pets", "/pets/{id}"},
    ),
}


def _write(tmp_path: Path, filename: str, source: str) -> Path:
    svc = tmp_path / "services" / "svc"
    svc.mkdir(parents=True)
    (svc / filename).write_text(source)
    return tmp_path


@pytest.mark.parametrize("framework", list(FIXTURES))
def test_adapter_detects_and_discovers(tmp_path: Path, framework: str) -> None:
    filename, source, expected_paths = FIXTURES[framework]
    root = _write(tmp_path, filename, source)

    assert framework in detect_frameworks(SourceIndex(root))

    paths = {ep.path for ep in discover_endpoints(root, framework)}
    assert expected_paths <= paths


@pytest.mark.parametrize("framework", list(FIXTURES))
def test_mapper_builds_nonempty_deps(tmp_path: Path, framework: str) -> None:
    filename, source, expected_paths = FIXTURES[framework]
    root = _write(tmp_path, filename, source)

    result = DependencyMapper(str(root)).build_from_codebase()
    all_endpoints = {ep for svc in result["services"].values() for ep in svc["endpoints"]}
    assert expected_paths <= all_endpoints


def test_auto_mode_prefers_specific_framework(tmp_path: Path) -> None:
    """A Hono app using app.get() attributes to hono, not express."""
    root = _write(tmp_path, "app.ts", "import { Hono } from 'hono'\nconst app = new Hono()\napp.get('/x', c)\n")
    assert DependencyMapper(str(root))._detect_framework() == "hono"


def test_no_endpoints_for_plain_project(tmp_path: Path) -> None:
    (tmp_path / "readme.md").write_text("# hello")
    result = DependencyMapper(str(tmp_path)).build_from_codebase()
    assert result == {"services": {}, "files": {}}


def test_endpoints_deduplicated(tmp_path: Path) -> None:
    """The same path via GET and POST collapses to a single endpoint entry."""
    root = _write(
        tmp_path, "api.py",
        "from fastapi import APIRouter\nrouter = APIRouter()\n"
        '@router.get("/x")\ndef a(): ...\n@router.post("/x")\ndef b(): ...\n',
    )
    result = DependencyMapper(str(root)).build_from_codebase()
    eps = result["services"]["services/svc"]["endpoints"]
    assert eps.count("/x") == 1

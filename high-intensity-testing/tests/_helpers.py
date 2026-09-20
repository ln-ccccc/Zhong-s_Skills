# -*- coding: utf-8 -*-
"""preflight 测试公共工具:加载连字符文件名的脚本 + 构造最小 git 仓库"""
import importlib.util
import os
import subprocess
import tempfile


def load_preflight():
    path = os.path.join(os.path.dirname(__file__), "..", "scripts", "review-preflight.py")
    spec = importlib.util.spec_from_file_location("review_preflight", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_repo():
    """main: a.txt 已提交;feature 分支多一个 b.txt 提交;工作区干净"""
    tmp = tempfile.mkdtemp(prefix="preflight-test-")
    git(tmp, "init", "-b", "main")
    git(tmp, "config", "user.email", "t@example.com")
    git(tmp, "config", "user.name", "t")
    write(os.path.join(tmp, "a.txt"), "a\n")
    git(tmp, "add", ".")
    git(tmp, "commit", "-m", "a")
    git(tmp, "checkout", "-b", "feature")
    write(os.path.join(tmp, "b.txt"), "b\n")
    git(tmp, "add", ".")
    git(tmp, "commit", "-m", "b")
    return tmp

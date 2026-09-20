#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审查预检:OCR(open-code-review)可用则委托,不可用则降级 git/仓库规则文件。

用法:
  python review-preflight.py [repo_dir]        # 默认当前目录
  python review-preflight.py --from main --to fix/branch   # 传给 ocr review 的区间

输出 JSON:
  mode          "ocr-delegate" | "git-fallback"
  files         待审查文件清单(变更面)
  rule_files    找到的仓库规则文件(任务书的规则源)
  recent_commits 最近提交摘要(上下文)
  ocr_output    OCR 委托模式的原始输出(成功时)
  notes         降级原因等提示

纯标准库,无第三方依赖;只读操作,不改任何文件。
"""
import json
import os
import shutil
import subprocess
import sys

RULE_FILES = [
    "AGENTS.md", "CLAUDE.md", ".cursorrules", "CONTRIBUTING.md",
    "docs/testing_playbook.md", "README.md",
]


def run(cmd, cwd, timeout=120):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except Exception as e:  # 超时/编码/环境异常一律按失败处理
        return 1, "", str(e)


def find_rule_files(repo):
    return [f for f in RULE_FILES if os.path.exists(os.path.join(repo, f))]


def ocr_mode(repo, extra_args):
    notes = []
    if extra_args:
        cmd = ["ocr", "review", *extra_args, "--format", "json"]
    else:
        cmd = ["ocr", "delegate", "preview"]
    code, out, err = run(cmd, repo, timeout=300)
    if code != 0:
        return None, [f"ocr 退出码 {code}: {err.strip()[-200:]}"]
    try:
        json.loads(out)
        return {"ocr_output": json.loads(out)}, notes
    except json.JSONDecodeError:
        return {"ocr_output_raw": out[-4000:]}, notes


def fallback_mode(repo):
    notes = ["ocr 不可用,降级 git-fallback:文件面来自 git,规则源来自仓库规则文件"]
    files, commits = [], []
    code, out, err = run(["git", "rev-parse", "--is-inside-work-tree"], repo)
    if out.strip() != "true":
        return {"files": [], "recent_commits": [],
                "notes": notes + [f"不是 git 工作区: {err.strip()[-120:] or out.strip()}"]}
    _, out, _ = run(["git", "status", "--porcelain"], repo)
    status_lines = [l for l in out.splitlines() if l.strip()]
    _, out, _ = run(["git", "diff", "--name-only", "HEAD"], repo)
    files = [l for l in out.splitlines() if l.strip()]
    _, out, _ = run(["git", "diff", "--name-only", "--cached"], repo)
    files += [l for l in out.splitlines() if l.strip() and l not in files]
    _, out, _ = run(["git", "log", "--oneline", "-10"], repo)
    commits = [l for l in out.splitlines() if l.strip()]
    return {"files": files, "recent_commits": commits,
            "notes": notes + [f"工作区有 {len(status_lines)} 处未提交变更(构建/产物类需排除)"]}


def preflight(repo, extra_args=None):
    repo = os.path.abspath(repo)
    result = {"repo": repo, "rule_files": find_rule_files(repo)}
    if shutil.which("ocr"):
        ocr, notes = ocr_mode(repo, extra_args or [])
        if ocr is not None:
            result.update({"mode": "ocr-delegate", "files": [], "recent_commits": [],
                           "notes": notes, **ocr})
            return result
        result["notes"] = notes
    result.update(fallback_mode(repo))
    result.setdefault("mode", "git-fallback")
    return result


def main():
    args = [a for a in sys.argv[1:]]
    repo = args[0] if args and os.path.exists(args[0]) else "."
    extra = []
    if "--from" in args:
        i = args.index("--from")
        extra = args[i:i + 4]
    print(json.dumps(preflight(repo, extra), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

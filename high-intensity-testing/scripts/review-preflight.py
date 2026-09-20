#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""审查预检:OCR(open-code-review)可用则委托,不可用则降级 git/仓库规则文件。

架构分工:OCR 委托模式只做确定性文件/规则选择(deterministic file/rule selection),
评审推理由宿主 agent 执行——因此统一走 `ocr delegate preview`,不调 `ocr review`
(后者跑 OCR 自己的 LLM 管线,不是委托)。

用法:
  python review-preflight.py [repo_dir]                    # 工作区模式
  python review-preflight.py --from main --to fix/branch   # 区间模式(merge-base 语义)

输出 JSON:
  mode           "ocr-delegate" | "git-fallback"
  files          待审查文件清单
  rule_files     找到的仓库规则文件(任务书的规则源)
  recent_commits 提交摘要(上下文)
  ocr_output     OCR 委托模式的原始输出(成功时)
  notes          模式与降级原因

文件面语义与 OCR workspace review 对齐:staged ∪ unstaged ∪ untracked;
区间模式:merge-base(from,to)..to 的变更。纯标准库,只读,不改任何文件。
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


def git_out(repo, *args):
    code, out, _ = run(["git", *args], repo)
    return out if code == 0 else ""


def ocr_mode(repo, from_ref=None, to_ref=None):
    """委托模式预览;失败返回 (None, notes) 由调用方降级。"""
    cmd = ["ocr", "delegate", "preview", "--format", "json"]
    if from_ref and to_ref:
        cmd += ["--from", from_ref, "--to", to_ref]
    code, out, err = run(cmd, repo, timeout=300)
    if code != 0:
        return None, [f"ocr 退出码 {code}: {err.strip()[-200:]}"]
    try:
        return {"ocr_output": json.loads(out)}, []
    except json.JSONDecodeError:
        return {"ocr_output_raw": out[-4000:]}, []


def fallback_mode(repo, from_ref=None, to_ref=None):
    notes = ["ocr 不可用,降级 git-fallback:文件面来自 git,规则源来自仓库规则文件"]
    if git_out(repo, "rev-parse", "--is-inside-work-tree").strip() != "true":
        return {"files": [], "recent_commits": [],
                "notes": notes + ["不是 git 工作区"]}

    # 区间模式:与 ocr review --from/--to 同语义,按 merge-base 取 range
    if from_ref and to_ref:
        base = git_out(repo, "merge-base", from_ref, to_ref).strip()
        if base:
            files = [l for l in git_out(repo, "diff", "--name-only", f"{base}..{to_ref}").splitlines() if l.strip()]
            commits = [l for l in git_out(repo, "log", "--oneline", f"{base}..{to_ref}").splitlines() if l.strip()]
            return {"files": files, "recent_commits": commits,
                    "notes": notes + [f"区间模式 merge-base({from_ref},{to_ref})={base[:12]}..{to_ref}"]}
        notes.append(f"merge-base({from_ref},{to_ref}) 失败,回退工作区模式")

    # 工作区模式:staged ∪ unstaged ∪ untracked
    files = []
    for args in (["diff", "--name-only", "HEAD"],
                 ["diff", "--name-only", "--cached"],
                 ["ls-files", "--others", "--exclude-standard"]):
        for line in git_out(repo, *args).splitlines():
            if line.strip() and line not in files:
                files.append(line)
    commits = [l for l in git_out(repo, "log", "--oneline", "-10").splitlines() if l.strip()]
    return {"files": files, "recent_commits": commits, "notes": notes}


def preflight(repo, from_ref=None, to_ref=None):
    repo = os.path.abspath(repo)
    result = {"repo": repo, "rule_files": find_rule_files(repo), "notes": []}
    if shutil.which("ocr"):
        ocr, notes = ocr_mode(repo, from_ref, to_ref)
        if ocr is not None:
            result.update({"mode": "ocr-delegate", "files": [], "recent_commits": [],
                           **ocr})
            return result
        result["notes"].extend(notes)  # OCR 存在但执行失败 → 记录原因后同样降级
    fb = fallback_mode(repo, from_ref, to_ref)
    result["notes"].extend(fb.pop("notes", []))
    result.update(fb)
    result.setdefault("mode", "git-fallback")
    return result


def main():
    args = sys.argv[1:]
    from_ref = to_ref = None
    rest = []
    i = 0
    while i < len(args):
        if args[i] == "--from" and i + 1 < len(args):
            from_ref = args[i + 1]
            i += 2
        elif args[i] == "--to" and i + 1 < len(args):
            to_ref = args[i + 1]
            i += 2
        else:
            rest.append(args[i])
            i += 1
    repo = rest[0] if rest else "."
    print(json.dumps(preflight(repo, from_ref, to_ref), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

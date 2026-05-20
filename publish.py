"""
TubeUp 블로그 자동발행 봇
사용법:
  python publish.py --title "글 제목" --file draft.md --tags "유튜브,쇼츠"
  python publish.py --title "글 제목" --content "본문 내용" --tags "유튜브"
  echo "본문" | python publish.py --title "글 제목"

옵션:
  --slug "custom-url"   URL 직접 지정 (영문 권장)
  --description "..."   메타 description (SEO용)
  --draft               임시저장 (블로그에 노출 안 됨)
  --no-publish          git push 안 함 (로컬에만)
  --no-build            hugo 빌드 안 함 (.md만 저장)
"""
import sys
import re
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

BLOG_DIR = Path(__file__).parent
HUGO_EXE = Path(
    r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages"
    r"\Hugo.Hugo.Extended_Microsoft.Winget.Source_8wekyb3d8bbwe\hugo.exe"
)
KST = timezone(timedelta(hours=9))


def make_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s가-힣-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    if not text or not re.search(r"[a-z0-9]", text):
        text = datetime.now(KST).strftime("post-%Y%m%d-%H%M%S")
    return text[:80]


def write_post(title, content, slug=None, tags=None, description="", draft=False):
    slug = slug or make_slug(title)
    post_path = BLOG_DIR / "content" / "posts" / f"{slug}.md"
    post_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S%z")
    now = now[:-2] + ":" + now[-2:]  # +0900 -> +09:00
    tags = tags or []
    tags_yaml = "[" + ", ".join(f'"{t}"' for t in tags) + "]"
    desc_escaped = description.replace('"', '\\"')
    title_escaped = title.replace('"', '\\"')

    front_matter = (
        "---\n"
        f'title: "{title_escaped}"\n'
        f"date: {now}\n"
        f"draft: {str(draft).lower()}\n"
        f"tags: {tags_yaml}\n"
        f'description: "{desc_escaped}"\n'
        "---\n\n"
        f"{content.strip()}\n"
    )
    post_path.write_text(front_matter, encoding="utf-8")
    return post_path, slug


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=BLOG_DIR, check=True, **kw)


def build_site():
    run([str(HUGO_EXE), "--minify", "--gc"])
    # 네이버 호환: sitemap.xml/ 와 index.xml/ 도 대응
    import shutil
    docs = BLOG_DIR / "docs"
    (docs / "CNAME").write_text("blog.tubeup.kr\n", encoding="utf-8")
    (docs / "sitemap").mkdir(exist_ok=True)
    shutil.copyfile(docs / "sitemap.xml", docs / "sitemap" / "index.xml")
    (docs / "rss").mkdir(exist_ok=True)
    shutil.copyfile(docs / "index.xml", docs / "rss" / "index.xml")


def git_publish(message):
    run(["git", "add", "-A"])
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=BLOG_DIR
    )
    if result.returncode == 0:
        print("[SKIP] no changes to commit")
        return
    run(["git", "commit", "-m", message])
    run(["git", "push"])


def main():
    p = argparse.ArgumentParser(description="TubeUp 블로그 자동발행")
    p.add_argument("--title", required=True)
    p.add_argument("--content", help="본문 (직접 입력)")
    p.add_argument("--file", help="본문 마크다운 파일 경로")
    p.add_argument("--slug", help="URL slug (영문 권장, 미지정시 자동)")
    p.add_argument("--tags", default="", help="태그 쉼표 구분")
    p.add_argument("--description", default="", help="SEO 설명")
    p.add_argument("--draft", action="store_true")
    p.add_argument("--no-build", action="store_true")
    p.add_argument("--no-publish", action="store_true")
    args = p.parse_args()

    if args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.content:
        content = args.content
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        p.error("본문 필요: --content 또는 --file 또는 stdin")

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]

    post_path, slug = write_post(
        title=args.title,
        content=content,
        slug=args.slug,
        tags=tags,
        description=args.description or args.title,
        draft=args.draft,
    )
    print(f"[OK] saved: {post_path.relative_to(BLOG_DIR)}")

    if args.no_build:
        return

    build_site()
    print("[OK] hugo build done")

    if args.no_publish or args.draft:
        print("[SKIP] no publish (draft or --no-publish)")
        return

    git_publish(f"post: {args.title}")
    print(f"[LIVE] https://blog.tubeup.kr/posts/{slug}/")


if __name__ == "__main__":
    main()

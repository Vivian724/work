#!/usr/bin/env python3
"""
把两份原型（后台、前台）的内嵌副本塞进规格书对照版。

为什么需要这支脚本？
  daily_spec.html 左栏预设「即时载入」同资料夹的 daily_admin.html，
  所以原型改版后对照版会自动跟著更新，平常不必执行这支脚本。

  只有一种情况需要跑：把 daily_spec.html 单独寄给别人时。
  收到的人身边没有 daily_admin.html / daily_front.html，即时载入会失败，
  这时才会改用文件底部两个 <script type="text/plain"> 区块里的内嵌副本
  （后台放在 id="proto-src"，前台放在 id="proto-src-front"）。

用法：
  python3 merge_spec.py

原理：
  HTML 里不能直接放 </script>，会把外层的 script 提前关掉。
  所以存进去之前把所有 </script 换成 @@ENDSCRIPT@@，
  对照版的程式读出来时再换回去。
"""

import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = HERE / "daily_spec.html"

# 要嵌进去的两份原型：(档案, 区块起标记, 区块讫标记, 塞进去之后的 id)
# ⚠ 刻意用 HTML 注解当区块标记，而不是直接找 <script ... id="proto-src">——
#    因为档头的说明注解里也会提到那个标签，用标签当标记会比对到注解，
#    结果把整份版面覆盖掉（2026-09-14 踩过这个坑）。
TARGETS = [
    (HERE / "daily_admin.html", "<!-- PROTO_EMBED_BEGIN -->", "<!-- PROTO_EMBED_END -->", "proto-src"),
    (HERE / "daily_front.html", "<!-- PROTO_EMBED_FRONT_BEGIN -->", "<!-- PROTO_EMBED_FRONT_END -->", "proto-src-front"),
]

def main() -> int:
    if not SPEC.exists():
        print(f"✗ 找不到 {SPEC.name}")
        return 1

    spec_html = SPEC.read_text(encoding="utf-8")
    stamp = date.today().isoformat()

    for proto, mark_begin, mark_end, holder_id in TARGETS:
        if not proto.exists():
            print(f"✗ 找不到 {proto.name}")
            return 1

        proto_html = proto.read_text(encoding="utf-8")

        # 原型尾端必须有桥接程序，否则对照版不会连动
        # （2026-09-15 起用词统一为简体惯用语，「程式」改成「程序」，这里跟著改）
        if "桥接程序" not in proto_html and "桥接程式" not in proto_html:
            print(f"✗ {proto.name} 里找不到桥接程序，对照版将无法连动。")
            print("  请确认原型尾端那段 <script> 还在（注解标记「桥接程序」）。")
            return 1

        # 把 </script 换成安全标记，才塞得进 <script type="text/plain">
        escaped = proto_html.replace("</script", "@@ENDSCRIPT@@")

        # 标记必须各自只出现一次，否则宁可停下来也不要乱改
        for mark in (mark_begin, mark_end):
            n = spec_html.count(mark)
            if n != 1:
                print(f"✗ daily_spec.html 里的 {mark} 出现 {n} 次，预期 1 次")
                return 1

        start = spec_html.find(mark_begin) + len(mark_begin)
        end = spec_html.find(mark_end)
        if end < start:
            print(f"✗ {mark_begin} 与 {mark_end} 的顺序颠倒")
            return 1

        spec_html = (
            spec_html[:start]
            + f"\n<!-- 内嵌副本 · {proto.name} · 存档于 {stamp} · 由 merge_spec.py 自动产生，请勿手改 -->\n"
            + f'<script type="text/plain" id="{holder_id}">'
            + escaped
            + "</script>\n"
            + spec_html[end:]
        )
        print(f"✓ 已把 {proto.name}（{len(escaped.encode('utf-8')) / 1024:.0f} KB）嵌进 daily_spec.html")

    # 顺手把工具列上「内嵌副本」的日期换成今天
    spec_html = re.sub(
        r"内嵌副本（存档于 [\d-]+）· 非即时|内嵌副本 · 非即时",
        f"内嵌副本（存档于 {stamp}）· 非即时",
        spec_html,
    )

    SPEC.write_text(spec_html, encoding="utf-8")
    print(f"  daily_spec.html 现在 {len(spec_html.encode('utf-8')) / 1024:.0f} KB，存档日期 {stamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

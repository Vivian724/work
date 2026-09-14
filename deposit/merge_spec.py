#!/usr/bin/env python3
"""
把后台原型的内嵌副本塞进规格书对照版。

为什么需要这支脚本？
  daily_spec.html 左栏预设「即时载入」同资料夹的 daily_admin.html，
  所以原型改版后对照版会自动跟著更新，平常不必执行这支脚本。

  只有一种情况需要跑：把 daily_spec.html 单独寄给别人时。
  收到的人身边没有 daily_admin.html，即时载入会失败，
  这时才会改用文件底部 <script type="text/plain" id="proto-src"> 里的内嵌副本。

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
PROTO = HERE / "daily_admin.html"
SPEC = HERE / "daily_spec.html"

# 内嵌副本区块的起讫标记
OPEN_TAG = '<script type="text/plain" id="proto-src">'
CLOSE_TAG = "</script>"


def main() -> int:
    for f in (PROTO, SPEC):
        if not f.exists():
            print(f"✗ 找不到 {f.name}")
            return 1

    proto_html = PROTO.read_text(encoding="utf-8")

    # 原型尾端必须有桥接程式，否则对照版不会连动
    if "桥接程式" not in proto_html:
        print("✗ daily_admin.html 里找不到桥接程式，对照版将无法连动。")
        print("  请确认原型尾端那段 <script> 还在（注解标记「桥接程式」）。")
        return 1

    # 把 </script 换成安全标记，才塞得进 <script type="text/plain">
    escaped = proto_html.replace("</script", "@@ENDSCRIPT@@")

    spec_html = SPEC.read_text(encoding="utf-8")

    start = spec_html.find(OPEN_TAG)
    if start == -1:
        print("✗ daily_spec.html 里找不到内嵌副本区块的开始标记")
        return 1
    body_start = start + len(OPEN_TAG)
    end = spec_html.find(CLOSE_TAG, body_start)
    if end == -1:
        print("✗ 内嵌副本区块没有结束标记")
        return 1

    stamp = date.today().isoformat()
    new_spec = (
        spec_html[:body_start]
        + f"<!-- 内嵌副本 · 存档于 {stamp} · 由 merge_spec.py 自动产生，请勿手改 -->\n"
        + escaped
        + spec_html[end:]
    )

    # 顺手把工具列上「内嵌副本」的日期换成今天
    new_spec = re.sub(
        r"内嵌副本（存档于 [\d-]+）· 非即时|内嵌副本 · 非即时",
        f"内嵌副本（存档于 {stamp}）· 非即时",
        new_spec,
    )

    SPEC.write_text(new_spec, encoding="utf-8")

    kb_proto = len(escaped.encode("utf-8")) / 1024
    kb_spec = len(new_spec.encode("utf-8")) / 1024
    print(f"✓ 已把 daily_admin.html（{kb_proto:.0f} KB）嵌进 daily_spec.html")
    print(f"  daily_spec.html 现在 {kb_spec:.0f} KB，存档日期 {stamp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

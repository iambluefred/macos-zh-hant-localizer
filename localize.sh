#!/bin/bash
# 幫有簡體中文的 Mac App 產生台灣繁體翻譯（zh-Hant.lproj），輸出到 output/<App 名稱>/。
# 不會修改 App 本身；產生後再自行把 zh-Hant.lproj 放進 App 的 Contents/Resources/。
#
# 用法：./localize.sh /Applications/某某.app
set -euo pipefail
cd "$(dirname "$0")"

APP="${1:?用法：./localize.sh /Applications/某某.app}"
RES="$APP/Contents/Resources"
SRC=""
for name in zh-Hans.lproj zh_CN.lproj zh-CN.lproj zh.lproj; do
  [ -d "$RES/$name" ] && SRC="$RES/$name" && break
done
[ -n "$SRC" ] || { echo "找不到簡體中文翻譯（zh-Hans / zh_CN）：$RES"; exit 1; }
[ -d "$RES/zh-Hant.lproj" ] && echo "注意：這個 App 已經有 zh-Hant.lproj，仍會在 output/ 產生一份新的。"

# 第一次執行時建立 Python 環境
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi

NAME="$(basename "$APP" .app)"
OUT="output/$NAME/zh-Hant.lproj"
rm -rf "$OUT"
.venv/bin/python convert_lproj.py "$SRC" "$OUT"

# 檢查每個 .strings 的格式，壞掉的話 App 會讀不到
bad=0
for f in "$OUT"/*.strings; do
  [ -e "$f" ] || continue
  plutil -lint -s "$f" >/dev/null 2>&1 || { echo "格式錯誤：$f"; bad=1; }
done
[ "$bad" -eq 0 ] || exit 1

echo
echo "完成：$(pwd)/$OUT"
echo "接著把 zh-Hant.lproj 拖進 $RES/（Finder 會要求確認），再重新開啟 App。"
echo "建議先備份 App；App 更新後需要重新放一次。"

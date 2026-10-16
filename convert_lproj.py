#!/usr/bin/env python3
"""把 App 的簡體中文翻譯（zh_CN.lproj / zh-Hans.lproj）轉成台灣繁體（zh-Hant.lproj）。

只轉「翻譯後的文字」，不動對照用的 key；.strings 保持原本的格式（UTF-16 或二進位 plist）。
用法：python3 convert_lproj.py <來源 .lproj> <輸出 .lproj>
"""
import os, plistlib, re, shutil, sys
from opencc import OpenCC

CC = OpenCC('s2twp')  # 簡體 → 台灣繁體，含常用詞彙轉換（文件→檔案、视频→影片…）

# OpenCC 轉錯或不符合台灣習慣的詞，轉完再修正
FIXES = {
    '影象': '影像',
    '圖象': '影像',
    '幺': '么',
    '釋出': '發布',      # 发布：照片「發布」到網站，不是軟體「釋出」
    '專案': '項目',      # 项目：介面上多半指清單裡的項目
    '選中': '選取',
    '跳轉': '前往',
    '關鍵詞': '關鍵字',
    '示例': '範例',
    '連線庫': '連接圖庫',
    '斷開庫': '中斷連接圖庫',
    '新建': '新增',
    '另存為': '另存新檔',
    '撤銷': '還原',
    '退出': '結束',
    '型別': '類型',    # 类型：OpenCC 會轉成程式用語「型別」
    '全屏': '全螢幕',
}

# 整段文字完全相同時才替換（例如選單標題）
EXACT = {
    '幫助': '說明',
    '幫助...': '說明...',
    '開啟元還原已完成': '後設資料還原完成',  # Lyn 原本的簡體是機器直譯（Open Meta Restore Done）
}

def convert(text: str) -> str:
    out = CC.convert(text)
    for wrong, right in FIXES.items():
        out = out.replace(wrong, right)
    return EXACT.get(out, out)

def read_strings(path):
    """讀 .strings：可能是二進位 plist，或 UTF-16／UTF-8 的文字格式"""
    raw = open(path, 'rb').read()
    if raw.startswith(b'bplist'):
        return plistlib.loads(raw), 'binary'
    # 依開頭的 BOM 判斷編碼；沒有 BOM 時先試 UTF-8（UTF-8 位元組常常也能被誤解成 UTF-16）
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw.decode('utf-16'), 'utf-16'
    if raw.startswith(b'\xef\xbb\xbf'):
        return raw.decode('utf-8-sig'), 'utf-8-sig'
    return raw.decode('utf-8'), 'utf-8'

STRING = r'"((?:[^"\\]|\\.)*)"'
PAIR = re.compile(STRING + r'(\s*=\s*)' + STRING + r'(\s*;)')

def convert_strings_file(src, dst):
    data, kind = read_strings(src)
    changed = 0
    if kind == 'binary':
        out = {k: convert(v) if isinstance(v, str) else v for k, v in data.items()}
        changed = sum(1 for k in data if out[k] != data[k])
        open(dst, 'wb').write(plistlib.dumps(out, fmt=plistlib.FMT_BINARY))
    else:
        def repl(m):
            nonlocal changed
            value = convert(m.group(3))
            if value != m.group(3):
                changed += 1
            return f'"{m.group(1)}"{m.group(2)}"{value}"{m.group(4)}'
        # 註解（/* … */）也一起轉，方便以後閱讀
        text = PAIR.sub(repl, data)
        text = re.sub(r'/\*.*?\*/', lambda m: convert(m.group(0)), text, flags=re.S)
        open(dst, 'w', encoding=kind).write(text)
    return changed

def main(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    total = 0
    for name in sorted(os.listdir(src_dir)):
        src, dst = os.path.join(src_dir, name), os.path.join(dst_dir, name)
        if name.endswith('.strings'):
            total += convert_strings_file(src, dst)
        elif name.endswith(('.html', '.htm', '.txt', '.rtf')):
            open(dst, 'w', encoding='utf-8').write(convert(open(src, encoding='utf-8', errors='replace').read()))
        elif os.path.isfile(src):
            shutil.copy2(src, dst)  # 圖片等其他資源照原樣複製
    print(f'{dst_dir}: converted {total} strings')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_terminal.py — воспроизводит оформление терминала на Windows:

  * Oh My Posh + тема bubblesextra (в одну строку, полный путь, яркие цвета Mocha)
  * шрифты JetBrains Mono Nerd Font и Meslo Nerd Font
  * Windows Terminal: схема «Mocha Vivid», тема «Modern», прозрачность,
    звёздное поле на фоне, курсор-черта, отступы, шрифт Medium
  * Windows PowerShell / PowerShell 7 / Developer PowerShell — через $PROFILE
  * Командная строка и Developer Command Prompt — через Clink
  * Ubuntu (WSL) — через ~/.bashrc

Запуск (в PowerShell или cmd, из папки репозитория):
    python setup_terminal.py

Тема берётся из themes/bubblesextra.omp.json, а если файла рядом нет —
из встроенной копии, так что скрипт работает и сам по себе.

Полезные ключи:
    --no-install   не ставить программы и шрифты (только настройки)
    --no-wsl       не трогать WSL / Ubuntu
    --no-stars     без звёздного поля на фоне
    --opacity N    непрозрачность фона в процентах (по умолчанию 90)

Перед изменением settings.json и профилей делаются резервные копии (*.backup-ДАТА).
После завершения полностью закройте Windows Terminal и откройте заново.
"""

import argparse
import ctypes
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ----------------------------------------------------------------------------
# Настройки внешнего вида
# ----------------------------------------------------------------------------

THEME_FILE_NAME = "bubblesextra.omp.json"
STARS_FILE_NAME = "starfield.png"

FONT_FACE = "JetBrainsMono Nerd Font, MesloLGM Nerd Font"
FONTS_TO_INSTALL = ["JetBrainsMono", "Meslo"]

WSL_ICON = "ms-appx:///ProfileIcons/{9acb9455-ca41-5af7-950f-6bca1bc9722f}.png"

COLOR_SCHEME = {
    "name": "Mocha Vivid",
    "background": "#1E1E2E",
    "foreground": "#F5F7FF",
    "cursorColor": "#FFFFFF",
    "selectionBackground": "#585B70",
    "black": "#45475A",
    "red": "#FF5B89",
    "green": "#7BEF72",
    "yellow": "#FFD985",
    "blue": "#609DFF",
    "purple": "#FD96E1",
    "cyan": "#62F0D8",
    "white": "#DDE3F5",
    "brightBlack": "#7F849C",
    "brightRed": "#FF7A9F",
    "brightGreen": "#95F28D",
    "brightYellow": "#FFE3A4",
    "brightBlue": "#7FB0FF",
    "brightPurple": "#FEB4EA",
    "brightCyan": "#7EF3DF",
    "brightWhite": "#FFFFFF",
}

WT_THEME = {
    "name": "Modern",
    "window": {"applicationTheme": "dark", "useMica": False},
    "tab": {
        "background": "terminalBackground",
        "unfocusedBackground": "terminalBackground",
        "showCloseButton": "hover",
    },
    "tabRow": {
        "background": "terminalBackground",
        "unfocusedBackground": "terminalBackground",
    },
}

# Тема Oh My Posh (bubblesextra, доработанная). Иконки записаны как \uXXXX.
OMP_THEME_JSON = r'''{
  "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json",
  "blocks": [
    {
      "alignment": "left",
      "segments": [
        {
          "background": "#313244",
          "foreground": "#7BEF72",
          "leading_diamond": "\ue0b6",
          "options": {
            "style": "full"
          },
          "style": "diamond",
          "template": "\uf07b {{ if .WSL }}{{ if .Env.PWD }}{{ .Env.PWD }}{{ else }}{{ .Path }}{{ end }}{{ else }}{{ .AbsolutePWD }}{{ end }}",
          "trailing_diamond": "\ue0b4",
          "type": "path"
        },
        {
          "background": "#313244",
          "foreground": "#609DFF",
          "foreground_templates": [
            "{{ if or (.Working.Changed) (.Staging.Changed) }}#FF9C5E{{ end }}",
            "{{ if and (gt .Ahead 0) (gt .Behind 0) }}#FF5B89{{ end }}",
            "{{ if gt .Ahead 0 }}#B77AFF{{ end }}",
            "{{ if gt .Behind 0 }}#B77AFF{{ end }}"
          ],
          "leading_diamond": " \ue0b6",
          "options": {
            "branch_template": "{{ trunc 25 .Branch }}"
          },
          "style": "diamond",
          "template": " {{ .UpstreamIcon }}{{ .HEAD }}{{if .BranchStatus }} {{ .BranchStatus }}{{ end }}{{ if .Working.Changed }} \uf044 {{ .Working.String }}{{ end }}{{ if and (.Working.Changed) (.Staging.Changed) }} |{{ end }}{{ if .Staging.Changed }} \uf046 {{ .Staging.String }}{{ end }}{{ if gt .StashCount 0 }} \ueb4b {{ .StashCount }}{{ end }} ",
          "trailing_diamond": "\ue0b4",
          "type": "git"
        },
        {
          "background": "#313244",
          "foreground": "#FFD985",
          "leading_diamond": " \ue0b6",
          "style": "diamond",
          "template": "\ue235 {{ if .Error }}{{ .Error }}{{ else }}{{ if .Venv }}{{ .Venv }} {{ end }}{{ .Full }}{{ end }}",
          "trailing_diamond": "\ue0b4",
          "type": "python"
        },
        {
          "background": "#313244",
          "foreground": "#55E2FC",
          "leading_diamond": " \ue0b6",
          "style": "diamond",
          "template": "\ue626{{ if .Error }}{{ .Error }}{{ else }}{{ .Full }}{{ end }}",
          "trailing_diamond": "\ue0b4",
          "type": "go"
        },
        {
          "background": "#313244",
          "foreground": "#7BEF72",
          "leading_diamond": " \ue0b6",
          "style": "diamond",
          "template": "\ue718{{ if .PackageManagerIcon }}{{ .PackageManagerIcon }} {{ end }}{{ .Full }}",
          "trailing_diamond": "\ue0b4",
          "type": "node"
        },
        {
          "background": "#313244",
          "foreground": "#FF5B89",
          "leading_diamond": " \ue0b6",
          "style": "diamond",
          "template": "\ue791{{ if .Error }}{{ .Error }}{{ else }}{{ .Full }}{{ end }}",
          "trailing_diamond": "\ue0b4",
          "type": "ruby"
        },
        {
          "background": "#313244",
          "foreground": "#FF5B89",
          "leading_diamond": " \ue0b6",
          "style": "diamond",
          "template": "\ue738{{ if .Error }}{{ .Error }}{{ else }}{{ .Full }}{{ end }}",
          "trailing_diamond": "\ue0b4",
          "type": "java"
        },
        {
          "background": "#313244",
          "foreground": "#B77AFF",
          "leading_diamond": " \ue0b6",
          "style": "diamond",
          "template": "\ue624{{ if .Error }}{{ .Error }}{{ else }}{{ .Full }}{{ end }} ",
          "trailing_diamond": "\ue0b4",
          "type": "julia"
        },
        {
          "type": "php",
          "style": "diamond",
          "foreground": "#8F9EFF",
          "background": "#313244",
          "leading_diamond": " \ue0b6",
          "template": "\ue73d {{ .Full }} ",
          "trailing_diamond": "\ue0b4"
        },
        {
          "background": "#313244",
          "foreground": "#B77AFF",
          "foreground_templates": [
            "{{if eq \"Charging\" .State.String}}#55E2FC{{end}}",
            "{{if eq \"Discharging\" .State.String}}#FF9C5E{{end}}",
            "{{if eq \"Full\" .State.String}}#7BEF72{{end}}"
          ],
          "leading_diamond": " \ue0b6",
          "options": {
            "charged_icon": "\uf240 ",
            "charging_icon": "\u21e1 ",
            "discharging_icon": "\u21e3 "
          },
          "style": "diamond",
          "template": "{{ if not .Error }}{{ .Icon }}{{ .Percentage }}{{ end }}{{ .Error }}",
          "trailing_diamond": "\ue0b4",
          "type": "battery"
        }
      ],
      "type": "prompt",
      "newline": true
    },
    {
      "alignment": "left",
      "newline": false,
      "segments": [
        {
          "background": "#313244",
          "foreground": "#C8CEE6",
          "leading_diamond": "\ue0b6",
          "options": {
            "style": "austin",
            "threshold": 150
          },
          "style": "diamond",
          "template": "{{ .FormattedMs }}",
          "trailing_diamond": "\ue0b4 ",
          "type": "executiontime"
        },
        {
          "background": "#313244",
          "foreground": "#FF5B89",
          "leading_diamond": "\ue0b6",
          "style": "diamond",
          "template": "{{ .UserName }} \u276f",
          "trailing_diamond": "\ue0b4",
          "type": "text"
        }
      ],
      "type": "prompt"
    }
  ],
  "final_space": true,
  "version": 4
}'''


# ----------------------------------------------------------------------------
# Вспомогательные функции
# ----------------------------------------------------------------------------

def say(msg):
    print(f"==> {msg}", flush=True)


def warn(msg):
    print(f"  ! {msg}", flush=True)


def stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def backup(path: Path):
    if path.exists():
        dst = path.with_name(f"{path.name}.backup-{stamp()}")
        shutil.copy2(path, dst)
        print(f"     резервная копия: {dst}")


def run(cmd, check=False, capture=False):
    """Запускает команду; возвращает CompletedProcess или None, если программы нет."""
    try:
        return subprocess.run(
            cmd,
            check=check,
            capture_output=capture,
            text=capture,
            encoding="utf-8" if capture else None,
            errors="replace" if capture else None,
        )
    except FileNotFoundError:
        return None


def documents_dir() -> Path:
    """Настоящая папка «Документы» (учитывает перенос в OneDrive)."""
    try:
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                        ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

        # FOLDERID_Documents {FDD39AD0-238F-46AF-ADB4-6C85480369C7}
        fid = GUID(0xFDD39AD0, 0x238F, 0x46AF,
                   (ctypes.c_ubyte * 8)(0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7))
        p = ctypes.c_wchar_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(fid), 0, None, ctypes.byref(p)) == 0:
            result = Path(p.value)
            ctypes.windll.ole32.CoTaskMemFree(p)
            return result
    except Exception:
        pass
    return Path.home() / "Documents"


def find_exe(name, extra_paths=()):
    found = shutil.which(name)
    if found:
        return found
    for p in extra_paths:
        if p and Path(p).exists():
            return str(p)
    return None


def local_appdata() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))


def ohmyposh_exe():
    la = local_appdata()
    return find_exe("oh-my-posh", [
        la / "Programs" / "oh-my-posh" / "bin" / "oh-my-posh.exe",
        la / "Microsoft" / "WindowsApps" / "oh-my-posh.exe",
    ])


def clink_exe():
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                 str(local_appdata() / "Programs")):
        if not base:
            continue
        d = Path(base) / "clink"
        for name in ("clink_x64.exe", "clink_arm64.exe", "clink_x86.exe"):
            if (d / name).exists():
                return str(d / name)
    return None


def strip_jsonc(text: str) -> str:
    """Убирает комментарии // и /* */ и висячие запятые (settings.json это допускает)."""
    out, i, n = [], 0, len(text)
    in_str = False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j == -1 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
        elif c == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":
                i += 1  # висячая запятая
            else:
                out.append(c)
                i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def to_wsl_path(win_path: Path) -> str:
    s = str(win_path)
    if len(s) >= 2 and s[1] == ":":
        return f"/mnt/{s[0].lower()}{s[2:].replace(chr(92), '/')}"
    return s.replace("\\", "/")


# ----------------------------------------------------------------------------
# Шаги
# ----------------------------------------------------------------------------

def install_programs():
    say("Установка программ и шрифтов")
    if not shutil.which("winget"):
        warn("winget не найден — установите «Установщик приложений» из Microsoft Store и запустите скрипт снова.")
        return

    if not ohmyposh_exe():
        print("     ставлю Oh My Posh…")
        run(["winget", "install", "JanDeDobbeleer.OhMyPosh", "-s", "winget",
             "--accept-package-agreements", "--accept-source-agreements"])
    else:
        print("     Oh My Posh уже установлен")

    omp = ohmyposh_exe()
    if omp:
        for font in FONTS_TO_INSTALL:
            print(f"     шрифт {font}…")
            run([omp, "font", "install", font])
    else:
        warn("oh-my-posh не найден после установки — откройте новый терминал и запустите скрипт ещё раз.")

    if not clink_exe():
        print("     ставлю Clink (для командной строки)…")
        run(["winget", "install", "chrisant996.Clink",
             "--accept-package-agreements", "--accept-source-agreements"])
    else:
        print("     Clink уже установлен")


def write_theme(target_dir: Path) -> Path:
    say("Тема Oh My Posh")
    target_dir.mkdir(parents=True, exist_ok=True)
    repo_theme = Path(__file__).resolve().parent / "themes" / THEME_FILE_NAME
    if repo_theme.exists():
        theme = json.loads(repo_theme.read_text(encoding="utf-8"))
        print(f"     источник: {repo_theme}")
    else:
        theme = json.loads(OMP_THEME_JSON)  # встроенная копия, если скрипт запущен отдельно
    path = target_dir / THEME_FILE_NAME
    path.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"     {path}")
    return path


def ensure_imaging_libs():
    try:
        import numpy  # noqa: F401
        from PIL import Image  # noqa: F401
        return True
    except ImportError:
        print("     ставлю numpy и Pillow для звёздного поля…")
        r = run([sys.executable, "-m", "pip", "install", "--user", "numpy", "pillow"])
        if r is None or r.returncode != 0:
            return False
        import importlib
        import site
        importlib.invalidate_caches()
        user_site = site.getusersitepackages()
        if user_site not in sys.path:
            sys.path.append(user_site)
        try:
            import numpy  # noqa: F401,F811
            from PIL import Image  # noqa: F401,F811
            return True
        except ImportError:
            return False


def make_starfield(path: Path, seed=7, width=3840, height=2160):
    """Блёклое звёздное поле на прозрачном фоне (PNG RGBA)."""
    import numpy as np
    from PIL import Image, ImageFilter

    rng = np.random.default_rng(seed)
    W, H = width, height
    img = np.zeros((H, W, 4), dtype=np.float32)

    # едва заметная полоса Млечного Пути по диагонали
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.abs((yy - H * 0.15) - (xx * 0.42)) / (H * 0.28)
    band = np.exp(-d ** 2)
    small = (rng.random((H // 16, W // 16)) * 255).astype(np.uint8)
    noise = np.array(
        Image.fromarray(small).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(24)),
        dtype=np.float32) / 255
    img[..., 0] += 150
    img[..., 1] += 160
    img[..., 2] += 220
    img[..., 3] = band * (0.45 + 0.55 * noise) * 10.0

    def star(x, y, a, r=0, col=(255, 255, 255)):
        x0, x1 = max(0, x - r - 2), min(W, x + r + 3)
        y0, y1 = max(0, y - r - 2), min(H, y + r + 3)
        sy, sx = np.mgrid[y0:y1, x0:x1]
        dist = np.sqrt((sx - x) ** 2 + (sy - y) ** 2)
        sig = 0.6 + r * 0.9
        s = a * np.exp(-(dist ** 2) / (2 * sig ** 2))
        patch = img[y0:y1, x0:x1]
        new = np.maximum(patch[..., 3], s)
        w = np.where(new > 0, s / np.maximum(new, 1e-6), 0)
        for c in range(3):
            patch[..., c] = patch[..., c] * (1 - w) + col[c] * w
        patch[..., 3] = new

    palette = [(255, 255, 255), (200, 215, 255), (255, 235, 210), (220, 200, 255)]
    for _ in range(5200):  # много мелких тусклых звёзд, гуще в полосе
        x = int(rng.integers(0, W))
        y = int(rng.integers(0, H))
        if rng.random() > 0.35 + 0.65 * band[y, x]:
            continue
        star(x, y, float(rng.uniform(25, 85)), 0, palette[int(rng.integers(0, 4))])
    for _ in range(260):  # звёзды поярче
        star(int(rng.integers(0, W)), int(rng.integers(0, H)),
             float(rng.uniform(70, 120)), 1, palette[int(rng.integers(0, 4))])
    for _ in range(22):  # несколько мягко светящихся
        star(int(rng.integers(0, W)), int(rng.integers(0, H)),
             float(rng.uniform(90, 135)), 2, palette[int(rng.integers(0, 4))])

    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA").save(path, optimize=True)


def write_starfield(target_dir: Path):
    say("Звёздное поле")
    path = target_dir / STARS_FILE_NAME
    if not ensure_imaging_libs():
        warn("не удалось поставить numpy/Pillow — фон будет без звёзд.")
        return None
    make_starfield(path)
    print(f"     {path}")
    return path


def wt_settings_paths():
    la = local_appdata()
    return [
        la / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        la / "Packages" / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe" / "LocalState" / "settings.json",
        la / "Microsoft" / "Windows Terminal" / "settings.json",
    ]


def configure_windows_terminal(stars_path, opacity):
    say("Windows Terminal")
    candidates = [p for p in wt_settings_paths() if p.exists()]
    if not candidates:
        candidates = [p for p in wt_settings_paths()[:2] if p.parent.exists()][:1]
    if not candidates:
        warn("Windows Terminal не найден — поставьте его из Microsoft Store и запустите скрипт снова.")
        return

    for path in candidates:
        if path.exists():
            raw = path.read_text(encoding="utf-8-sig")
            settings = json.loads(strip_jsonc(raw)) if raw.strip() else {}
            backup(path)
        else:
            settings = {}

        profiles = settings.setdefault("profiles", {})
        if isinstance(profiles, list):  # очень старый формат
            profiles = settings["profiles"] = {"list": profiles}
        defaults = profiles.setdefault("defaults", {})
        plist = profiles.setdefault("list", [])

        schemes = [s for s in settings.get("schemes", []) if s.get("name") != COLOR_SCHEME["name"]]
        settings["schemes"] = schemes + [COLOR_SCHEME]
        themes = [t for t in settings.get("themes", []) if t.get("name") != WT_THEME["name"]]
        settings["themes"] = themes + [WT_THEME]
        settings["theme"] = WT_THEME["name"]
        settings["tabWidthMode"] = "titleLength"

        font = defaults.setdefault("font", {})
        font["face"] = FONT_FACE
        font["weight"] = "medium"
        defaults.pop("fontFace", None)
        defaults.update({
            "colorScheme": COLOR_SCHEME["name"],
            "opacity": opacity,
            "useAcrylic": False,
            "padding": "14, 10",
            "cursorShape": "bar",
        })
        if stars_path:
            defaults.update({
                "backgroundImage": str(stars_path),
                "backgroundImageStretchMode": "uniformToFill",
                "backgroundImageAlignment": "center",
                "backgroundImageOpacity": 1.0,
            })

        # Профили WSL получают свою схему/шрифт из «фрагментов», поэтому задаём явно.
        for p in plist:
            src = str(p.get("source", ""))
            if src == "Windows.Terminal.Wsl" or src.startswith("CanonicalGroupLimited"):
                p["colorScheme"] = COLOR_SCHEME["name"]
                p.setdefault("font", {}).update({"face": FONT_FACE, "weight": "medium"})
                p.pop("fontFace", None)
                p["cursorShape"] = "bar"
                if not p.get("hidden") and not p.get("icon"):
                    p["icon"] = WSL_ICON

        path.write_text(json.dumps(settings, indent=4, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        print(f"     {path}")


def ps_profile_path(shell):
    r = run([shell, "-NoProfile", "-NoLogo", "-Command",
             "[Console]::OutputEncoding = [Text.Encoding]::UTF8; $PROFILE.CurrentUserCurrentHost"], capture=True)
    if r is None or r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip().splitlines()[-1])


def configure_powershell(theme_path: Path):
    say("PowerShell")
    line = f'oh-my-posh init pwsh --config "{theme_path}" | Invoke-Expression'
    done_any = False
    for shell in ("powershell", "pwsh"):
        if not shutil.which(shell):
            continue
        prof = ps_profile_path(shell)
        if not prof:
            warn(f"не удалось узнать путь профиля для {shell}")
            continue
        prof.parent.mkdir(parents=True, exist_ok=True)
        old = ""
        if prof.exists():
            backup(prof)
            old = prof.read_text(encoding="utf-8-sig", errors="replace")
        kept = [l for l in old.splitlines() if "oh-my-posh init" not in l]
        kept.append(line)
        prof.write_text("\r\n".join(kept) + "\r\n", encoding="utf-8-sig")
        print(f"     {shell}: {prof}")
        done_any = True

    if shutil.which("powershell"):
        r = run(["powershell", "-NoProfile", "-Command",
                 "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"], capture=True)
        if r is None or r.returncode != 0:
            warn("не удалось разрешить запуск профиля (ExecutionPolicy). Выполните вручную в PowerShell:\n"
                 "       Set-ExecutionPolicy RemoteSigned -Scope CurrentUser")
        else:
            print("     запуск профиля разрешён (ExecutionPolicy RemoteSigned для текущего пользователя)")
    if not done_any:
        warn("PowerShell не найден")


def configure_cmd(theme_path: Path):
    say("Командная строка (Clink)")
    clink_dir = local_appdata() / "clink"
    clink_dir.mkdir(parents=True, exist_ok=True)
    cfg = str(theme_path).replace("\\", "/")
    lua = f"load(io.popen('oh-my-posh init cmd --config {cfg}'):read(\"*a\"))()\n"
    (clink_dir / "oh-my-posh.lua").write_text(lua, encoding="utf-8")
    print(f"     {clink_dir / 'oh-my-posh.lua'}")
    exe = clink_exe()
    if exe:
        r = run([exe, "autorun", "install"], capture=True)
        if r is not None and r.returncode == 0:
            print("     автозапуск Clink включён")
        else:
            warn("не удалось включить автозапуск Clink — выполните:  clink autorun install")
    else:
        warn("Clink не найден — без него командная строка останется без темы")


def wsl_distros():
    try:
        res = subprocess.run(["wsl", "-l", "-q"], capture_output=True)
    except FileNotFoundError:
        return []
    if res.returncode != 0:
        return []
    out = res.stdout
    text = out.decode("utf-16-le", errors="ignore") if b"\x00" in out else out.decode("utf-8", errors="ignore")
    names = [n.strip().strip("\x00") for n in text.splitlines()]
    return [n for n in names if n and not n.lower().startswith("docker-desktop")]


BASH_SETUP = r'''#!/usr/bin/env bash
set -u
THEME="$1"
mkdir -p "$HOME/.local/bin"
export PATH="$HOME/.local/bin:$PATH"
if ! command -v oh-my-posh >/dev/null 2>&1; then
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://ohmyposh.dev/install.sh | bash -s -- -d "$HOME/.local/bin" \
      || echo "  ! установка Oh My Posh не удалась; возможно, нужен unzip: sudo apt install -y unzip"
  else
    echo "  ! нужен curl: sudo apt install -y curl unzip — затем запустите скрипт снова"
  fi
fi
touch "$HOME/.bashrc"
cp "$HOME/.bashrc" "$HOME/.bashrc.backup-$(date +%Y%m%d-%H%M%S)"
sed -i '/oh-my-posh init bash/d' "$HOME/.bashrc"
grep -q '\.local/bin' "$HOME/.bashrc" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
echo "eval \"\$(oh-my-posh init bash --config '$THEME')\"" >> "$HOME/.bashrc"
echo "     ~/.bashrc обновлён"
'''


def configure_wsl(theme_path: Path):
    say("Ubuntu / WSL")
    distros = wsl_distros()
    if not distros:
        print("     WSL-дистрибутивы не найдены — пропускаю")
        return
    tmp = Path(tempfile.gettempdir()) / "omp_wsl_setup.sh"
    tmp.write_text(BASH_SETUP, encoding="utf-8", newline="\n")
    theme_wsl = to_wsl_path(theme_path)
    script_wsl = to_wsl_path(tmp)
    for d in distros:
        print(f"     {d}")
        r = run(["wsl", "-d", d, "-e", "bash", script_wsl, theme_wsl])
        if r is None or r.returncode != 0:
            warn(f"не удалось настроить {d}")


# ----------------------------------------------------------------------------

def main():
    if os.name != "nt":
        sys.exit("Этот скрипт для Windows.")

    ap = argparse.ArgumentParser(description="Оформление терминала: Oh My Posh + Windows Terminal")
    ap.add_argument("--no-install", action="store_true", help="не ставить программы и шрифты")
    ap.add_argument("--no-wsl", action="store_true", help="не настраивать WSL/Ubuntu")
    ap.add_argument("--no-stars", action="store_true", help="без звёздного поля на фоне")
    ap.add_argument("--opacity", type=int, default=90, help="непрозрачность фона, %% (по умолчанию 90)")
    args = ap.parse_args()

    target_dir = documents_dir() / "oh-my-posh"

    if not args.no_install:
        install_programs()
    theme_path = write_theme(target_dir)
    stars_path = None if args.no_stars else write_starfield(target_dir)
    configure_windows_terminal(stars_path, max(0, min(100, args.opacity)))
    configure_powershell(theme_path)
    configure_cmd(theme_path)
    if not args.no_wsl:
        configure_wsl(theme_path)

    print()
    say("Готово! Полностью закройте Windows Terminal (все окна) и откройте заново.")


if __name__ == "__main__":
    main()

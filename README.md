# terminal-setup

Одна команда, и Windows Terminal выглядит одинаково во всех оболочках: PowerShell, командной строке и Ubuntu (WSL).

*One command to give Windows Terminal the same modern look in PowerShell, cmd and WSL: an Oh My Posh prompt, the JetBrains Mono Nerd Font, a vivid Catppuccin-based color scheme, transparency and a faint starfield background. Run `python setup_terminal.py` on Windows.*

![Звёздное поле на фоне терминала](docs/starfield-preview.png)

## Что получится

- **Строка приглашения Oh My Posh** на основе темы `bubblesextra`:
  - всё в одну строку, перед каждой командой пустая строка;
  - полный путь к папке: `C:\Users\…` в Windows и `/home/…` в Ubuntu;
  - ветка git с числом изменений, версии Python, Node, Go и других языков в папках проектов;
  - время выполнения долгих команд.
- **Шрифт** JetBrains Mono Nerd Font начертания Medium, запасной шрифт Meslo Nerd Font.
- **Цветовая схема «Mocha Vivid»**: более яркая и насыщенная версия палитры Catppuccin Mocha.
- **Windows Terminal**: прозрачность фона 90%, блёклое звёздное поле, курсор-черта, отступы, вкладки по ширине названия, крестик на вкладке появляется только при наведении.
- **Одинаковая тема везде**: Windows PowerShell, PowerShell 7, Developer PowerShell for VS, командная строка, Developer Command Prompt for VS и Ubuntu (WSL).

## Требования

- Windows 10 или 11 с [Windows Terminal](https://aka.ms/terminal)
- Python 3.9+
- `winget` («Установщик приложений» из Microsoft Store)
- WSL с Ubuntu — по желанию

## Установка

```powershell
git clone https://github.com/<ваш-логин>/terminal-setup.git
cd terminal-setup
python setup_terminal.py
```

Или скачайте ZIP (**Code → Download ZIP**), распакуйте и запустите `python setup_terminal.py` в папке.

После завершения **полностью закройте Windows Terminal** (все окна) и откройте заново.

### Ключи

| Ключ | Что делает |
|---|---|
| `--no-install` | не ставить программы и шрифты, только применить настройки |
| `--no-wsl` | не настраивать Ubuntu / WSL |
| `--no-stars` | без звёздного поля на фоне |
| `--opacity N` | непрозрачность фона в процентах, по умолчанию `90` |

## Что меняет скрипт

| Что | Где |
|---|---|
| Ставит Oh My Posh, Clink, шрифты JetBrains Mono и Meslo | через `winget` и `oh-my-posh font install` |
| Тема и звёздное поле | `Документы\oh-my-posh\` |
| Настройки Windows Terminal | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_…\LocalState\settings.json` |
| Профиль PowerShell | `$PROFILE` (Windows PowerShell и PowerShell 7) |
| Разрешение запуска профиля | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Командная строка | `%LOCALAPPDATA%\clink\oh-my-posh.lua` + автозапуск Clink |
| Ubuntu (WSL) | `~/.bashrc`; при необходимости ставит Oh My Posh в `~/.local/bin` |

Перед изменением `settings.json`, профилей PowerShell и `~/.bashrc` скрипт сохраняет рядом резервную копию вида `*.backup-ГГГГММДД-ЧЧММСС`. Повторный запуск ничего не дублирует.

### Как вернуть всё назад

Переименуйте нужную резервную копию обратно в исходное имя, например `settings.json.backup-20261105-174844` → `settings.json`.

## Настройка под себя

- **Строка приглашения**: `themes/bubblesextra.omp.json`. Цвета записаны обычными HEX-кодами, иконки берутся из [Nerd Fonts](https://www.nerdfonts.com/cheat-sheet).
- **Цвета терминала, прозрачность, шрифт**: константы `COLOR_SCHEME`, `WT_THEME` и `FONT_FACE` в начале `setup_terminal.py`.
- **Звёздное поле**: функция `make_starfield()`. Число и яркость звёзд задаются в циклах в её конце.

## Если что-то не так

- **Вместо иконок ромбики или квадратики.** Терминал не видит шрифт: закройте все окна Windows Terminal и откройте снова. Шрифт должен быть установлен в Windows, а не внутри WSL.
- **PowerShell пишет, что выполнение сценариев отключено.** Выполните `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- **В командной строке нет темы.** Проверьте, что Clink установлен, и выполните `clink autorun install`.
- **В Ubuntu нет темы.** Для установщика Oh My Posh нужны `curl` и `unzip`: `sudo apt install -y curl unzip`, затем запустите скрипт снова.
- **Пузыри в соседних строках касаются друг друга.** Это ограничение терминала: фон строки заливается на всю её высоту, поэтому тема и выводит всё в одну строку.

## Благодарности

- [Oh My Posh](https://ohmyposh.dev): тема `themes/bubblesextra.omp.json` основана на `bubblesextra` из Oh My Posh (MIT, © Jan De Dobbeleer), подробности в [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- [Catppuccin](https://catppuccin.com): палитра Mocha, на которой основана схема «Mocha Vivid»
- [Nerd Fonts](https://www.nerdfonts.com), [JetBrains Mono](https://www.jetbrains.com/lp/mono/), [Clink](https://chrisant996.github.io/clink/)

## Лицензия

[MIT](LICENSE)

"""Език на drv-marka: български, ако системата е на български, иначе английски.
   DRV_MARKA_EZIK=bg|en го задава ръчно. _("текст") превежда; шаблоните с {} хващат и f-низовете."""
import os
import re

_EZIK = [None]


def ezik():
    if _EZIK[0] is None:
        e = os.environ.get("DRV_MARKA_EZIK", "")
        if not e:
            loc = os.environ.get("LANGUAGE") or os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or ""
            if not loc or loc in ("C", "C.UTF-8", "POSIX"):          # pkexec чисти средата: взимаме езика на системата
                try:
                    for l in open("/etc/default/locale"):
                        if l.startswith(("LANG=", "LANGUAGE=")):
                            loc = l.split("=", 1)[1].strip().strip('"')
                            break
                except OSError:
                    pass
            e = "bg" if loc.lower().startswith("bg") else "en"
        _EZIK[0] = "bg" if e.startswith("bg") else "en"
    return _EZIK[0]


def set_ezik(e):
    _EZIK[0] = "bg" if e.startswith("bg") else "en"


EN = {
    "Помощ": "Help",
    "За програмата": "About",
    "Меню": "Menu",
    "Проверка, търсене и инсталиране на драйвери за Debian — с „Върни както беше“.": "Check, find and install drivers on Debian — with “Undo everything”.",
    "Как се ползва": "How to use",
    "1. Програмата сама проверява компютъра. Отгоре пише дали всичко е наред.\n2. <b>Намери драйвери</b> търси пакет за всяко устройство без драйвер и липсващ фърмуер.\n3. <b>Поправи…</b> показва какво може да се направи. Отметни нужното и въведи паролата си.\n4. Рестартирай компютъра, за да се заредят новите драйвери.":
        "1. The program checks the computer by itself. The top line says whether everything is fine.\n2. <b>Find drivers</b> looks for a package for every device without a driver and for missing firmware.\n3. <b>Fix…</b> shows what can be done. Tick what you need and enter your password.\n4. Restart the computer to load the new drivers.",
    "Безопасно ли е?": "Is it safe?",
    "Проверката само чете. Нищо не се инсталира без „Поправи“ и паролата. Преди всяка поправка apt прави проба, а пакетите, които би махнал, се показват в червено. Старите извори на apt се пазят в <tt>/var/backups/drv-marka</tt>.":
        "The check only reads. Nothing is installed without “Fix” and your password. Before every fix apt does a dry run, and packages it would remove are shown in red. The old apt sources are kept in <tt>/var/backups/drv-marka</tt>.",
    "Ако нещо се обърка": "If something goes wrong",
    "• Натисни <b>↶</b> (Върни както беше): маха пакетите, сложени от програмата, и връща старите извори.\n• Ако новото ядро не тръгва, избери старото в менюто при стартиране и пусни „Върни“ оттам.\n• От терминала: <tt>drv-marka --reset</tt>":
        "• Press <b>↶</b> (Undo everything): removes the packages the program installed and restores the old sources.\n• If a new kernel won't boot, pick the old one in the boot menu and run “Undo” from there.\n• In a terminal: <tt>drv-marka --reset</tt>",
    "NVIDIA": "NVIDIA",
    "<b>Ядро Linux</b> и „Намери драйвери“ ползват nvidia-detect на Debian, за да предложат правилния драйвер. При Secure Boot след рестарт се иска потвърждение на ключа (MOK).":
        "<b>Linux kernel</b> and “Find drivers” use Debian's nvidia-detect to suggest the right driver. With Secure Boot you'll be asked to confirm the key (MOK) after restart.",
    "Команден ред": "Command line",
    "<tt>drv-marka --text --search</tt>  проверка и търсене в терминала\n<tt>drv-marka --fix</tt>  пита за всяка поправка\n<tt>drv-marka --kernel</tt>  по-ново ядро\n<tt>drv-marka --reset</tt>  връща всичко както беше":
        "<tt>drv-marka --text --search</tt>  check and search in the terminal\n<tt>drv-marka --fix</tt>  asks about every fix\n<tt>drv-marka --kernel</tt>  a newer kernel\n<tt>drv-marka --reset</tt>  undoes everything",
    "Проблем или идея?": "Problem or idea?",
    "Пиши в GitHub: <a href=\"https://github.com/nikogurzov/drv-marka/issues\">github.com/nikogurzov/drv-marka/issues</a>":
        "Write on GitHub: <a href=\"https://github.com/nikogurzov/drv-marka/issues\">github.com/nikogurzov/drv-marka/issues</a>",
    "{} [{}] {} ({}): {}": "{} [{}] {} ({}): {}",
    "без драйвер": "no driver",
    "Без драйвер в ядрото: {}": "No driver in the kernel: {}",
    "Без драйвер. За този вид устройство това обикновено е нормално.": "No driver. For this kind of device that is usually normal.",
    "Безжично устройство": "Wireless device",
    "Без него Debian не може да инсталира фърмуер за Wi-Fi, видео и звук.": "Without it Debian can't install firmware for Wi-Fi, video and sound.",
    "Вероятно се решава с пакета {}. Той още не е инсталиран.": "Probably fixed by the package {}. It is not installed yet.",
    ", версия {}": ", version {}",
    "Вече си в групата adm, но това важи след излизане и влизане отново в системата. Дотогава не виждам липсващия фърмуер.":
        "You are already in the adm group, but it takes effect after logging out and in again. Until then I can't see missing firmware.",
    "Видеокарта NVIDIA": "NVIDIA graphics card",
    "== Включвам в изворите: ": "== Enabling in the sources: ",
    "Включва non-free-firmware в изворите на Debian": "Enables non-free-firmware in Debian's sources",
    ". ВНИМАНИЕ: ще махне {}": ". WARNING: will remove {}",
    "Въвеждане": "Input",
    "== Върнат е старият {}": "== Restored the old {}",
    "Върни": "Undo",
    "Върни както беше": "Undo everything",
    "Върни както беше: маха всичко, сложено от програмата": "Undo everything: removes all the program installed",
    "== ГОТОВО.": "== DONE.",
    "== ГОТОВО. Всичко е както преди програмата. Рестартирай компютъра.": "== DONE. Everything is as before the program. Restart the computer.",
    "== ГОТОВО. Рестартирай компютъра, за да се заредят новите драйвери.": "== DONE. Restart the computer to load the new drivers.",
    "Данни": "Storage",
    "Да продължа ли? [д/Н] ": "Continue? [y/N] ",
    "д/Н": "y/N",
    "Д/н": "Y/n",
    "== Добавих {}-backports в изворите ({})": "== Added {}-backports to the sources ({})",
    "Добавя те в групата adm, за да виждам липсващия фърмуер. Важи след излизане и влизане.":
        "Adds you to the adm group so I can see missing firmware. Takes effect after logging out and in.",
    "Достъп до дневника на ядрото": "Access to the kernel log",
    "Драйвер за {}": "Driver for {}",
    "ДРАЙВЕРИ": "DRIVERS",
    "Драйвери (drv-marka)": "Drivers (drv-marka)",
    "Драйверът на NVIDIA ({})": "The NVIDIA driver ({})",
    "== {} е добавен в групата adm. Важи след излизане и влизане отново.": "== {} was added to the adm group. Takes effect after logging out and in again.",
    "== {} е изваден от групата adm": "== {} was removed from the adm group",
    "За по-задълбочено търсене натисни „Намери драйвери“.": "For a deeper search press “Find drivers”.",
    "Заредени драйвери": "Loaded drivers",
    "ЗАРЕДЕНИ ДРАЙВЕРИ ({})": "LOADED DRIVERS ({})",
    "Зарежда драйвера {}": "Loads the driver {}",
    "Затвори": "Close",
    "Звук": "Sound",
    "Избери какво да направя. Ще поискам паролата ти.": "Choose what to do. I will ask for your password.",
    "Изворът non-free-firmware": "The non-free-firmware source",
    "Изворът non-free-firmware не е включен": "The non-free-firmware source is not enabled",
    "== Изтрит {}": "== Deleted {}",
    "Има драйвер „{}“, но не е зареден.": "There is a driver “{}”, but it is not loaded.",
    "Инсталира {}": "Installs {}",
    "Инсталирай": "Install",
    "Инсталирането не успя (виж по-горе).": "Installing failed (see above).",
    "Инсталира nvidia-detect: инструментът на Debian, който казва дали картата се поддържа. После натисни „Намери драйвери“.":
        "Installs nvidia-detect: Debian's tool that tells whether the card is supported. Then press “Find drivers”.",
    "Инсталира pciutils, за да се виждат вътрешните устройства": "Installs pciutils so internal devices are visible",
    "Инструментът lspci": "The lspci tool",
    "Камера": "Camera",
    "Карта": "Card",
    " Картата е твърде стара за драйвера на NVIDIA в тази версия на Debian, затова остава nouveau.":
        " The card is too old for the NVIDIA driver in this Debian version, so nouveau stays.",
    "Кое ядро работи и има ли по-ново": "Which kernel is running and is there a newer one",
    "Кой драйвер е за видеокартата": "Which driver is right for the graphics card",
    " Кой драйвер на NVIDIA е за нея ще каже nvidia-detect.": " nvidia-detect will tell which NVIDIA driver is right for it.",
    "Комуникация": "Communication",
    "Копирай всичко като текст": "Copy everything as text",
    "Копирано.": "Copied.",
    "Липсват поправките за процесора": "The CPU microcode updates are missing",
    "Липсва търсачката isenkram": "The isenkram finder is missing",
    "Липсва фърмуер: {}": "Missing firmware: {}",
    "Липсва GTK 4 за прозореца. Инсталирай го с:\n  sudo apt install python3-gi gir1.2-gtk-4.0\nДотогава работи в терминала: drv-marka.py --text --search  или  drv-marka.py --fix\n":
        "GTK 4 is missing for the window. Install it with:\n  sudo apt install python3-gi gir1.2-gtk-4.0\nUntil then it works in the terminal: drv-marka.py --text --search  or  drv-marka.py --fix\n",
    "== Махам пакетите, сложени от програмата: ": "== Removing the packages the program installed: ",
    "Махането не успя (виж по-горе). Нищо друго не е пипано.": "Removing failed (see above). Nothing else was touched.",
    "МОЖЕ ДА СЕ ПОПРАВИ (drv-marka.py --fix)": "CAN BE FIXED (drv-marka.py --fix)",
    "Може да се сложи (не е отметнато, избери само ако имаш нужда, например нов хардуер без драйвер):":
        "Can be installed (not ticked; choose only if you need it, e.g. new hardware without a driver):",
    "Намерени неща за проверка: {}": "Things to check: {}",
    "Намерен пакет: {}": "Package found: {}",
    "Намери драйвери": "Find drivers",
    "НАПРАВЕНО ОТ ПРОГРАМАТА: {} пъти, {} пакета (връщане: drv-marka.py --reset)": "DONE BY THE PROGRAM: {} times, {} packages (undo: drv-marka.py --reset)",
    "Не беше проверено": "Not checked",
    "НЕ БЕШЕ ПРОВЕРЕНО": "NOT CHECKED",
    "Не знам от кой пакет идва. Може да не е нужен.": "I don't know which package it comes from. It may not be needed.",
    "Не намерих липсващи драйвери.": "No missing drivers found.",
    "Не намерих липсващи драйвери или фърмуер.": "No missing drivers or firmware found.",
    "Не намерих липсващи драйвери, но част не беше проверена.": "No missing drivers found, but part was not checked.",
    "Непознат аргумент: {}": "Unknown argument: {}",
    "!! НЕ РЕСТАРТИРАЙ: за ядро {} липсват драйверите: {}. Натисни „Върни“.": "!! DO NOT RESTART: kernel {} is missing the drivers: {}. Press “Undo”.",
    "   Не успях да ги сложа обратно. Пусни: sudo apt install ": "   I couldn't put them back. Run: sudo apt install ",
    "   Нови пакети: ": "   New packages: ",
    "няма": "none",
    "Няма драйвер за това устройство.": "There is no driver for this device.",
    "Няма драйвер. Устройството може да не работи.": "No driver. The device may not work.",
    "Няма зареден драйвер за картата.": "No driver is loaded for the card.",
    "Няма какво да се инсталира.": "Nothing to install.",
    "Няма какво да се прави": "Nothing to do",
    "Нямам достъп до дневника на ядрото, затова не виждам липсващ фърмуер. Поправката „Достъп до дневника“ го оправя.":
        "I have no access to the kernel log, so I can't see missing firmware. The “Access to the kernel log” fix solves it.",
    "Няма по-ново ядро за този компютър.": "There is no newer kernel for this computer.",
    "Няма dpkg, затова инсталираните пакети не се виждат.": "dpkg is missing, so installed packages can't be seen.",
    "Няма lspci, затова вътрешните устройства не се виждат. Идва с пакета pciutils.": "lspci is missing, so internal devices can't be seen. It comes with the pciutils package.",
    "== Остава само: ": "== Only this remains: ",
    "Отказвам, неправилни имена: ": "Refusing, invalid names: ",
    "от backports": "from backports",
    "Официалното стабилно ядро на Debian с последните поправки.": "Debian's official stable kernel with the latest fixes.",
    "Пакетът {} е инсталиран, но няма точно този файл. Често е търсена по-нова версия и устройството работи с друга.":
        "The package {} is installed but lacks this exact file. Often a newer version is requested and the device works with another one.",
    "Пакетът {} поправя грешки и пробиви в процесора.": "The package {} fixes CPU bugs and vulnerabilities.",
    "Памет": "Memory",
    " Подходящият драйвер на NVIDIA за нея е {}.": " The right NVIDIA driver for it is {}.",
    "По-ново ядро за нов хардуер, по-малко тествано от стабилното.": "A newer kernel for new hardware, less tested than the stable one.",
    "Поправи ({})…": "Fix ({})…",
    "Поправи": "Fix",
    "Поправи…": "Fix…",
    "Препоръчан от nvidia-detect за тази карта. При Secure Boot ще поиска потвърждение на ключ след рестарт.":
        "Recommended by nvidia-detect for this card. With Secure Boot it will ask to confirm a key after restart.",
    " (при „Върни“ се слагат обратно)": " (“Undo” puts them back)",
    "Принтер": "Printer",
    "Провери отново": "Check again",
    "Проверка": "Check",
    "ПРОВЕРКА": "CHECK",
    "Проверката не успя да прочете устройствата.": "The check could not read the devices.",
    "Проверявам…": "Checking…",
    "Програмата не е променяла нищо. Няма какво да връщам.": "The program has not changed anything. Nothing to undo.",
    "Работи с драйвера на NVIDIA{}.": "Runs with the NVIDIA driver{}.",
    "  ← работи сега": "  ← running now",
    "Работи със свободния драйвер nouveau.": "Runs with the free nouveau driver.",
    "!! Работиш с ядро {}, сложено от програмата. Него не махам: стартирай със старото и пусни „Върни“ пак.":
        "!! You are running kernel {}, installed by the program. I won't remove it: boot the old one and run “Undo” again.",
    "Сега работи ядро {}. Инсталирани: {}": "Running kernel {}. Installed: {}",
    "Сега работи ядро {}.\nИнсталирани:\n{}\n\n": "Running kernel {}.\nInstalled:\n{}\n\n",
    "== Слагам обратно махнатото: ": "== Putting back what was removed: ",
    "С нея Debian казва кой пакет е за кое устройство. Инсталирай я и търси отново.": "With it Debian tells which package is for which device. Install it and search again.",
    "Снимки": "Imaging",
    "стабилно": "stable",
    "   {} (старото е запазено в {})": "   {} (the old one is saved in {})",
    "{} Старото ядро остава в менюто при стартиране. Преди рестарт проверявам NVIDIA и другите DKMS драйвери.":
        "{} The old kernel stays in the boot menu. Before restarting I check NVIDIA and the other DKMS drivers.",
    ". Стартирай със старото ядро и натисни „Върни“ пак.": ". Boot the old kernel and press “Undo” again.",
    "Трябва да се пусне като root (през pkexec).": "Must be run as root (through pkexec).",
    "Търсенето е направено.": "The search is done.",
    "Търсен файл: {}": "Requested file: {}",
    "Търси драйвери и пакети за всяко устройство": "Finds drivers and packages for every device",
    "Търси драйвер или устройство": "Search for a driver or device",
    "Търся драйвери…": "Looking for drivers…",
    "Търся драйвери за устройствата…": "Looking for drivers for the devices…",
    "Търся липсващ фърмуер…": "Looking for missing firmware…",
    "Устройства": "Devices",
    "УСТРОЙСТВА ({})": "DEVICES ({})",
    "Фърмуер и пакети": "Firmware and packages",
    "ФЪРМУЕР И ПАКЕТИ ЗА ДРАЙВЕРИ ({})": "FIRMWARE AND DRIVER PACKAGES ({})",
    "Чета драйверите…": "Reading drivers…",
    "Чета пакетите…": "Reading packages…",
    "Чета устройствата…": "Reading devices…",
    "Ще върна старите извори на apt и групите на потребителя.": "I will restore the old apt sources and the user's groups.",
    "Ще махна всичко, сложено от програмата, и ще върна старите извори на apt.\n\nПакети ({}): {}\n\nПосле рестартирай компютъра.":
        "I will remove everything the program installed and restore the old apt sources.\n\nPackages ({}): {}\n\nThen restart the computer.",
    "Ще махна пакетите, сложени от програмата:": "I will remove the packages the program installed:",
    "{}, ядро {}": "{}, kernel {}",
    "{}, ядро {}. {}": "{}, kernel {}. {}",
    "== Ядро {}: всички драйвери са готови": "== Kernel {}: all drivers are ready",
    "Ядрото има драйвер „{}“, но не е зареден. Ще го заредя.": "The kernel has a driver “{}”, but it is not loaded. I will load it.",
    "Ядрото няма драйвер за това устройство. Виж и препоръките на isenkram.": "The kernel has no driver for this device. See isenkram's suggestions too.",
    "Ядро Linux {} ({})": "Linux kernel {} ({})",
    "Ядро Linux": "Linux kernel",
    "   apt махна: ": "   apt removed: ",
    "apt-get update не успя. Провери интернета.": "apt-get update failed. Check the internet.",
    "isenkram го препоръчва за устройство в този компютър.": "isenkram recommends it for a device in this computer.",
    "\nОтказано: паролата не беше въведена.\n": "\nCancelled: the password was not entered.\n",
    "\nСпря с грешка (код {}).\n": "\nStopped with an error (code {}).\n",
    "{}\n  {}\n  Да го инсталирам ли? [д/Н] ": "{}\n  {}\n  Install it? [y/N] ",
    "{}\n  {}\n  Да го направя ли? [{}] ": "{}\n  {}\n  Do it? [{}] ",
    "USB разклонител": "USB hub",
    "USB устройство": "USB device",
}

_SH = None


def _shabloni():
    global _SH
    if _SH is None:
        _SH = []
        for k, v in EN.items():
            if "{}" in k:
                rx = re.compile("^" + re.escape(k).replace(r"\{\}", "(.*?)") + "$", re.S)
                _SH.append((rx, v))
    return _SH


def _(s):
    if ezik() == "bg" or not isinstance(s, str):
        return s
    if s in EN:
        return EN[s]
    for rx, v in _shabloni():
        m = rx.match(s)
        if m:
            return v.format(*(EN.get(g, g) for g in m.groups()))
    return s

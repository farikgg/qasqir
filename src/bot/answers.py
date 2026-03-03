class ButtonIDs:
    LANG_RU = "lang_ru"
    LANG_KZ = "lang_kz"

    # --- НОВЫЕ КАТЕГОРИИ (3 шт) ---
    CAT_CHARGE = "cat_charge"   # Зарядка
    CAT_SERVICE = "cat_service" # Сервисы
    CAT_HELP = "cat_help"       # Помощь

    # Главное меню (Функции)
    MAIN_PROBLEM = "main_problem"
    MAIN_PAYMENT = "main_payment"
    MAIN_STORE = "main_store"
    MAIN_APP = "main_app"
    MAIN_MANAGER = "main_manager"
    MAIN_AI_HELP = "main_ai_help"

    # Проблемы
    PROB_BATTERY = "prob_battery"
    PROB_VIDEO = "prob_video"
    PROB_OTHER = "prob_other"

    # Оплата
    PAY_KASPI = "pay_kaspi"
    PAY_REFUND = "pay_refund"

    # Магазин
    STORE_RFID = "store_rfid"
    STORE_HOME = "store_home"

    # Навигация
    BACK = "nav_back"
    FINISH = "nav_finish"


# 2. РУССКИЙ ЯЗЫК
class TextRu:
    WELCOME = "Добро пожаловать в Qasqir! / Qasqir-ға қош келдіңіз!\n\nВыберите язык / Тілді таңдаңыз 👇"

    ASK_NAME = "Как я могу к вам обращаться? (Напишите ваше имя)"
    GREETING = "Рад вас видеть снова, {name}! 👋\nВыберите раздел:"

    # Заголовки категорий
    MENU_CHARGE = "⚡ Зарядка и Оплата:"
    MENU_SERVICE = "🛒 Магазин и Приложение:"
    MENU_HELP = "🤖 Поддержка:"

    # Заголовки разделов
    PROBLEM_HEAD = "Что случилось со станцией?"
    PAYMENT_HEAD = "Вопросы по оплате и балансу:"
    STORE_HEAD = "Магазин Qasqir (Карты и станции):"

    # --- КОНТЕНТ (Твой оригинал) ---

    # 1. Приложение
    APP_LINKS = """
📲Скачать приложение Qasqir    

🤖Android:    
https://play.google.com/store/apps/details?id=kz.qasqir.app

🍏iOS (iPhone):    
https://apps.apple.com/kz/app/qasqir/id1616661520

⚠️ВАЖНО: Убедитесь, что в настройках вашего телефона (Apple ID / Google Play) регион действия указан — Казахстан🇰🇿. Иначе приложение может быть недоступно.
"""

    # 2. Проблемы
    LOW_BATTERY = """
🔋Батарея ниже 7%?    

Быстрые станции (DC) не запустят зарядку, если уровень заряда ниже 5-7%. Это заводская защита батареи.
✅Решение: Вам нужно найти медленную станцию (AC / Переменный ток) и поднять заряд выше 10%.
"""
    VIDEO_INSTRUCTION = "🎥Как заряжаться?\nПосмотрите видео-инструкцию: https://youtu.be/N__-gRImB30?feature=shared"

    # 3. Оплата
    KASPI = """
✅Пополнение через Kaspi (Без комиссии)    

1. Откройте приложение Kaspi -> Платежи.
2. В поиске введите: `Qasqir EV`.
3. Укажите номер телефона, привязанный к аккаунту.
4. Введите сумму. Готово!
"""
    REFUND = """
💸Возврат средств    
Заполните заявку по ссылке: https://qasqir.kz/support/refund

⚠️Важно:    
1. Не указывайте номер карты! Указывайте IBAN счет (KZ...).
2. Прикрепите удостоверение личности.
Срок: ~3 рабочих дня.
"""

    # 4. Магазин
    RFID = """
💳RFID-карта Qasqir (2500 ₸)
Заряжайтесь без приложения! Просто приложите карту.

📹Видео-примеры:    
• AC: https://www.instagram.com/reel/DFC_DsMCDO3/
• GB/T: https://www.instagram.com/reel/DE7gjk5CRl9/
• CCS2: https://www.instagram.com/reel/DE4u0nuiSZZ/

Хотите купить? Нажмите "Позвать менеджера".
"""
    HOME_STATION = """
🏠Домашние зарядные станции    
Мы продаем и устанавливаем станции AC (7, 11, 22 кВт).
Рекомендуем заряжаться на медленных станциях хотя бы 1 раз в месяц для "здоровья" батареи.
"""

    # AI и Финал
    AI_START = """
🤖Виртуальный помощник    
Опишите вашу проблему одним сообщением. Я поищу решение в базе знаний.
  Если не справлюсь — позову человека.  
"""
    MANAGER_WAIT = "Передал информацию оператору. Ожидайте ответа."
    GOODBYE = "Рад был помочь! Хорошей дороги! 🚗💨"

    # КНОПКИ (Словарь: ID -> Текст)
    BUTTONS = {
        ButtonIDs.LANG_RU: "🇷🇺Русский",
        ButtonIDs.LANG_KZ: "🇰🇿Қазақша",

        # КАТЕГОРИИ (3 шт)
        ButtonIDs.CAT_CHARGE:  "⚡ Зарядка",
        ButtonIDs.CAT_SERVICE: "🛒 Сервисы",
        ButtonIDs.CAT_HELP:    "🤖 Помощь",

        ButtonIDs.MAIN_PROBLEM: "🆘Не заряжает",
        ButtonIDs.MAIN_PAYMENT: "💳Оплата / Баланс",
        ButtonIDs.MAIN_STORE: "🛒Магазин",
        ButtonIDs.MAIN_APP: "📱Скачать приложение",
        ButtonIDs.MAIN_MANAGER: "📞Менеджер",
        ButtonIDs.MAIN_AI_HELP: "🤖AI Помощник",

        ButtonIDs.PROB_BATTERY: "🔋Мало заряда (<7%)",
        ButtonIDs.PROB_VIDEO: "📹Как заряжать?",
        ButtonIDs.PROB_OTHER: "⚠️Другая ошибка",

        ButtonIDs.PAY_KASPI: "🏦Kaspi (без комиссии)",
        ButtonIDs.PAY_REFUND: "💸Возврат денег",

        ButtonIDs.STORE_RFID: "💳RFID Карта",
        ButtonIDs.STORE_HOME: "🏠Домашняя станция",

        ButtonIDs.BACK: "🔙Назад",
        ButtonIDs.FINISH: "✅Спасибо, всё",
    }


# 3. КАЗАХСКИЙ ЯЗЫК (ПЕРЕВОД)
class TextKz:
    WELCOME = TextRu.WELCOME  # Приветствие всегда общее

    ASK_NAME = "Сізге қалай хабарлассам болады? (Есіміңізді жазыңыз)"
    GREETING = "Қайта кездескенімізге қуаныштымын, {name}! 👋\nБөлімді таңдаңыз:"

    MENU_CHARGE = "⚡ Қуаттау және Төлем:"
    MENU_SERVICE = "🛒 Дүкен және Қосымша:"
    MENU_HELP = "🤖 Қолдау:"

    PROBLEM_HEAD = "Станцияда не болды?"
    PAYMENT_HEAD = "Төлем және баланс бойынша сұрақтар:"
    STORE_HEAD = "Qasqir Дүкені (Карталар мен станциялар):"

    # --- КОНТЕНТ ---

    # 1. Приложение
    APP_LINKS = """
📲Qasqir қосымшасын жүктеу    

🤖Android:    
https://play.google.com/store/apps/details?id=kz.qasqir.app

🍏iOS (iPhone):    
https://apps.apple.com/kz/app/qasqir/id1616661520

⚠️МАҢЫЗДЫ: Телефоныңыздың параметрлерінде (Apple ID / Google Play) аймақ ретінде Қазақстан🇰🇿 көрсетілгеніне көз жеткізіңіз. Әйтпесе қосымша қолжетімсіз болуы мүмкін.
"""

    # 2. Проблемы
    LOW_BATTERY = """
🔋Батарея 7%-дан төмен бе?    

Егер қуат деңгейі 5-7%-дан төмен болса, жылдам станциялар(DC) қуаттауды бастамайды. Бұл батареяны қорғау жүйесі.
✅Шешімі: Сізге баяу станцияны (AC / Айнымалы ток) тауып, қуатты 10%-ға дейін көтеру қажет.
"""
    VIDEO_INSTRUCTION = "🎥Қалай қуаттау керек?\nБейне-нұсқаулықты қараңыз: https://youtu.be/N__-gRImB30?feature=shared"

    # 3. Оплата
    KASPI = """
✅Kaspi арқылы толтыру (Комиссиясыз)    

1. Kaspi қосымшасын ашыңыз -> Төлемдер.
2. Іздеу жолағына жазыңыз: `Qasqir EV`.
3. Аккаунтқа тіркелген телефон нөмірін көрсетіңіз.
4. Соманы енгізіңіз. Дайын!
"""
    REFUND = """
💸     Ақшаны қайтару    
Өтінішті сілтеме арқылы толтырыңыз: https://qasqir.kz/support/refund

⚠️Маңызды:    
1. Карта нөмірін жазбаңыз! IBAN шотты (KZ...) көрсетіңіз.
2. Жеке куәлікті тіркеңіз.
Орындалу мерзімі: ~3 жұмыс күні.
"""

    # 4. Магазин
    RFID = """
💳Qasqir RFID-картасы (2500 ₸)
Қосымшасыз қуаттаңыз! Картаны тигізсеңіз болғаны.

📹Бейне-мысалдар:    
• AC: https://www.instagram.com/reel/DFC_DsMCDO3/
• GB/T: https://www.instagram.com/reel/DE7gjk5CRl9/
• CCS2: https://www.instagram.com/reel/DE4u0nuiSZZ/

Сатып алғыңыз келе ме? "Менеджерді шақыру" түймесін басыңыз.
"""
    HOME_STATION = """
🏠Үйге арналған қуаттау станциялары    
Біз AC станцияларын (7, 11, 22 кВт) сатамыз және орнатамыз.
Батареяның "денсаулығы" үшін айына кемінде 1 рет баяу станцияларда қуаттауды ұсынамыз.
"""

    # AI и Финал
    AI_START = """
🤖Виртуальный көмекші    
Мәселеңізді бір хабарламамен сипаттаңыз. Мен білім қорынан жауап іздеймін.
Егер жауап бере алмасам, адамды шақырамын.  
"""
    MANAGER_WAIT = "Ақпарат операторға берілді. Жауап күтіңіз."
    GOODBYE = "Көмектескеніме қуаныштымын! Жолыңыз болсын! 🚗💨"

    # КНОПКИ (ПЕРЕВОД)
    BUTTONS = {
        ButtonIDs.LANG_RU: "🇷🇺 Русский",
        ButtonIDs.LANG_KZ: "🇰🇿 Қазақша",

        # КАТЕГОРИИ
        ButtonIDs.CAT_CHARGE: "⚡ Қуаттау",
        ButtonIDs.CAT_SERVICE: "🛒 Сервистер",
        ButtonIDs.CAT_HELP:    "🤖 Көмек",

        ButtonIDs.MAIN_PROBLEM: "🆘Қуаттамай тұр",
        ButtonIDs.MAIN_PAYMENT: "💳Төлем / Баланс",
        ButtonIDs.MAIN_STORE: "🛒Дүкен",
        ButtonIDs.MAIN_APP: "📱Қосымшаны жүктеу",
        ButtonIDs.MAIN_MANAGER: "📞Менеджер",
        ButtonIDs.MAIN_AI_HELP: "🤖AI Көмекші",

        ButtonIDs.PROB_BATTERY: "🔋Қуат аз (<7%)",
        ButtonIDs.PROB_VIDEO: "📹Қалай қолдану керек?",
        ButtonIDs.PROB_OTHER: "⚠️Басқа қате",

        ButtonIDs.PAY_KASPI: "🏦Kaspi (комиссиясыз)",
        ButtonIDs.PAY_REFUND: "💸Ақша қайтару",

        ButtonIDs.STORE_RFID: "💳RFID Карта",
        ButtonIDs.STORE_HOME: "🏠Үйге арналған станция",

        ButtonIDs.BACK: "🔙Артқа",
        ButtonIDs.FINISH: "✅Рахмет, болды",
    }

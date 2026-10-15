"""All visible text of octopustms.com, in English and Russian.

Edit here, then run `python3 src/build.py` from the repo root. The build writes
index.html (English) and ru/index.html (Russian) from the same template, and
embeds both dictionaries so the flag toggle switches language without a reload.

Values may contain inline HTML (<em>, <b>, <span class="hl">). Keep every claim
here true — this file is the source of truth for what the site promises.
"""

REGISTER_URL = "https://app.octopustms.com/register"
DEMO_URL = "https://cal.com/digital-ronin/15min"
CONTACT_EMAIL = "ask@octopustms.com"
SITE = "https://octopustms.com"

# The eight stops of the lifecycle, in order. "paid" is the lit stop; "archived" is drawn dimmer.
STAGES = ["found", "booked", "dispatched", "moving", "delivered", "proven", "paid", "archived"]

EN = {
    "meta": {
        "title": "LLMP — Load Lifecycle Management and Payments | Octopus TMS",
        "description": "Octopus TMS keeps one record for every load: found, booked, dispatched, moving, delivered, proven, paid, archived. $20 per load. No subscription. No seats. No load, no fee.",
        "og_title": "LLMP — Load Lifecycle Management and Payments",
        "og_description": "From the moment a load is born to the moment you hear cha-ching. One platform. One record. Every step. $20 per load — no load, no fee.",
    },
    "ui": {
        "brand": "Octopus TMS",
        "demo": "Book a 15-min demo",
        "start": "Start free",
        "theme": "Switch light / dark mode",
        "footer_rights": "© 2026 Digital Ronin LLC",
        "privacy": "Privacy",
        "terms": "Terms",
        "payment_terms": "Payment terms",
        "refund_policy": "Refund policy",
    },
    "hero": {
        "h1": "LLMP",
        "h3": "Load Lifecycle Management and Payments",
        "sub": "From the moment a load is born to the moment you hear <em>cha-ching.</em> One platform. One record. Every step.",
        "motto": "We don't eat unless you eat.",
        "price": "<b>$20 per load.</b> No subscription. No seats. No load, no fee.",
    },
    "life": {
        "eyebrow": "THE LIFECYCLE",
        "chain": "Found → Booked → Dispatched → Moving → Delivered → Proven → Paid → Archived",
        "chaching": "cha-ching",
        "found": ["Found", "DAT and 123Loadboard results in under a second, ranked the way a dispatcher thinks: deadhead first, then rate, broker rating and payment terms."],
        "booked": ["Booked", "one click to call or message the broker."],
        "dispatched": ["Dispatched", "the driver gets the load in his app and sees the real rate con. Nothing hidden."],
        "moving": ["Moving", "live tracking, with one tracking link for the broker. No check calls."],
        "delivered": ["Delivered", "documents arrive at the load's own email address, attach themselves, and are read by AI."],
        "proven": ["Proven", "the POD, the verified driver and the location become one payment-confidence score."],
        "paid": ["Paid", "settlements calculated, the factoring package sent, the invoice synced. Then one sound, the only sound Octopus makes."],
        "archived": ["Archived", "one complete record, kept forever."],
    },
    "why": {
        "eyebrow": "WHY IT EXISTS",
        "p1": "3 AM, past Flagstaff, twenty tons behind me. A herd of deer was running alongside the truck, and I floored it. I came to at 82 mph. There were no deer.",
        "p2": "Weeks later, on another highway, I passed a crash. The driver stood by his cab with his hands on his head.",
        "p3": "You can be legal on paper and exhausted one hour after you wake up, with 12 hours left on your logbook. The logbook measures hours. It doesn't measure the man. And nobody in the chain — not the broker, not the carrier, not the state — could see who was behind that wheel.",
        "p4": "We don't need more laws. We need visibility.",
        "sonar": "Octopus is sonar for a blind industry.",
    },
    "sasr": {
        "eyebrow": "SECURITY",
        "title": "SASR",
        "full": "(Strict Access Security Rule)",
        "r1": "Only phones approved by the owner can enter.",
        "r2": "Only the assigned driver's phone, unlocked by his face, can accept the load.",
        "r3": "Add a new face to the phone and its key destroys itself.",
        "close": "Security and money are the same problem: <span class=\"hl\">whoever sees the whole load gets paid fast, and nobody can steal it.</span>",
    },
    "std": {
        "eyebrow": "THE STANDARD",
        "h2": "LLMP isn't a feature.",
        "p": "It's how every load should live: one unbreakable record of load, truck, driver and documents. Today it's for carriers. Tomorrow, an inspector types one plate number and sees everything connected to it.",
        "load": "Load",
        "truck": "Truck",
        "driver": "Driver",
        "docs": "Documents",
        "aria": "One plate number, TX 4821 KJ, connects to the load, the truck, the verified driver and the documents.",
    },
    "end": {
        "byline": "Built by a driver who slept in the cab, for carriers the software industry forgot.",
    },
}

RU = {
    "meta": {
        "title": "LLMP — управление жизненным циклом груза и платежами | Octopus TMS",
        "description": "Octopus TMS ведёт одну запись на каждый груз: найден, забронирован, отправлен, в пути, доставлен, подтверждён, оплачен, в архиве. $20 за груз. Без подписки. Без платы за пользователей. Нет груза — нет платы.",
        "og_title": "LLMP — управление жизненным циклом груза и платежами",
        "og_description": "С момента, когда груз появился, до момента, когда звучит «дзынь». Одна платформа. Одна запись. Каждый шаг. $20 за груз — нет груза, нет платы.",
    },
    "ui": {
        "brand": "Octopus TMS",
        "demo": "Демо за 15 минут",
        "start": "Начать бесплатно",
        "theme": "Переключить светлую / тёмную тему",
        "footer_rights": "© 2026 Digital Ronin LLC",
        "privacy": "Конфиденциальность",
        "terms": "Условия",
        "payment_terms": "Оплата",
        "refund_policy": "Возвраты",
    },
    "hero": {
        "h1": "LLMP",
        "h3": "Управление жизненным циклом груза и платежами",
        "sub": "С момента, когда груз появился, до момента, когда вы слышите <em>«дзынь».</em> Одна платформа. Одна запись. Каждый шаг.",
        "motto": "Мы не едим, пока не поели вы.",
        "price": "<b>$20 за груз.</b> Без подписки. Без платы за пользователей. Нет груза — нет платы.",
    },
    "life": {
        "eyebrow": "ЖИЗНЕННЫЙ ЦИКЛ",
        "chain": "Найден → Забронирован → Отправлен → В пути → Доставлен → Подтверждён → Оплачен → В архиве",
        "chaching": "дзынь",
        "found": ["Найден", "результаты DAT и 123Loadboard меньше чем за секунду, в том порядке, в каком думает диспетчер: сначала порожний пробег, затем ставка, рейтинг брокера и условия оплаты."],
        "booked": ["Забронирован", "один клик — и вы звоните или пишете брокеру."],
        "dispatched": ["Отправлен", "водитель получает груз в своём приложении и видит настоящий rate con. Ничего не скрыто."],
        "moving": ["В пути", "трекинг в реальном времени и одна ссылка для брокера. Никаких звонков «где груз?»."],
        "delivered": ["Доставлен", "документы приходят на собственный email груза, прикрепляются сами и читаются ИИ."],
        "proven": ["Подтверждён", "POD, проверенный водитель и геолокация складываются в одну оценку надёжности оплаты."],
        "paid": ["Оплачен", "расчёты посчитаны, пакет для факторинга отправлен, счёт синхронизирован. И один звук — единственный звук, который издаёт Octopus."],
        "archived": ["В архиве", "одна полная запись, навсегда."],
    },
    "why": {
        "eyebrow": "ЗАЧЕМ ЭТО НУЖНО",
        "p1": "3 часа ночи, за Флагстаффом, двадцать тонн за спиной. Рядом с грузовиком бежало стадо оленей, и я вдавил газ в пол. Очнулся на 82 милях в час. Никаких оленей не было.",
        "p2": "Через несколько недель, на другом шоссе, я проехал мимо аварии. Водитель стоял у своей кабины, схватившись за голову.",
        "p3": "Можно быть чистым по бумагам и вымотанным через час после пробуждения, когда в логбуке ещё 12 часов. Логбук считает часы. Он не измеряет человека. И никто в цепочке — ни брокер, ни перевозчик, ни государство — не мог увидеть, кто сидит за этим рулём.",
        "p4": "Нам не нужно больше законов. Нам нужна видимость.",
        "sonar": "Octopus — сонар для слепой индустрии.",
    },
    "sasr": {
        "eyebrow": "БЕЗОПАСНОСТЬ",
        "title": "SASR",
        "full": "(правило строгого доступа)",
        "r1": "Войти могут только телефоны, одобренные владельцем.",
        "r2": "Принять груз может только телефон назначенного водителя, разблокированный его лицом.",
        "r3": "Добавьте в телефон новое лицо — и его ключ уничтожит себя сам.",
        "close": "Безопасность и деньги — одна и та же задача: <span class=\"hl\">тот, кто видит груз целиком, получает деньги быстро, и украсть их не может никто.</span>",
    },
    "std": {
        "eyebrow": "СТАНДАРТ",
        "h2": "LLMP — это не функция.",
        "p": "Так должен жить каждый груз: одна неразрушимая запись о грузе, грузовике, водителе и документах. Сегодня — для перевозчиков. Завтра инспектор введёт один номер и увидит всё, что с ним связано.",
        "load": "Груз",
        "truck": "Грузовик",
        "driver": "Водитель",
        "docs": "Документы",
        "aria": "Один номер, TX 4821 KJ, связывает груз, грузовик, проверенного водителя и документы.",
    },
    "end": {
        "byline": "Создано водителем, который спал в кабине, — для перевозчиков, о которых забыла индустрия софта.",
    },
}

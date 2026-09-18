"""All visible text of octopustms.com, in English and Russian.

Edit here, then run `python3 src/build.py` from the repo root. The build writes
index.html (English) and ru/index.html (Russian) from the same template, and
embeds both dictionaries so the flag toggle switches language without a reload.

Card bodies are HTML on purpose: that is the content shown when a card is
expanded. Keep every claim here true — this file is the source of truth for
what the site promises.
"""

REGISTER_URL = "https://app.octopustms.com/register"
DEMO_URL = "https://cal.com/digital-ronin/15min"
CONTACT_EMAIL = "ask@octopustms.com"
SITE = "https://octopustms.com"

EN = {
    "meta": {
        "title": "Free to Start TMS for Small Carriers — $20 Per Booked Load | Octopus TMS",
        "description": "Octopus TMS is free to start and charges $20 only when you book a load — refunded if the load falls through. DAT + 123Loadboard search, dispatch, tracking, documents, driver settlements and QuickBooks in one place. English and Russian.",
        "og_title": "Octopus TMS — Free to Start. $20 Per Booked Load.",
        "og_description": "The carrier's partner, not a subscription: find, book, track and get paid in one place. $20 per booked load, refunded if the load falls through.",
    },
    "ui": {
        "brand": "Octopus TMS",
        "lang_en": "English",
        "lang_ru": "Русский",
        "demo": "Book a 15-min demo",
        "start": "Start free",
        "open": "Read more",
        "close": "Close",
        "panel_cta": "Start free — no card needed",
        "panel_demo": "or talk to the founder for 15 minutes",
        "footer_rights": "© 2026 Digital Ronin LLC",
        "privacy": "Privacy",
        "terms": "Terms",
        "payment_terms": "Payment terms",
        "refund_policy": "Refund policy",
    },
    "hero": {
        "h1": "The TMS that wins when you win.",
        "sub": "Octopus TMS is your carrier partner, not a subscription — one place to find the load, book it, track it and get paid.",
        "q": "Is it free?",
        "a": "Yes. If you don't book a load, you don't pay. Octopus isn't built to make money without its partner — the carrier. $20 per booked load, refunded if the load falls through.",
    },
    "cards": {
        "free": {
            "eyebrow": "Pricing",
            "hook": "Is it really FREE though?!",
            "teaser": "Yes. Every feature, no card on file. You pay $20 for a load you book — and it comes back if the load dies before the truck moves.",
            "body": """
<h3>What free means here</h3>
<p>Register and use the whole platform — load search, dispatch, tracking, documents, invoices, settlements — with no card on file. The free plan covers one truck, one driver and up to 10 booked loads a month.</p>
<h3>When you grow: $20 per booked load</h3>
<p>Switch to the Partnership plan and everything is unlimited. You pay $20 the moment a load is created in Octopus. No monthly fee, no per-seat fee, no setup fee, no minimum.</p>
<h3>Refunded if the load falls through</h3>
<p>Cancel a load before the truck moves and the $20 comes back automatically — in full, every time, no ticket, no asking. Once the load is in transit, the fee is earned.</p>
<div class="compare">
  <div class="compare-item"><strong>Any subscription TMS</strong><span>A fixed fee every month — whether you moved 0 loads or 100.</span></div>
  <div class="compare-item is-us"><strong>Octopus</strong><span>$0 in a dead month. $20 × the loads you booked in a good one.</span></div>
</div>
<div class="callout"><strong>$600 in a month with Octopus</strong> means you booked 30 loads — roughly <strong>$75,000 of freight</strong> moved. A subscription doesn't know if you earned anything at all.</div>
<p class="motto">We don't eat until you eat.</p>
<p class="fine">The exact rules live in the <a href="{payment_terms_url}">Payment Terms</a> and the <a href="{refund_url}">Refund &amp; Cancellation Policy</a> — short, plain English.</p>
""",
        },
        "one": {
            "eyebrow": "One place",
            "hook": "Find. Book. Track. Get paid.",
            "teaser": "The whole life of a load — from the load board to the money in your account — without ever leaving Octopus.",
            "body": """
<p><em>Leaving</em> means a load board in one tab, a spreadsheet in another, a group chat with the drivers, a folder of BOL photos, an invoicing tool, and QuickBooks at the end of the month. Octopus is the one tab.</p>
<ol class="steps">
  <li><strong>Find</strong><span>Search DAT and 123Loadboard side by side — results in under a second.</span></li>
  <li><strong>Book</strong><span>Booking creates the load: broker, rate, stops, dates — no retyping.</span></li>
  <li><strong>Dispatch</strong><span>Assign the driver and the truck; the driver gets the load on their phone.</span></li>
  <li><strong>Track</strong><span>Live location from the driver's phone; the broker gets a link, not a phone call.</span></li>
  <li><strong>Paperwork</strong><span>BOL and POD photos uploaded from the road and read automatically.</span></li>
  <li><strong>Invoice</strong><span>The invoice is built from the load — send it to the broker or your factoring company.</span></li>
  <li><strong>Get paid</strong><span>Driver settlement calculated, QuickBooks in sync. Done.</span></li>
</ol>
""",
        },
        "boards": {
            "eyebrow": "Load boards",
            "hook": "Two load boards. One search. Under a second.",
            "teaser": "DAT and 123Loadboard, searched from inside Octopus — and the load you book is already in your system.",
            "body": """
<p>Connect your DAT and 123Loadboard accounts once. Search a lane, equipment and dates and both boards answer in under a second. Book, and the load is created for you — broker, rate and stops included. DAT match alerts stream in as new loads are posted.</p>
<ul class="checks">
  <li>Built on the official DAT and 123Loadboard APIs.</li>
  <li>One search form, both boards, one result list per board — no copy-pasting between tabs.</li>
  <li>From a search result to a dispatched load in a couple of clicks.</li>
</ul>
<p class="fine">You bring your own DAT / 123Loadboard subscription — Octopus connects to it. We don't resell load board access.</p>
""",
        },
        "track": {
            "eyebrow": "Tracking",
            "hook": "The driver's phone is the tracker.",
            "teaser": "No ELD wiring, no extra hardware. The driver opens Octopus on their phone; you and your broker see the truck move.",
            "body": """
<p>Your driver accepts the load on their phone, shares location while the load is moving, and uploads the BOL and the POD straight from the dock. You see every truck on one map. The broker gets a tracking link that shows the truck — not your driver's phone number.</p>
<ul class="checks">
  <li>Location sharing is the driver's choice, turned on for a load — never a silent tracker.</li>
  <li>No hardware to buy, install or wire. Any phone works.</li>
  <li>"Where's my truck?" becomes a link you send once.</li>
</ul>
""",
        },
        "paper": {
            "eyebrow": "Paperwork & money",
            "hook": "Paperwork that does itself.",
            "teaser": "Rate confirmations, BOLs and PODs get read automatically. Invoices, driver pay and QuickBooks follow from the load — not from retyping.",
            "body": """
<ul class="checks">
  <li><strong>Documents that read themselves.</strong> Upload a rate confirmation or a POD and Octopus reads it — broker, rate, stops and reference numbers land in the load.</li>
  <li><strong>Invoices from loads.</strong> One click; send it to the broker or hand it to your factoring company.</li>
  <li><strong>Driver settlements.</strong> Percentage of gross, per load, weekly, owner-operator or employee — calculated per load, paid the way you pay.</li>
  <li><strong>QuickBooks.</strong> Invoices go to QuickBooks; when they get paid there, Octopus knows.</li>
  <li><strong>Load record export.</strong> Everything about a load — documents, invoice, settlement, timeline — in one file for audits and disputes.</li>
  <li><strong>English and Russian, natively.</strong> Every screen, both languages.</li>
</ul>
""",
        },
        "founder": {
            "eyebrow": "Who built it",
            "hook": "Driver. Dispatcher. Engineer.",
            "teaser": "150,000 miles behind the wheel and years of dispatching before the first line of code. Every screen comes from a real day on the road.",
            "body": """
<img class="photo" src="{img_prefix}images/IMG_7073.webp" alt="Octopus truck at a truck stop" width="1200" height="670" loading="lazy">
<p>Octopus wasn't designed in a conference room. Its founder drove 150,000 miles as an owner-operator — from Charjou to Chicago — then dispatched trucks, then learned to build software, because nothing on the market treated a small carrier like a partner.</p>
<p>Every screen in Octopus exists because someone in this company has personally lived the 2&nbsp;AM "where's my load?" call, the Friday settlement scramble, and the software bill that arrived in a month with no freight. That's why the price is a share of the work — not rent on a tool.</p>
<div class="trust">
  <div><strong>2,000+</strong><span>automated tests before every release</span></div>
  <div><strong>Isolated</strong><span>each carrier's data, at the database level</span></div>
  <div><strong>Encrypted</strong><span>bank details and tax IDs at rest</span></div>
</div>
<p class="fine">Want to talk to the person who built it? <a href="{demo_url}">Book 15 minutes.</a></p>
""",
        },
    },
    "faq": {
        "q": "Is Octopus TMS free?",
        "a": "Yes. Octopus TMS is free to start: register with no card, one truck, one driver and up to 10 booked loads a month. On the Partnership plan you pay $20 per booked load with no monthly fee, and the $20 is refunded automatically if the load is cancelled before the truck moves.",
    },
}

RU = {
    "meta": {
        "title": "Бесплатная TMS для небольших перевозчиков — $20 за забронированный груз | Octopus TMS",
        "description": "Octopus TMS: старт бесплатный, $20 только за забронированный груз — с возвратом, если груз сорвался. Поиск по DAT и 123Loadboard, диспетчерская, трекинг, документы, расчёты с водителями и QuickBooks в одном месте. Русский и английский.",
        "og_title": "Octopus TMS — старт бесплатный. $20 за забронированный груз.",
        "og_description": "Партнёр перевозчика, а не подписка: найти, забронировать, отследить и получить деньги в одном месте. $20 за забронированный груз, возврат, если груз сорвался.",
    },
    "ui": {
        "brand": "Octopus TMS",
        "lang_en": "English",
        "lang_ru": "Русский",
        "demo": "Демо за 15 минут",
        "start": "Начать бесплатно",
        "open": "Подробнее",
        "close": "Закрыть",
        "panel_cta": "Начать бесплатно — карта не нужна",
        "panel_demo": "или 15 минут с основателем",
        "footer_rights": "© 2026 Digital Ronin LLC",
        "privacy": "Конфиденциальность",
        "terms": "Условия",
        "payment_terms": "Оплата",
        "refund_policy": "Возвраты",
    },
    "hero": {
        "h1": "TMS, которая выигрывает, когда выигрываете вы.",
        "sub": "Octopus TMS — партнёр перевозчика, а не подписка: одно место, где вы находите груз, бронируете, отслеживаете и получаете деньги.",
        "q": "Это бесплатно?",
        "a": "Да. Не забронировали груз — ничего не платите. Octopus не создан зарабатывать без своего партнёра — перевозчика. $20 за забронированный груз, и они возвращаются, если груз сорвался.",
    },
    "cards": {
        "free": {
            "eyebrow": "Цена",
            "hook": "А это точно БЕСПЛАТНО?!",
            "teaser": "Да. Все функции, без карты. $20 вы платите только за груз, который забронировали, — и они возвращаются, если груз сорвался до выезда.",
            "body": """
<h3>Что здесь значит «бесплатно»</h3>
<p>Регистрируетесь и пользуетесь всей платформой — поиск грузов, диспетчерская, трекинг, документы, счета, расчёты — без карты. Бесплатный план: один грузовик, один водитель и до 10 забронированных грузов в месяц.</p>
<h3>Когда вы растёте: $20 за забронированный груз</h3>
<p>Переходите на план «Партнёрство» — и всё без ограничений. $20 списываются в момент создания груза в Octopus. Ни ежемесячной платы, ни платы за пользователей, ни за подключение, ни минимума.</p>
<h3>Возврат, если груз сорвался</h3>
<p>Отмените груз до того, как грузовик тронулся, — и $20 вернутся автоматически: полностью, каждый раз, без заявок и просьб. Как только груз в пути, плата считается заработанной.</p>
<div class="compare">
  <div class="compare-item"><strong>Любая TMS по подписке</strong><span>Фиксированная сумма каждый месяц — перевезли вы 0 грузов или 100.</span></div>
  <div class="compare-item is-us"><strong>Octopus</strong><span>$0 в пустой месяц. $20 × число забронированных грузов в хороший.</span></div>
</div>
<div class="callout"><strong>$600 за месяц в Octopus</strong> означают, что вы забронировали 30 грузов — примерно <strong>$75 000 перевезённого фрахта</strong>. Подписке всё равно, заработали ли вы хоть что-нибудь.</div>
<p class="motto">Мы не едим, пока не поели вы.</p>
<p class="fine">Точные правила — в <a href="{payment_terms_url}">Условиях оплаты</a> и <a href="{refund_url}">Политике возвратов</a> (на английском, коротко и без юридического тумана).</p>
""",
        },
        "one": {
            "eyebrow": "Одно место",
            "hook": "Найти. Забронировать. Отследить. Получить деньги.",
            "teaser": "Вся жизнь груза — от доски грузов до денег на счёте — не выходя из Octopus.",
            "body": """
<p><em>Выйти</em> — это доска грузов в одной вкладке, таблица в другой, чат с водителями, папка с фото накладных, программа для счетов и QuickBooks в конце месяца. Octopus — одна вкладка.</p>
<ol class="steps">
  <li><strong>Найти</strong><span>Поиск по DAT и 123Loadboard рядом — результаты меньше чем за секунду.</span></li>
  <li><strong>Забронировать</strong><span>Бронирование создаёт груз: брокер, ставка, точки, даты — без перепечатывания.</span></li>
  <li><strong>Отправить</strong><span>Назначьте водителя и грузовик; водитель получает рейс на телефон.</span></li>
  <li><strong>Отследить</strong><span>Живая геолокация с телефона водителя; брокер получает ссылку, а не звонок.</span></li>
  <li><strong>Документы</strong><span>Фото BOL и POD загружаются с дороги и распознаются автоматически.</span></li>
  <li><strong>Выставить счёт</strong><span>Счёт собирается из груза — отправьте брокеру или в факторинговую компанию.</span></li>
  <li><strong>Получить деньги</strong><span>Расчёт с водителем посчитан, QuickBooks синхронизирован. Готово.</span></li>
</ol>
""",
        },
        "boards": {
            "eyebrow": "Доски грузов",
            "hook": "Две доски грузов. Один поиск. Меньше секунды.",
            "teaser": "DAT и 123Loadboard прямо внутри Octopus — а забронированный груз уже в вашей системе.",
            "body": """
<p>Подключите свои аккаунты DAT и 123Loadboard один раз. Задайте маршрут, тип прицепа и даты — обе доски ответят меньше чем за секунду. Бронируете — и груз создан за вас: брокер, ставка и точки уже на месте. Оповещения DAT о подходящих грузах приходят сразу, как только они появляются.</p>
<ul class="checks">
  <li>Работает на официальных API DAT и 123Loadboard.</li>
  <li>Одна форма поиска, обе доски, отдельный список результатов по каждой — без копирования между вкладками.</li>
  <li>От результата поиска до отправленного в рейс груза — пара кликов.</li>
</ul>
<p class="fine">Подписка на DAT / 123Loadboard — ваша собственная: Octopus подключается к ней. Мы не перепродаём доступ к доскам.</p>
""",
        },
        "track": {
            "eyebrow": "Трекинг",
            "hook": "Телефон водителя — и есть трекер.",
            "teaser": "Без проводов ELD и лишнего оборудования. Водитель открывает Octopus на телефоне — вы и брокер видите, как едет грузовик.",
            "body": """
<p>Водитель принимает рейс на телефоне, делится геолокацией, пока груз в пути, и загружает BOL и POD прямо с рампы. Вы видите все грузовики на одной карте. Брокер получает ссылку для отслеживания — видит грузовик, а не номер вашего водителя.</p>
<ul class="checks">
  <li>Геолокация — выбор водителя, включается на рейс. Никакого тайного трекера.</li>
  <li>Ничего не нужно покупать, ставить или подключать. Подходит любой телефон.</li>
  <li>«Где грузовик?» превращается в ссылку, которую вы отправляете один раз.</li>
</ul>
""",
        },
        "paper": {
            "eyebrow": "Документы и деньги",
            "hook": "Бумаги, которые делают себя сами.",
            "teaser": "Rate confirmation, BOL и POD распознаются сами. Счета, зарплата водителей и QuickBooks следуют из груза — без ручного ввода.",
            "body": """
<ul class="checks">
  <li><strong>Документы читают себя сами.</strong> Загрузите подтверждение ставки или POD — Octopus прочитает его: брокер, ставка, точки и номера попадут в груз.</li>
  <li><strong>Счета из грузов.</strong> Один клик — брокеру или в вашу факторинговую компанию.</li>
  <li><strong>Расчёты с водителями.</strong> Процент от гросса, за груз, понедельно, owner-operator или штатный водитель — считается по каждому грузу, платите как привыкли.</li>
  <li><strong>QuickBooks.</strong> Счета уходят в QuickBooks; когда их там оплатили, Octopus об этом знает.</li>
  <li><strong>Досье груза одним файлом.</strong> Всё о грузе — документы, счёт, расчёт, хронология — для проверок и споров.</li>
  <li><strong>Русский и английский — родные.</strong> Каждый экран, оба языка.</li>
</ul>
""",
        },
        "founder": {
            "eyebrow": "Кто это построил",
            "hook": "Водитель. Диспетчер. Инженер.",
            "teaser": "150 000 миль за рулём и годы в диспетчерской до первой строчки кода. Каждый экран — из реального дня на дороге.",
            "body": """
<img class="photo" src="{img_prefix}images/IMG_7073.webp" alt="Грузовик Octopus на стоянке" width="1200" height="670" loading="lazy">
<p>Octopus не придумали в переговорной. Основатель проехал 150 000 миль как owner-operator — от Чарджоу до Чикаго, — потом диспетчировал грузовики, потом научился писать софт, потому что ничего на рынке не относилось к небольшому перевозчику как к партнёру.</p>
<p>Каждый экран Octopus существует потому, что кто-то в компании лично пережил звонок в два часа ночи «где мой груз?», пятничную гонку с расчётами и счёт за софт, пришедший в месяц без фрахта. Поэтому цена — доля от работы, а не аренда инструмента.</p>
<div class="trust">
  <div><strong>2 000+</strong><span>автотестов перед каждым релизом</span></div>
  <div><strong>Изолированы</strong><span>данные каждого перевозчика — на уровне базы данных</span></div>
  <div><strong>Зашифрованы</strong><span>банковские реквизиты и налоговые номера</span></div>
</div>
<p class="fine">Хотите поговорить с тем, кто это построил? <a href="{demo_url}">15 минут — здесь.</a></p>
""",
        },
    },
    "faq": {
        "q": "Octopus TMS — это бесплатно?",
        "a": "Да. Старт бесплатный: регистрация без карты, один грузовик, один водитель и до 10 забронированных грузов в месяц. На плане «Партнёрство» вы платите $20 за забронированный груз без ежемесячной платы, и $20 возвращаются автоматически, если груз отменён до выезда.",
    },
}

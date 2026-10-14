# Выбор скиллов под задачу

Это маршруты, а не обязательная последовательность. Пропускать уже решённое; включать дополнительный модуль только если он нужен для результата. Полный каталог — [CATALOG_RU.md](../CATALOG_RU.md).

| Задача | Основные модули | Дополнительно |
|---|---|---|
| Лендинг с нуля | [product-marketing](modules/ru-product-marketing.md), [customer-research](modules/ru-customer-research.md), [offers](modules/ru-offers.md), [copywriting](modules/ru-copywriting.md), [cro](modules/ru-cro.md) | [frontend-design](modules/ru-frontend-design.md) после текстов для дизайна и реализации; analytics и seo-audit — по объёму запроса |
| Аудит существующего сайта | [cro](modules/ru-cro.md), [analytics](modules/ru-analytics.md) | copy-editing, seo-audit и ab-testing — по найденным проблемам |
| Позиционирование и предложение | [product-marketing](modules/ru-product-marketing.md), [customer-research](modules/ru-customer-research.md), [competitor-profiling](modules/ru-competitor-profiling.md), [offers](modules/ru-offers.md) | pricing — для цены и комплектации |
| Запуск или общий план | [marketing-plan](modules/ru-marketing-plan.md), [launch](modules/ru-launch.md) | Подключать только выбранные каналы и analytics |
| Платная реклама | [ads](modules/ru-ads.md), [ad-creative](modules/ru-ad-creative.md), [cro](modules/ru-cro.md), [analytics](modules/ru-analytics.md) | attribution — при оценке окупаемости |
| VK/Telegram и контент | [content-strategy](modules/ru-content-strategy.md), [social](modules/ru-social.md) | image, video, community-marketing — по формату |
| SEO и поиск с ИИ | [seo-audit](modules/ru-seo-audit.md), [site-architecture](modules/ru-site-architecture.md), [content-strategy](modules/ru-content-strategy.md) | schema, ai-seo, programmatic-seo — только по реальной задаче |
| Локальная услуга | [product-marketing](modules/ru-product-marketing.md), [offers](modules/ru-offers.md), [directory-submissions](modules/ru-directory-submissions.md), [cro](modules/ru-cro.md) | ads — при бюджете, co-marketing — при подходящем партнёре |
| Карточка товара/маркетплейс | [customer-research](modules/ru-customer-research.md), [competitor-profiling](modules/ru-competitor-profiling.md), [copywriting](modules/ru-copywriting.md), [image](modules/ru-image.md), [pricing](modules/ru-pricing.md) | Применить экономику маркетплейса из ru-context; analytics — по доступным данным |
| Подписка и приложение | [signup](modules/ru-signup.md), [onboarding](modules/ru-onboarding.md), [paywalls](modules/ru-paywalls.md), [churn-prevention](modules/ru-churn-prevention.md) | aso, pricing, emails — в зависимости от узкого места |
| B2B-продажи | [prospecting](modules/ru-prospecting.md), [sales-enablement](modules/ru-sales-enablement.md), [revops](modules/ru-revops.md) | cold-email — для разрешённого делового обращения |
| Письма и повторные покупки | [emails](modules/ru-emails.md), [churn-prevention](modules/ru-churn-prevention.md) | sms, referrals — при подходящем сценарии |
| Лид-магнит/калькулятор | [lead-magnets](modules/ru-lead-magnets.md), [free-tools](modules/ru-free-tools.md), [cro](modules/ru-cro.md) | emails и analytics — для согласованной выдачи и измерения |
| Партнёры, медиа, события | [co-marketing](modules/ru-co-marketing.md), [public-relations](modules/ru-public-relations.md), [events](modules/ru-events.md) | influencer-marketing — для работы с авторами |
| Проверка гипотезы | [ab-testing](modules/ru-ab-testing.md), [analytics](modules/ru-analytics.md) | marketing-council/marketing-psychology — если нужны разные подходы |
| Регулярная работа | [marketing-loops](modules/ru-marketing-loops.md) | Добавить предметный скилл процесса; расписание создавать только при поручении |
| Дизайн, вёрстка или редизайн | [frontend-design](modules/ru-frontend-design.md) | Сохранить согласованные оффер и тексты; cro — для проверки пути к действию |


## Проверка реализации

| Задача | Модуль | Граница |
|---|---|---|
| Технический аудит UI | [52: web-design-audit](modules/ru-web-design-audit.md) | Находки с доказательствами и приоритетами; CRO — отдельно |
| Работают ли кнопки и форма | [53: webapp-testing](modules/ru-webapp-testing.md) | Выполнение в браузере либо честно обозначенный план без инструментов |
| Доработать готовый внешний вид / мобильную версию | [54: design-polish](modules/ru-design-polish.md) | Исправления внутри текущего стиля; новый стиль — модуль 51 |

Для полного лендинга после реализации: проверить UI → пройти главный сценарий → исправить существенные дефекты → повторить затронутые проверки. Если проверка уже выполнена в модуле 51, использовать её результаты. Только стратегия/тексты не запускают технические процедуры. В Tilda без кода опираться на доступный редактор/страницу и честно ограничивать выводы.


## Дополнительные результаты
| Задача | Процедура |
|---|---|
| Точная серия по фото | [Карточки товара](modules/ru-product-cards.md) |
| Правки изображения | [Изображения](modules/ru-image-production.md) |
| Связанные видеосцены | [Раскадровка](modules/ru-storyboard.md) |
| Монтаж готовых файлов | [Монтаж](modules/ru-media-editing.md) |
| Анимация из кода | [Remotion](modules/ru-remotion.md) |
| Бот или приложение | [Python](modules/ru-python-bot.md), [API](modules/ru-api-integration.md) |
| Данные и сервер | [База](modules/ru-database.md), [Деплой](modules/ru-docker-deploy.md) |
| Документ и расчёт | [Документы](modules/ru-document-check.md), [Таблицы](modules/ru-spreadsheet-economics.md) |
| Сравнить модели или навыки | [Оценка](modules/ru-model-evaluation.md) |
| Проверить вероятностную модель | [Прогнозы](modules/ru-probabilistic-review.md) |

## Tg_bot ##

Это бот для проведения викторин. Подробно останавливаться на интерфейсе не вижу смысла, потому что тут всё очевидно. 

https://t.me/quzzz_bot

![Telegram_kpTvqaE1Yc](https://github.com/nikitakomissarov/quiz_bot/assets/59535117/be29cc2b-a9a3-41c1-a188-e579377890a9)


В этом же проекте есть logger — бот, который подхватывает ошибки (если они возникнут) и отправляет их в Телеграме тому пользователю, чей id будет указан в качестве id для отправки сообщений. 

Чтобы ими пользоваться, нужно:
1. Создать 2 ботов: один непосредственно tg_bot, второй — бот для логирования ошибок logger. 
2. Скачать этот репозиторий и установить requirements.txt:
``` C:\Users\big shot>git clone https://github.com/nikitakomissarov/quiz_bot
C:\Users\big shot>cd bots
C:\Users\big shot\bots>python  -m venv env
C:\Users\big shot\bots>env\Scripts\activate.bat
(env) C:\Users\big shot\bots>pip install -r requirements.txt
``` 
3. Создать каталог вопросов через set_creator.py.
4. Подключить переменные для tg_bot в .env, где TG_TOKEN — токен для бота в Телеграме, QUIZ_FILE — ваши вопросы в формате JSON.
5. Подключить logger.py для подхватывания ошибок: в .env указываем переменные, где TG_CHAT_ID — id пользователя, которому будут отправляться ошибки, TG_LOGGER_TOKEN — токен бота, который вы создавали в пункте 1. 
6. Наконец, запускаем:
```
(env) C:\Users\big shot\bots>python tg_bot.py
```

## Vk_bot ##
Это бот для проведения викторин. Подробно останавливаться на интерфейсе не вижу смысла, потому что тут всё очевидно.

https://vk.com/club219472973

![opera_pn3EPEUY9d](https://github.com/nikitakomissarov/quiz_bot/assets/59535117/4fd6aa86-af28-47f0-96c4-d923e8bf53f5)

В этом же проекте есть logger — бот, который подхватывает ошибки (если они возникнут) и отправляет их в Телеграме тому пользователю, чей id будет указан в качестве id для отправки сообщений.
Чтобы ими пользоваться, нужно:
1. Создать группу ВК и получить токен для API, а также бот в Телеграме для логирования ошибок logger. 
2. Повторить пункт 2 из Tg_bot.
3. Повторить пункт 3 из Tg_bot.
4. Подключить переменные для vk_bot в .env, где VK_TOKEN — токен для доступа к API из настроек группы ВК, QUIZ_FILE — ваши вопросы в формате JSON.
5. Повторить пункт 6 из Tg_bot.
6. Наконец, запускаем:
```
(env) C:\Users\big shot\bots>python vk_bot.py
```
## Set_creator ##
Этот скрипт создает сет quiz_file.json вопросов из пресетов для использования в упомянутых выше ботах. 

Чтобы начать им пользоваться, необходимо при запуске кода указать путь к папке, где у вас лежат пресеты, которые нужно обработать. 

Запуск:
```
(env) C:\Users\big shot\bots>python set_creator.py -f C:\Users\user\Documents\GitHub\quiz_bot\quiz_files
```


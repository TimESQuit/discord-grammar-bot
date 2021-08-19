# discord-grammar-bot


This bot was built using Discord.py and uses [LanguageTool](https://languagetool.org/dev) (LT) in [Dockerized](https://github.com/Erikvl87/docker-languagetool) form.

### Features

* Listens to all user messages. If ```your``` is present, it will ask LT if it was used incorrectly, and if so, sends a reply correcting the original user message.
* ```gb!leaders``` shows a "leaders" table, tracking total errors. This table is kept presistent with SQLite.
* The leaders table notes users' nicknames and if necessary, automatically updates a nickname when it records the next error. ```gb!updatenicks``` can be used to force update nicknames.
* ```gb!fixme {message_id}``` asks LT if there are any grammatical or spelling errors (not just "your") and sends a reply with each suggested fix.

## Demo

https://user-images.githubusercontent.com/55008059/130125317-6ef22fc4-e636-4798-8802-79a49bc943cb.mp4


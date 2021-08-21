# api_sp1_bot
### Бот получения погоды 
#### Возможности:
* команда /weathernow {город} вернет текущюю погоду в городе
* команда /start выбор запускает меню с выбором погоды в разных городах, после выбора города нужно выбрать время от 3 часов до 5 суток в часах с шагом в 3 часа
* команда /vacation показывает сколько мне осталось до отпуска)))

###Как запустить проект:
```
git clone https://github.com/EugeneSal/api_my_bot1.git
```
Cоздать и активировать виртуальное окружение:
```
python -m venv env

source venv/bin/activate
```
обновить pip
```
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt

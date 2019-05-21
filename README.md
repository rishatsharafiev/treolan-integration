# treolan-integration

### Установка зависимостей
- https://beget.com/ru/articles/webapp_main
- https://beget.com/ru/articles/webapp_python

Python3
```
ssh localhost -p222
wet https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tar.xz
tar xf Python-3.6.8.tar.xz && cd Python-3.6.8
./configure --prefix $HOME/.local
make -j33 && make install
```

requirements.txt
```
ssh localhost -p222
pip3 install -r requirements.txt --user --ignore-installed
```

### Настройка crontab
см. beget

### Вирутальное окружение
Создание
```
virtualenv venv -p python3
```

Активация
```
. venv/bin/activate
```

Деактивация
```
deactivate
```

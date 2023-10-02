# Проект парсинга товаров с сайта maksavit.ru.

### Описание

Проект Парсера написанного на scrapy, собирающего данные о документах товарах с сайта по категориям.
В проекте присутствует возможность как парсить лишь одну категорию товара так и несколько, инструкция по применению далее.

## Stack

Python 3.11, Scrapy 2.11.0

### Установка, Как запустить проект:
https://github.com/Alex386386/brand_scrapy_parser
Клонировать репозиторий и перейти в него в командной строке:

```
git@github.com:Alex386386/brand_scrapy_parser.git
```

```
cd brand_scrapy_parser
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Для обновления списка категорий товаров, введите:

```
scrapy crawl scrapy crawl category
```

Для парсинга товаров по категориям, введите команду вида:

```
scrapy crawl product_info_spider -a categories="{name_of_category}"
```

Для парсинга нескольких категорий вводите их внутри кавычек, разделя знаком ";", пример:

```
scrapy crawl product_info_spider -a categories="{name_of_category};{name_of_category}"
```

Регистр значения не имеет.

Автор:
- [Александр Мамонов](https://github.com/Alex386386) 
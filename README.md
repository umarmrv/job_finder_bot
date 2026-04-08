### 1. Клонировать репозиторий

`bash
git clone <your-repo-url>
cd <project-folder>

Создать виртуальное окружение

python -m venv venv

Активировать:

Windows:

Set-ExecutionPolicy Unrestricted -Scope Process
venv\Scripts\activate

Linux / Mac:

source venv/bin/activate

3. Установить зависимости

pip install -r requirements.txt

4. Настроить .env

Создай файл .env и скопируй туда содержимое из .env.example:

cp .env.example .env

Отредактируй значения под себя (особенно DATABASE_URL).

▶️ Запуск проекта

uvicorn main:app --reload
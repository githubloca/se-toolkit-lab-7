FROM python:3.12-slim

WORKDIR /app

# Устанавливаем uv
RUN pip install uv

# Копируем только нужное
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --frozen

# Копируем весь код
COPY . .

# Запуск бота
CMD ["uv", "run", "bot.py"]

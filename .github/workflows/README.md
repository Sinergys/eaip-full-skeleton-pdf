# GitHub Actions Workflows

## Docker Build & Publish

Автоматическая сборка и публикация Docker образов при каждом push в `main` и при создании тегов версий.

### Триггеры

- Push в ветку `main`
- Создание тега формата `v*.*.*` (например, `v0.2.0`)
- Ручной запуск через `workflow_dispatch`

### Собираемые сервисы

- `gateway-auth`
- `ingest`
- `validate`
- `analytics`
- `recommend`
- `reports`
- `management`

### Теги образов

При создании тега `v0.2.0`:
- `ecosinergys/eaip-full-skeleton-{service}:v0.2.0`
- `ecosinergys/eaip-full-skeleton-{service}:latest`

При push в `main`:
- `ecosinergys/eaip-full-skeleton-{service}:latest`
- `ecosinergys/eaip-full-skeleton-{service}:{short-sha}`

### Настройка секретов

Для работы workflow необходимо настроить секреты в GitHub:

1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте следующие секреты:

   - **DOCKERHUB_USERNAME** - ваш Docker Hub username (например, `ecosinergys`)
   - **DOCKERHUB_TOKEN** - Docker Hub Access Token

#### Как получить Docker Hub Token:

1. Войдите на https://hub.docker.com
2. Перейдите в Account Settings → Security → New Access Token
3. Создайте токен с правами **Read, Write, Delete**
4. Скопируйте токен и добавьте в GitHub Secrets как `DOCKERHUB_TOKEN`

### Оптимизация

- Workflow пропускает сборку, если нет изменений в Dockerfile или docker-compose.yml
- Используется кэширование через GitHub Actions Cache для ускорения сборок
- Параллельная сборка всех сервисов через matrix strategy

### Пример использования

После создания тега `v0.2.0`:

```bash
git tag v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

Workflow автоматически:
1. Определит изменения
2. Соберет все 7 образов
3. Опубликует их на Docker Hub с тегами `v0.2.0` и `latest`

### Просмотр результатов

После выполнения workflow:
- Все образы будут доступны на Docker Hub: https://hub.docker.com/u/ecosinergys
- В summary workflow будет список опубликованных образов


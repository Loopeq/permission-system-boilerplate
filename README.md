# permission-system-boilerplate

## Запуск проекта
```
  mv .env.example .env
  docker compose up --build
```
## Архитектура системы прав доступа
<img width="1017" height="768" alt="image" src="https://github.com/user-attachments/assets/3f2bf3af-3d66-4b12-9b49-edb1f037aa31" />

Управление прав доступа основано на механизме Permission-Based Access Control

Код права хранится в формате resourse:action (например, document:read)

Связь между пользователями и правами хранится в таблице ```user_permissions```

### Логика проверки права доступа

1. Аутентификация пользователя (проверка JWT-токена)
2. Проверка ```is_active``` пользователя (в случае мягкого удаления)
3. Проверка права доступа на ресурс, например

```
GET /documents                  требует document:read
POST /documents                 требует document:create
DELETE /documents/{id}          требует document:delete
```

### Права администратора

Управлением прав доступа может занимать ```user``` с ролью ```admin``` (```user.role = admin```)

1. Получить доступные права доступа
2. Создать новое право доступа
3. Посмотреть права доступа пользователя
4. Выдать право доступа пользователю
5. Отозвать право доступа у пользователя

# Back-end

## Install and configure

Install python dependencies:

```bash
pip install -r requirments.txt
```

Then edit the ```.env``` file and provide following values

| Key name          | Description                                                          |
|-------------------|----------------------------------------------------------------------|
| OPENAI_API_KEY    | OpenAI API key (create [hier](https://platform.openai.com/api-keys)) |
| GOOGLE_API_KEY    | Google (gemini) API key                                              |
| ANTHROPIC_API_KEY | Anthropic (claude) API key                                           |                                           

## Starting server

To start a web-server just run:

```bash
python main.py
```

Then access the server on http://localhost:8080/

## API routes

Note: all input/output parameters are passed as a JSON object with the fields specified below.

**API routes table**

| Route          | Description                        | Method     |
|----------------|------------------------------------|------------|
| /auth/register | New user registration              | ```POST``` |
| /auth/login    | Log-in user                        | ```POST``` |
| /auth/logout   | Log-out user                       | ```GET```  |
| /chat/list     | Get list of user's chats           | ```GET```  |
| /chat/create   | Create a new chat                  | ```POST``` |
| /chat/edit     | Edit chat settings                 | ```POST``` |
| /chat/delete   | Delete chat                        | ```POST``` |
| /chat/get      | Loading chat and get history       | ```POST``` |
| /chat/send     | Send chat message to the LLM model | ```POST``` |
| /models/list   | Get list of available LLM models   | ```GET```  |

### ```POST /auth/register```

Register a new user

#### Request

```json
{
  "name": [First/last name of the user],
  "username": [User name (login)],
  "password": [User password]
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")]
}
```

### ```POST /auth/login```

Log-in an existed user

#### Request

```json
{
  "username": [User login],
  "password": [User password],
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")]
}
```

### ```GET /auth/logout```

Log-out logged user

#### Request

```json
-
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")]
}
```

### ```GET /chat/list```

Get list of user's chats

#### Request

```json
-
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")],
  "chats": [
    {
      "id": [Chat ID],
      "title": [Chat title],
    },
    {
      "id": [Chat ID],
      "title": [Chat title],
    },
    ...
  ]
}
```

### ```POST /chat/create```

Create a new user chat

#### Request

```json
{
  "title": [New chat title]
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")]
}
```

### ```POST /chat/edit```

Change chat title

#### Request

```json
{
  "chat_id": [ID of the chat to edit title],
  "title": [New chat title],
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")]
}
```

### ```POST /chat/delete```

Delete an existed user chat

#### Request

```json
{
  "chat_id": [ID of the chat to delete]
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")]
}
```

### ```POST /chat/get```

Loading chat and get history

#### Request

```json
{
  "chat_id": [ID of the chat to loading]
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")],
  "id": [Chat ID],
  "title": [Chat title],
  "messages": [
    {
      "role": [Message role (user, assistant or system)],
      "message": [Message content]
    },
    {
      "role": [Message role (user, assistant or system)],
      "message": [Message content],
    },
    ...
  ]
}
```

### ```POST /chat/send```

Send a message to the selected LLM model

#### Request

```json
{
  "model_id": [ID of the model to use],
  "message": [User message to send]
}
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")],
  "response": [Model response]
}
```

### ```GET /models/list```

Returns list of available LLM models

#### Request

```json
-
```

#### Response

```json
{
  "status": ["ok" or "error"],
  "error": [Error description (if status == "error")],
  "models": [
    {
      "id": [Model ID],
      "provider": [Model provider (openai, google etc.)],
      "model": [LLM model name]
    },
    {
      "id": [Model ID],
      "provider": [Model provider (openai, google etc.)],
      "model": [LLM model name]
    },
    ...
  ]
}
```

## Database structure

### Table ```users```

| Field name           | Type           | Description              | Required |
|----------------------|----------------|--------------------------|----------|
| ```id```             | ```INTEGER```  | Unique user ID           | Yes      |
| ```name```           | ```TEXT```     | User first and last name | No       |
| ```username```       | ```TEXT```     | User login               | Yes      |
| ```password```       | ```TEXT```     | Password hash (SHA256)   | Yes      |
| ```role```           | ```INTEGER```  | Role code (?)            | No       |
| ```permissions_id``` | ```INTEGER```  | Permission ID            | No       |

### Table ```chats```

| Field name    | Type          | Description      | Required |
|---------------|---------------|------------------|----------|
| ```id```      | ```INTEGER``` | Unique chat ID   | Yes      |
| ```user_id``` | ```INTEGER``` | ID of the user   | Yes      |
| ```title```   | ```TEXT```    | Chat title       | No       |

### Table ```chat_messages```

| Field name    | Type          | Description                                                | Required |
|---------------|---------------|------------------------------------------------------------|----------|
| ```id```      | ```INTEGER``` | ID of the chat message                                     | Yes      |
| ```chat_id``` | ```INTEGER``` | ID of the chat                                             | Yes      |
| ```message``` | ```TEXT```    | Message text                                               | No       |
| ```role```    | ```TEXT```    | Message role (```user```, ```assistant``` or ```system```) | Yes      |
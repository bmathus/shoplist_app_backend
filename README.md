# Shopping List API

A RESTful API backend for a collaborative shopping list mobile application. In this this users can manage shopping lists, products within lists, join lists via invite codes, and even initiate call between 2 users. The API is built using Django and Django REST Framework, leveraging token-based authentication for secure access.

## Features

- **User Authentication**: Token-based authentication using a custom endpoint (`/auth-user`) - only login
- **Shopping List Management**: Create, view, and delete shopping lists.
- **Product Management**: Add, update, and remove products within shopping lists.
- **List Sharing**: Join a shopping list with a valid invite code.
- **Call Functionality**: Create and manage call rooms between users.
- **Image Support**: Product images handled as base64 strings and stored/referenced via a JSON file.

## Tech Stack

- Python 3.9
- Django 4.0.3
- Django REST Framework 3.13.1
- PostgreSQL
- Docker (optional for running PostgreSQL)
- Token Authentication

## API Endpoints

- `POST /auth-user`: Authenticate a user (requires email and password) and return user details along with an authentication token.
- `GET /lists`: Retrieve all shopping lists associated with the authenticated user.
- `POST /lists`: Create a new shopping list with a provided name; generates a unique invite code and associates the list with the user.
- `GET /list/{list_id}`: Retrieve details (including products) of the specified shopping list.
- `DELETE /list/{list_id}`: Remove the authenticated user from the list; if the user is the only participant, delete the list.
- `PUT /list/{list_id}/product/{id}`: Update a product's details (name, quantity, unit, bought status, and optional base64 image) in a shopping list.
- `DELETE /list/{list_id}/product/{id}`: Delete a specific product from the shopping list.
- `POST /list/{list_id}/product`: Add a new product to the given shopping list with details such as name, quantity, unit, and optional image.
- `POST /list/invite`: Join an existing shopping list by providing a valid invite code in the request body.
- `GET /list/{list_id}/participants`: Retrieve the list of users participating in the specified shopping list.
- `DELETE /call/end`: End an ongoing call session by clearing the call room data for the authenticated user.

## Authentication Header

After obtaining the token via the `/auth-user` endpoint, include it in the header of subsequent requests:

```
Authorization: Token <your-auth-token>
```

## Getting Started

### Prerequisites

- Python 3.9 installed locally.
- A PostgreSQL server ready for use. You can also use Docker to run a PostgreSQL container:

  ```bash
  docker run --name shopping-list-db \
    -e POSTGRES_DB=shopping_db \
    -e POSTGRES_USER=shopping_user \
    -e POSTGRES_PASSWORD=shopping_password \
    -p 5432:5432 \
    -d postgres:13
  ```

### Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   # On Linux/Mac:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the project root with the following content:

   ```env
   DB_NAME=shopping_db
   DB_USER=shopping_user
   DB_PASS=shopping_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

6. **(Optional) Create a Superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**

   ```bash
   python manage.py runserver
   ```

   The API will be accessible at `http://127.0.0.1:8000/`.

## Contact

For further information or any questions regarding the API, please contact [me](mailto:bojko.matus@gmail.com).

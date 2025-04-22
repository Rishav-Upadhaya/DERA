# DERA - Property Rental Platform

DERA is a property rental platform that allows users to list, rent, and manage properties. It provides features such as property listing, booking requests, chat functionality, and favorites management.

## Features

- **Property Listing**: Users can add, view, edit, and delete properties.
- **Booking Requests**: Users can send and manage booking requests for properties.
- **Favorites**: Users can mark properties as favorites for quick access.
- **Chat System**: Integrated chat functionality for communication between property owners and renters.
- **Responsive Design**: Fully responsive UI for seamless usage across devices.

## Tech Stack

- **Backend**: Django, Django Channels
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default, can be replaced with other databases)
- **WebSocket**: Real-time communication using Django Channels
- **AI Integration**: OpenAI-powered chatbot for property recommendations and assistance

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Rishav-Upadhaya/DERA.git
   cd DERA
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the `.env` file:
   - Create a `.env` file in the root directory.
   - Add the following variables:
     ```
     DEEPSEEK_API_KEY=your_api_key_here
     ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000`.

## Usage

### Property Management
- **Add Property**: Navigate to the "Add Property" page to list a new property.
- **View Property**: Click on a property card to view its details.
- **Edit/Delete Property**: Property owners can edit or delete their properties.

### Booking Requests
- **Send Request**: Use the "Send a Book Request" button on a property page.
- **Manage Requests**: Property owners can accept or reject booking requests.

### Favorites
- **Add to Favorites**: Click the heart icon on a property card to mark it as a favorite.
- **View Favorites**: Access the "Your Favorites" section to view saved properties.

### Chat
- **Chat with Owners/Renters**: Use the integrated chat system for communication.
- **AI Chatbot**: Interact with the AI assistant for property recommendations and queries.

## Project Structure

```
projectDERA/
├── property/
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   ├── models.py           # Database models
│   ├── views.py            # Application logic
│   └── urls.py             # URL routing
├── users/
│   ├── templates/          # User-related templates
│   ├── static/             # User-specific static files
│   ├── models.py           # User models
│   ├── views.py            # User-related logic
│   └── urls.py             # User URL routing
├── projectDERA/
│   ├── settings.py         # Project settings
│   ├── urls.py             # Project-level URL routing
│   └── asgi.py             # ASGI configuration for WebSocket support
└── manage.py               # Django management script
```

## Environment Variables

- `DEEPSEEK_API_KEY`: API key for OpenAI integration.

## Dependencies

- Django
- Django Channels
- OpenAI
- daphne
- dotenv

## Contributing

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

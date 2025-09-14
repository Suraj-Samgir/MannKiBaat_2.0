# MannKiBaat 2.0 - Project Context

## Project Overview

MannKiBaat 2.0 is a web-based mental health support platform designed specifically for students. The application provides a safe, confidential space for students to share their thoughts, concerns, and feelings related to various aspects of their lives. The platform uses AI to provide empathetic responses and personalized support to help students manage stress and improve their mental well-being.

### Key Features

1. **User Registration & Authentication**
   - Secure user registration with personal information
   - Password encryption using bcrypt
   - Session management for logged-in users

2. **Lifestyle Assessment**
   - Comprehensive lifestyle data collection
   - Questions about diet, physical activity, social interaction, relaxation habits
   - Screen time, stress level, and sleep hour tracking

3. **Category-Based Problem Selection**
   - 8 key life categories for students:
     - Spirituality
     - Mindset
     - Health
     - Personality
     - Relationships
     - Network
     - Career
     - Money
   - Subcategories for each main category with specific issues

4. **AI Dashboard**
   - Personalized dashboard showing user information
   - Lifestyle insights display
   - Selected categories and problems visualization

5. **24/7 AI Support**
   - Interactive chatbot for mental wellness support
   - Crisis detection and resources
   - Community support features
   - Wellness activities and challenges
   - Daily affirmations
   - Lifestyle suggestions

## Technology Stack

### Backend
- **Python 3.x**
- **Flask** - Web framework
- **Flask-SQLAlchemy** - ORM for database operations
- **SQLite** - Database storage
- **bcrypt** - Password hashing

### Frontend
- **HTML5**
- **CSS3** with custom styling
- **Bootstrap 4/5** - Responsive design framework
- **JavaScript** - Client-side interactivity
- **Jinja2** - Template engine

### Key Dependencies
- Flask==3.1.2
- Flask-SQLAlchemy==3.1.1
- bcrypt==4.3.0
- SQLAlchemy==2.0.43

## Project Structure

```
MannKiBaat_2.0/
├── app.py                 # Main Flask application
├── categories_data.py     # Category definitions
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── instance/
│   └── Database.db       # SQLite database
├── static/
│   ├── css/              # CSS stylesheets
│   └── images/           # Images for UI
└── templates/
    ├── components/       # Reusable UI components
    ├── category.html     # Category selection page
    ├── dashboard.html    # User dashboard
    ├── index.html        # Landing page
    ├── lifestyle.html    # Lifestyle data collection
    ├── login.html        # User login page
    └── register.html     # User registration page
```

## Database Schema

The application uses SQLite with the following tables:

1. **Userdb** - User registration information
   - id (Integer, Primary Key)
   - firstName (String)
   - lastName (String)
   - email (String, Unique)
   - phone (String)
   - password (String, Hashed)
   - gender (String)
   - birthDate (Date)
   - eduLevel (String)
   - fieldOfStudy (String)

2. **Lifestyle** - User lifestyle data
   - id (Integer, Primary Key)
   - user_id (Integer, Foreign Key to Userdb)
   - diet (String)
   - physicalActivity (String)
   - socialInteraction (String)
   - relaxHabit (String)
   - screenTime (Integer)
   - stressLevel (Integer)
   - sleepHrs (Integer)

3. **UserCategorySelection** - User-selected categories and problems
   - id (Integer, Primary Key)
   - user_id (Integer, Foreign Key to Userdb)
   - category (String)
   - subcategory (String)
   - description (Text)
   - created_at (DateTime)

## Key Routes

- `/` - Landing page
- `/login` - User login
- `/register` - User registration
- `/lifestyle` - Lifestyle data collection
- `/category` - Category selection
- `/dashboard` - User dashboard (after login)
- `/logout` - User logout

## Development Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open `http://localhost:5000` in your browser

## UI/UX Features

- **Dark/Light Theme Toggle** - Users can switch between themes
- **Responsive Design** - Works on mobile, tablet, and desktop
- **Animated Elements** - Smooth animations and transitions
- **Interactive Forms** - Range sliders, dropdowns, and input validation
- **Visual Feedback** - Hover effects, loading states, and transitions

## Categories & Subcategories

The application focuses on 8 key life categories for students:

1. **Spirituality** - Purpose, values, existential crises, mindfulness
2. **Mindset** - Negative thoughts, overthinking, self-esteem, trauma
3. **Health** - Sleep, diet, exercise, substance abuse, screen addiction
4. **Personality** - Self-criticism, adaptability, emotional expression
5. **Relationships** - Breakups, family conflicts, loneliness, trust issues
6. **Network** - Bullying, toxic environments, social stigma, support systems
7. **Career** - Academic stress, workplace pressure, career direction, imposter syndrome
8. **Money** - Debt, financial stress, student loans, money management

## Development Conventions

- **Code Style**: Follows Python PEP 8 standards
- **Database**: Uses SQLAlchemy ORM for database operations
- **Security**: Passwords are hashed with bcrypt
- **Templates**: Jinja2 templating with component-based structure
- **Frontend**: Bootstrap-based responsive design with custom CSS
- **Session Management**: Flask session handling for user authentication

## Important Notes for Development

1. The application uses SQLite for development, which is suitable for local testing but should be replaced with a production database for deployment.
2. Passwords are securely hashed using bcrypt.
3. User sessions are managed using Flask's built-in session handling.
4. Static assets (images, CSS) are organized in the `static` directory.
5. Template components are reusable UI elements stored in `templates/components`.
6. The application follows a linear user flow: Register → Lifestyle Data → Category Selection → Dashboard.

## Future Enhancements

1. Integration with actual AI chatbot APIs
2. Advanced analytics and insights based on user data
3. Community features for peer support
4. Mobile application development
5. Admin panel for managing user data and content
6. Integration with mental health resources and helplines
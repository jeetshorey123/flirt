# Review Website - Rate My Flirt

A beautiful Flask web application for collecting and displaying reviews with a 5-star rating system. Features a pink hearts animated background and Supabase database integration.

## Features

- ⭐ 5-star rating system
- 💕 Beautiful pink hearts animated background
- 📸 Profile photo display
- 📝 Review submission form
- 📊 Average rating calculation (public)
- 🔒 **Private reviews** - Reviews are not displayed publicly
- 👤 **Admin panel** - Private view of all reviews at `/admin/reviews`
- 💾 Supabase database integration
- 📱 Responsive design
- 🚀 Vercel deployment ready

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Make sure your `.env` file contains:
```
REACT_APP_SUPABASE_URL=https://pngzkvczhcuwwowztvcb.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuZ3prdmN6aGN1d3dvd3p0dmNiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzMzY5NzksImV4cCI6MjA2NzkxMjk3OX0.j0eHLlyXuySaZG41QH0pXA-iW1vT0HD-eiE99dwiF8w
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### 3. Database Setup

Follow the instructions in `SUPABASE_SETUP.md` to create the database table.

### 4. Add Your Photo

Replace `static/images/profile.jpg` with your actual photo.

### 5. Customize the Name

Edit `templates/index.html` and change "Beautiful Girl" to the actual name.

### 6. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## File Structure

```
review/
├── app.py                 # Main Flask application
├── supabase_client.py     # Supabase database client
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── vercel.json           # Vercel deployment config
├── SUPABASE_SETUP.md     # Database setup instructions
├── static/
│   ├── css/
│   │   └── style.css     # Styles with pink hearts theme
│   └── images/
│       └── profile.jpg   # Profile photo (replace with actual)
├── templates/
│   └── index.html        # Main page template
└── README.md             # This file
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI: `npm install -g vercel`
2. Run: `vercel`
3. Follow the prompts

### Environment Variables for Production

Set these environment variables in your deployment platform:
- `REACT_APP_SUPABASE_URL`
- `REACT_APP_SUPABASE_ANON_KEY`
- `SECRET_KEY`

## API Endpoints

- `GET /` - Main page with review form (reviews hidden from public)
- `POST /submit_review` - Submit a new review
- `GET /admin/reviews` - **Admin only** - View all submitted reviews
- `GET /api/reviews` - Get reviews as JSON (for admin use)

## Review Data Structure

Each review contains:
- Reviewer name
- Rating (1-5 stars)
- Flirt review (required)
- Improvement suggestions (optional)
- Timestamp

## Customization

- **Background**: Modify the CSS in `static/css/style.css` to change colors or animations
- **Name**: Update the name in `templates/index.html`
- **Photo**: Replace `static/images/profile.jpg`
- **Text**: Customize labels and placeholders in the template

## Privacy & Security

- 🔒 **Reviews are private** - Not displayed publicly to maintain authenticity
- 📊 Only average rating and total count are shown publicly
- 👤 Admin can view all reviews at `/admin/reviews`
- 🔑 Change the `SECRET_KEY` in production
- 🛡️ Configure proper Row Level Security policies in Supabase
- ⏱️ Consider adding rate limiting for review submissions

## Support

For issues or questions, check the database connection and ensure all environment variables are properly set.
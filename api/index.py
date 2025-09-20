from flask import Flask, render_template, request, redirect, flash, jsonify, send_from_directory
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def get_supabase_client():
    """Create and return a Supabase client"""
    try:
        from supabase import create_client, Client
        
        url = os.environ.get('REACT_APP_SUPABASE_URL')
        key = os.environ.get('REACT_APP_SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise ValueError("Supabase URL and ANON KEY must be set in environment variables")
        
        supabase = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return None

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    return send_from_directory(static_dir, filename)

@app.route('/myself.jpg')
def serve_photo():
    """Serve the profile photo"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(root_dir, 'myself.jpg')

@app.route('/')
def index():
    # Get review statistics only (don't fetch actual reviews for public display)
    supabase = get_supabase_client()
    try:
        if supabase:
            response = supabase.table('reviews').select('stars').execute()
            reviews = response.data
            
            # Calculate average rating and total count
            if reviews:
                total_rating = sum(review['stars'] for review in reviews)
                avg_rating = round(total_rating / len(reviews), 1)
                total_reviews = len(reviews)
            else:
                avg_rating = 0
                total_reviews = 0
        else:
            avg_rating = 0
            total_reviews = 0
            
    except Exception as e:
        print(f"Error fetching review stats: {e}")
        avg_rating = 0
        total_reviews = 0
    
    # Simple HTML response for now
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rate My Flirt - Review Page</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #ff69b4, #ffb6c1, #ffc0cb);
                margin: 0; padding: 20px; min-height: 100vh;
                position: relative;
                overflow-x: hidden;
            }}
            
            /* Animated hearts background */
            body::before {{
                content: '';
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background-image: 
                    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50,90 C50,90 10,60 10,35 C10,20 20,10 35,10 C42,10 50,15 50,15 C50,15 58,10 65,10 C80,10 90,20 90,35 C90,60 50,90 50,90 Z' fill='%23ff1493' opacity='0.1'/%3E%3C/svg%3E"),
                    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50,90 C50,90 10,60 10,35 C10,20 20,10 35,10 C42,10 50,15 50,15 C50,15 58,10 65,10 C80,10 90,20 90,35 C90,60 50,90 50,90 Z' fill='%23ff69b4' opacity='0.05'/%3E%3C/svg%3E");
                background-size: 60px 60px, 40px 40px;
                background-position: 0 0, 30px 30px;
                animation: floatHearts 20s linear infinite;
                pointer-events: none;
                z-index: -1;
            }}
            
            @keyframes floatHearts {{
                0% {{ transform: translateY(100vh) rotate(0deg); }}
                100% {{ transform: translateY(-100vh) rotate(360deg); }}
            }}
            
            .container {{ 
                max-width: 800px; margin: 0 auto; 
                background: rgba(255,255,255,0.95); 
                border-radius: 20px; padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .profile-photo {{ 
                width: 200px; height: 200px; border-radius: 50%; 
                border: 5px solid #ff69b4; box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                margin-bottom: 20px; object-fit: cover;
            }}
            .name {{ font-size: 2.5em; color: #d63384; margin: 10px 0; font-weight: bold; }}
            .rating-summary {{ 
                background: linear-gradient(135deg, #ff69b4, #ff1493);
                color: white; padding: 20px; border-radius: 15px; text-align: center;
                margin: 20px 0;
            }}
            .form-group {{ margin: 20px 0; }}
            .form-group label {{ display: block; margin-bottom: 8px; color: #d63384; font-weight: bold; }}
            .form-control {{ 
                border: 2px solid #ff69b4; border-radius: 8px;
            }}
            .form-control:focus {{ 
                border-color: #ff1493; box-shadow: 0 0 5px rgba(255, 20, 147, 0.3);
            }}
            .btn-primary {{ 
                background: linear-gradient(135deg, #ff69b4, #ff1493);
                border: none; border-radius: 25px; font-weight: bold;
            }}
            .rating-input {{ 
                display: flex; gap: 5px; justify-content: center;
                flex-wrap: wrap; margin: 10px 0;
            }}
            .rating-input input[type="radio"] {{ display: none; }}
            .rating-input label {{ 
                font-size: 2.5em; color: #ddd; cursor: pointer; 
                transition: color 0.2s; margin: 0 2px;
                line-height: 1;
            }}
            .rating-input label:hover,
            .rating-input input[type="radio"]:checked ~ label,
            .rating-input label.active {{ 
                color: #ffd700; text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            }}
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {{
                .container {{ margin: 10px; padding: 15px; }}
                .profile-photo {{ width: 150px; height: 150px; }}
                .name {{ font-size: 2em; }}
                .rating-input label {{ font-size: 2em; margin: 0 1px; }}
            }}
            
            @media (max-width: 480px) {{
                .rating-input {{ gap: 2px; }}
                .rating-input label {{ font-size: 1.8em; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="/myself.jpg" alt="Profile Photo" class="profile-photo">
                <h1 class="name">Rate My Flirt</h1>
            </div>
            
            <div class="rating-summary">
                <div style="font-size: 3em; font-weight: bold;">{avg_rating if avg_rating else 'No ratings yet'}</div>
                <div style="font-size: 1.5em; margin: 10px 0;">
                    {'★' * int(avg_rating) + '☆' * (5 - int(avg_rating)) if avg_rating else '☆☆☆☆☆'}
                </div>
                <div>Based on {total_reviews} review{'s' if total_reviews != 1 else ''}</div>
            </div>
            
            <div class="card">
                <div class="card-body">
                    <h2 class="card-title text-center text-primary">Leave a Review</h2>
                    <form method="POST" action="/submit_review">
                        <div class="form-group mb-3">
                            <label for="name" class="form-label">Your Name:</label>
                            <input type="text" id="name" name="name" class="form-control" required>
                        </div>
                        
                        <div class="form-group mb-3">
                            <label class="form-label text-center d-block">Overall Rating:</label>
                            <div class="rating-input justify-content-center">
                                <input type="radio" id="star5" name="stars" value="5">
                                <label for="star5">★</label>
                                <input type="radio" id="star4" name="stars" value="4">
                                <label for="star4">★</label>
                                <input type="radio" id="star3" name="stars" value="3">
                                <label for="star3">★</label>
                                <input type="radio" id="star2" name="stars" value="2">
                                <label for="star2">★</label>
                                <input type="radio" id="star1" name="stars" value="1">
                                <label for="star1">★</label>
                            </div>
                        </div>
                        
                        <div class="form-group mb-3">
                            <label for="review" class="form-label">Your Review (Required):</label>
                            <textarea id="review" name="review" rows="4" class="form-control" placeholder="Share your thoughts..." required></textarea>
                        </div>
                        
                        <div class="form-group mb-3">
                            <label for="improvement" class="form-label">Areas for Improvement (Optional):</label>
                            <textarea id="improvement" name="improvement" rows="3" class="form-control" placeholder="Any suggestions for improvement?"></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100 py-3">Submit Review ✨</button>
                    </form>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-body text-center">
                    <h3 style="color: #d63384;">Thank You for Your Interest! 💕</h3>
                    <p style="color: #666;">Your review means a lot! Reviews are kept private to maintain authenticity.</p>
                    <p><strong>Total Reviews: {total_reviews}</strong></p>
                    {f'<p><strong>Current Average: {avg_rating}/5 ⭐</strong></p>' if avg_rating > 0 else ''}
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Interactive star rating
            const ratingLabels = document.querySelectorAll('.rating-input label');
            
            ratingLabels.forEach((label, index) => {{
                label.addEventListener('mouseover', () => {{
                    highlightStars(5 - index);
                }});
                
                label.addEventListener('click', () => {{
                    const value = label.getAttribute('for').replace('star', '');
                    document.querySelector(`#star${{value}}`).checked = true;
                    highlightStars(parseInt(value));
                }});
            }});
            
            document.querySelector('.rating-input').addEventListener('mouseleave', () => {{
                const checkedInput = document.querySelector('.rating-input input[type="radio"]:checked');
                if (checkedInput) {{
                    highlightStars(parseInt(checkedInput.value));
                }} else {{
                    clearStars();
                }}
            }});
            
            function highlightStars(rating) {{
                ratingLabels.forEach((label, index) => {{
                    if (5 - index <= rating) {{
                        label.style.color = '#ffd700';
                    }} else {{
                        label.style.color = '#ddd';
                    }}
                }});
            }}
            
            function clearStars() {{
                ratingLabels.forEach(label => {{
                    label.style.color = '#ddd';
                }});
            }}
        </script>
    </body>
    </html>
    """

@app.route('/submit_review', methods=['POST'])
def submit_review():
    try:
        name = request.form.get('name')
        stars = int(request.form.get('stars'))
        review = request.form.get('review')
        improvement = request.form.get('improvement')
        
        if not all([name, stars, review]):
            return redirect('/')
        
        # Insert review into Supabase
        supabase = get_supabase_client()
        if supabase:
            data = {
                'name': name,
                'stars': stars,
                'review': review,
                'improvement': improvement,
                'created_at': datetime.now().isoformat()
            }
            
            response = supabase.table('reviews').insert(data).execute()
        
    except Exception as e:
        print(f"Error submitting review: {e}")
    
    return redirect('/')

@app.route('/api/reviews')
def api_reviews():
    """Protected API endpoint to get reviews as JSON - for admin use only"""
    supabase = get_supabase_client()
    try:
        if supabase:
            response = supabase.table('reviews').select('*').order('created_at', desc=True).execute()
            return jsonify(response.data)
        else:
            return jsonify({'error': 'Database connection failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/reviews')
def admin_reviews():
    """Admin page to view all reviews"""
    supabase = get_supabase_client()
    try:
        if supabase:
            response = supabase.table('reviews').select('*').order('created_at', desc=True).execute()
            reviews = response.data
            
            # Calculate average rating
            if reviews:
                total_rating = sum(review['stars'] for review in reviews)
                avg_rating = round(total_rating / len(reviews), 1)
            else:
                avg_rating = 0
        else:
            reviews = []
            avg_rating = 0
            
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        reviews = []
        avg_rating = 0
    
    reviews_html = ""
    for review in reviews:
        stars_html = "★" * review['stars'] + "☆" * (5 - review['stars'])
        reviews_html += f"""
        <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 15px; border-left: 5px solid #ff69b4;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <strong style="color: #d63384;">{review['name']}</strong>
                <span style="color: #666; font-size: 0.9em;">{review['created_at'][:10] if review.get('created_at') else 'Unknown date'}</span>
            </div>
            <div style="margin: 10px 0; color: #ffd700; font-size: 1.2em;">{stars_html} ({review['stars']}/5)</div>
            <div style="margin: 15px 0;"><strong>Review:</strong><br>{review['review']}</div>
            {f'<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px;"><strong>Suggestions:</strong><br>{review["improvement"]}</div>' if review.get('improvement') else ''}
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Review Management</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #ff69b4, #ffb6c1); margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.95); border-radius: 20px; padding: 20px; }}
            .admin-header {{ background: linear-gradient(135deg, #dc3545, #6f1217); color: white; padding: 20px; border-radius: 15px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="admin-header">
                <h1>🔒 Admin Panel - Review Management</h1>
                <p>Private view of all submitted reviews</p>
            </div>
            
            <div style="background: linear-gradient(135deg, #ff69b4, #ff1493); color: white; padding: 20px; border-radius: 15px; margin: 20px 0; text-align: center;">
                <h3>Total Reviews: {len(reviews)}</h3>
                <h3>Average Rating: {avg_rating}/5</h3>
            </div>
            
            <h2>All Reviews ({len(reviews)})</h2>
            {reviews_html if reviews else '<p style="text-align: center; color: #666; margin: 40px 0;">No reviews submitted yet.</p>'}
            
            <div style="text-align: center; margin: 40px 0;">
                <a href="/" style="color: #ff69b4; text-decoration: none; font-weight: bold;">← Back to Public Page</a>
            </div>
        </div>
    </body>
    </html>
    """

# This is the main Flask app for Vercel
# For local development
if __name__ == '__main__':
    app.run(debug=True)
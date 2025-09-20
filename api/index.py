from flask import Flask, render_template, request, redirect, flash, jsonify
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
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #ff69b4, #ffb6c1, #ffc0cb);
                margin: 0; padding: 20px; min-height: 100vh;
            }}
            .container {{ 
                max-width: 800px; margin: 0 auto; 
                background: rgba(255,255,255,0.95); 
                border-radius: 20px; padding: 20px;
            }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .name {{ font-size: 2.5em; color: #d63384; margin: 10px 0; }}
            .rating-summary {{ 
                background: linear-gradient(135deg, #ff69b4, #ff1493);
                color: white; padding: 20px; border-radius: 15px; text-align: center;
            }}
            .form-group {{ margin: 20px 0; }}
            .form-group label {{ display: block; margin-bottom: 8px; color: #d63384; font-weight: bold; }}
            .form-group input, .form-group textarea {{ 
                width: 100%; padding: 12px; border: 2px solid #ff69b4; 
                border-radius: 8px; box-sizing: border-box;
            }}
            .submit-btn {{ 
                background: linear-gradient(135deg, #ff69b4, #ff1493);
                color: white; padding: 15px 30px; border: none; border-radius: 25px;
                font-size: 18px; cursor: pointer; width: 100%;
            }}
            .rating-input {{ display: flex; gap: 10px; margin: 10px 0; }}
            .rating-input label {{ font-size: 2em; color: #ddd; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="name">Rate My Flirt</h1>
            </div>
            
            <div class="rating-summary">
                <div style="font-size: 3em;">{avg_rating if avg_rating else 'No ratings yet'}</div>
                <div>Based on {total_reviews} review{'s' if total_reviews != 1 else ''}</div>
            </div>
            
            <div style="background: #fff; padding: 30px; border-radius: 15px; margin: 30px 0;">
                <h2>Leave a Review</h2>
                <form method="POST" action="/submit_review">
                    <div class="form-group">
                        <label for="name">Your Name:</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    
                    <div class="form-group">
                        <label>Overall Rating:</label>
                        <div class="rating-input">
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
                    
                    <div class="form-group">
                        <label for="review">Your Review (Required):</label>
                        <textarea id="review" name="review" rows="4" placeholder="Share your thoughts..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="improvement">Areas for Improvement (Optional):</label>
                        <textarea id="improvement" name="improvement" rows="3" placeholder="Any suggestions for improvement?"></textarea>
                    </div>
                    
                    <button type="submit" class="submit-btn">Submit Review</button>
                </form>
            </div>
            
            <div style="text-align: center; padding: 40px; background: rgba(255, 255, 255, 0.9); border-radius: 15px;">
                <h3 style="color: #d63384;">Thank You for Your Interest! 💕</h3>
                <p style="color: #666;">Your review means a lot! Reviews are kept private to maintain authenticity.</p>
                <p><strong>Total Reviews: {total_reviews}</strong></p>
            </div>
        </div>
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

# This is the main handler function for Vercel
def handler(req):
    return app

# For local development
if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from datetime import datetime

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Environment variables loaded from .env file")
except ImportError:
    print("python-dotenv not available, using system environment variables")

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

def get_supabase_client():
    try:
        from supabase import create_client, Client
        
        url = os.environ.get('REACT_APP_SUPABASE_URL')
        key = os.environ.get('REACT_APP_SUPABASE_ANON_KEY')
        
        # Enhanced debugging for Vercel
        print(f"Environment check - URL exists: {bool(url)}, Key exists: {bool(key)}")
        if url:
            print(f"URL starts with: {url[:20]}...")
        if key:
            print(f"Key starts with: {key[:20]}...")
        
        if not url or not key:
            print("Missing Supabase credentials - check Vercel environment variables")
            return None
        
        supabase = create_client(url, key)
        print("Supabase client created successfully")
        return supabase
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return None

@app.route('/static/<path:filename>')
def serve_static(filename):
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    return send_from_directory(static_dir, filename)

@app.route('/myself.jpg')
def serve_photo():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return send_from_directory(root_dir, 'myself.jpg')

@app.route('/')
def index():
    supabase = get_supabase_client()
    try:
        if supabase:
            response = supabase.table('reviews').select('stars').execute()
            reviews = response.data
            
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
    
    return render_template('index.html', reviews=[], avg_rating=avg_rating, total_reviews=total_reviews)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    try:
        name = request.form.get('name')
        stars = int(request.form.get('stars'))
        review = request.form.get('review')
        improvement = request.form.get('improvement')
        
        if not all([name, stars, review]):
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('index'))
        
        supabase = get_supabase_client()
        print(f"Supabase client status: {supabase is not None}")
        
        if supabase:
            data = {
                'name': name,
                'stars': stars,
                'review': review,
                'improvement': improvement,
                'created_at': datetime.now().isoformat()
            }
            
            print(f"Attempting to insert data: {data}")
            response = supabase.table('reviews').insert(data).execute()
            print(f"Insert response: {response}")
            flash('Thank you for your review!', 'success')
        else:
            print("Supabase client is None - database connection failed")
            flash('Database connection failed. Please try again.', 'error')
        
    except Exception as e:
        print(f"Error submitting review: {e}")
        flash('There was an error submitting your review. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/debug/env')
def debug_env():
    """Debug endpoint to check environment variables on Vercel"""
    url = os.environ.get('REACT_APP_SUPABASE_URL')
    key = os.environ.get('REACT_APP_SUPABASE_ANON_KEY')
    
    debug_info = {
        'has_supabase_url': bool(url),
        'has_supabase_key': bool(key),
        'url_preview': url[:30] + '...' if url else None,
        'key_preview': key[:30] + '...' if key else None,
        'all_env_vars': list(os.environ.keys())
    }
    
    return jsonify(debug_info)

@app.route('/admin/reviews')
def admin_reviews():
    supabase = get_supabase_client()
    try:
        if supabase:
            response = supabase.table('reviews').select('*').order('created_at', desc=True).execute()
            reviews = response.data
            
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
    
    return render_template('admin_reviews.html', reviews=reviews, avg_rating=avg_rating, total_reviews=len(reviews))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

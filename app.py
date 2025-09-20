import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from supabase_client import get_supabase_client

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

@app.route('/')
def index():
    # Get all reviews from Supabase
    supabase = get_supabase_client()
    try:
        response = supabase.table('reviews').select('*').order('created_at', desc=True).execute()
        reviews = response.data
        
        # Calculate average rating
        if reviews:
            total_rating = sum(review['stars'] for review in reviews)
            avg_rating = round(total_rating / len(reviews), 1)
        else:
            avg_rating = 0
            
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        reviews = []
        avg_rating = 0
    
    return render_template('index.html', reviews=reviews, avg_rating=avg_rating, total_reviews=len(reviews))

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
        
        # Insert review into Supabase
        supabase = get_supabase_client()
        data = {
            'name': name,
            'stars': stars,
            'review': review,
            'improvement': improvement,
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('reviews').insert(data).execute()
        flash('Thank you for your review!', 'success')
        
    except Exception as e:
        print(f"Error submitting review: {e}")
        flash('There was an error submitting your review. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/reviews')
def api_reviews():
    """API endpoint to get reviews as JSON"""
    supabase = get_supabase_client()
    try:
        response = supabase.table('reviews').select('*').order('created_at', desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
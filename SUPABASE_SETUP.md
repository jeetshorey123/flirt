# Supabase Database Setup

To set up your Supabase database, follow these steps:

## 1. Create the Reviews Table

Execute this SQL in your Supabase SQL editor:

```sql
-- Create the reviews table with 4 main columns: name, stars, review, improvement
CREATE TABLE reviews (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    stars INTEGER NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review TEXT NOT NULL,
    improvement TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create an index on created_at for better performance
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow public read access (optional)
CREATE POLICY "Allow public read access on reviews" ON reviews
    FOR SELECT USING (true);

-- Create a policy to allow public insert access (optional)
CREATE POLICY "Allow public insert access on reviews" ON reviews
    FOR INSERT WITH CHECK (true);
```

## 2. Test the Database Connection

You can test if your database is working by running the Flask app and trying to submit a review.

## 3. View Your Data

You can view your reviews in the Supabase dashboard under the "Table Editor" section.

## 4. API Access

The reviews are also accessible via the API endpoint: `/api/reviews`

## Database Schema

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| name | VARCHAR(100) | Name of the person leaving the review |
| stars | INTEGER | Rating from 1-5 stars |
| review | TEXT | Main review content |
| improvement | TEXT | Optional suggestions for improvement |
| created_at | TIMESTAMP | When the review was created |
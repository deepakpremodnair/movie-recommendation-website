import streamlit as st
import mysql.connector
from mysql.connector import Error
import bcrypt

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='Lamiya@2004',  # Replace with your MySQL password
            database='movie_db'  # Your database name
        )
        if connection.is_connected():
            return connection
        else:
            st.error("Failed to connect to the database.")
            return None
    except Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Function to add a movie
def add_movie(title, director, genre, language, release_year, rating, review, image_url):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Movies (title, director, genre, language, release_year, rating, review, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
            (title, director, genre, language, release_year, rating, review, image_url)
        )
        connection.commit()
        cursor.close()
        connection.close()
        st.success("Movie added successfully!")
    except Error as e:
        st.error(f"Error adding movie: {e}")

# Function to display movies as cards
def display_movies(movies):
    for movie in movies:
        with st.container():
            st.markdown(f"""
            <div style="background-color: #ecf0f1; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                <h2 style="color: #2980b9;">{movie['title']}</h2>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])

            with col1:
                st.image(movie['image_url'], use_column_width=True)

            with col2:
                st.write(f"<p style='color: #e74c3c;'><strong>Director:</strong> {movie['director']}</p>", unsafe_allow_html=True)
                st.write(f"<p style='color: #27ae60;'><strong>Genre:</strong> {movie['genre']}</p>", unsafe_allow_html=True)
                st.write(f"<p style='color: #8e44ad;'><strong>Language:</strong> {movie['language']}</p>", unsafe_allow_html=True)
                st.write(f"<p style='color: #f39c12;'><strong>Release Year:</strong> {movie['release_year']}</p>", unsafe_allow_html=True)
                st.write(f"<p style='color: #d35400;'><strong>Rating:</strong> {movie['rating']}</p>", unsafe_allow_html=True)
                st.write(f"<p style='color: #c0392b;'><strong>Review:</strong> {movie['review']}</p>", unsafe_allow_html=True)

            # Rating and comment section for each movie
            rating = st.slider(f"Rate {movie['title']}", min_value=0.0, max_value=10.0, step=0.1, key=f"rate_{movie['movie_id']}")
            comment = st.text_area(f"Leave a comment for {movie['title']}", key=f"comment_{movie['movie_id']}")

            if st.button(f"Submit Review for {movie['title']}", key=f"submit_{movie['movie_id']}"):
                submit_review(movie['movie_id'], rating, comment)

            st.markdown("<hr style='border:2px solid #3498db'>", unsafe_allow_html=True)

# Function to submit review and rating
def submit_review(movie_id, rating, comment):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Reviews (movie_id, rating, comment) VALUES (%s, %s, %s)",
            (movie_id, rating, comment)
        )
        connection.commit()
        cursor.close()
        connection.close()
        st.success("Review submitted successfully!")
    except Error as e:
        st.error(f"Error submitting review: {e}")

# Function to search for movies
def search_movies(search_query):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Movies WHERE title LIKE %s", (f"%{search_query}%",))
        movies = cursor.fetchall()
        cursor.close()
        connection.close()
        return movies
    except Error as e:
        st.error(f"Error searching for movies: {e}")
        return []

# Function to signup a new user
def signup(username, password):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO Users (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
        connection.commit()
        cursor.close()
        connection.close()
        st.success("Account created successfully!")
    except Error as e:
        st.error(f"Error creating account: {e}")

# Main function to run the Streamlit app
def main():
    st.markdown("<h1 style='text-align: center; color: #2980b9;'>🎬 Movie Database Management System</h1>", unsafe_allow_html=True)

    connection = create_connection()
    if connection is None:
        st.stop()

    # Initialize session state for tracking login and role
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''

    option = st.sidebar.selectbox("Select Action", ["Login", "Signup", "Search Movies", "View Movies"])

    # Signup Option
    if option == "Signup":
        st.sidebar.markdown("<h2 style='color: #27ae60;'>🔑 Signup</h2>", unsafe_allow_html=True)
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Create Account"):
            signup(username, password)

    # If not logged in, show login page
    elif option == "Login" and not st.session_state.logged_in:
        st.sidebar.markdown("<h2 style='color: #3498db;'>🔐 Login</h2>", unsafe_allow_html=True)
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
                user = cursor.fetchone()
                cursor.close()

                if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                    st.session_state.logged_in = True
                    st.session_state.user_role = 'admin' if username == 'admin' else 'user'
                    st.success(f"Logged in successfully as {username}!")
                else:
                    st.error("Invalid username or password.")
            except Error as e:
                st.error(f"Error logging in: {e}")

    # If logged in, show appropriate functionality
    elif st.session_state.logged_in:
        if st.session_state.user_role == 'admin':
            st.subheader("Admin Functionality")
            with st.form(key='add_movie_form'):
                movie_title = st.text_input("Title")
                movie_director = st.text_input("Director")
                movie_genre = st.text_input("Genre")
                movie_language = st.text_input("Language")
                movie_release_year = st.number_input("Release Year", min_value=1900, max_value=2100, value=2023)
                movie_rating = st.slider("Rating", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
                movie_review = st.text_area("Review")
                image_url = st.text_input("Image URL")

                submit_button = st.form_submit_button(label='Add Movie')
                if submit_button:
                    add_movie(movie_title, movie_director, movie_genre, movie_language, movie_release_year, movie_rating, movie_review, image_url)

        # View Movies or Search Movies
        if option == "Search Movies":
            search_query = st.text_input("Search for a movie")
            if st.button("Search"):
                movies = search_movies(search_query)
                if movies:
                    display_movies(movies)
                else:
                    st.warning("No movies found.")
        else:
            # By default, view all movies
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Movies")
            movies = cursor.fetchall()
            cursor.close()
            display_movies(movies)

if __name__ == "__main__":
    main()

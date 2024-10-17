import streamlit as st
from supabase import create_client, Client
import bcrypt

# Initialize Supabase client
SUPABASE_URL = "https://nfjmbgngzrwzaoclnfdi.supabase.co"  
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mam1iZ25nenJ3emFvY2xuZmRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkwMTMyNzQsImV4cCI6MjA0NDU4OTI3NH0.6G8SSUVrsaDWcgvwfmlS2e2z4M8jsQAcfJ7saQZHWbY"  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

admin_flag = 0
# Function to add a movie to Supabase
def add_movie(title, director, genres, language, release_year, rating, review, image_url):
    try:
        # Convert the list of genres to a comma-separated string
        genres_str = ', '.join(genres)  # Join genres into a single string
        data = {
            "title": title,
            "director": director,
            "genre": genres_str,  # Store the comma-separated genres
            "language": language,
            "release_year": release_year,
            "rating": rating,
            "review": review,
            "image_url": image_url
        }
        response = supabase.table('movies').insert(data).execute()
        st.success("Movie added successfully!")
        
    except Exception as e:
        st.write(title, director, genres_str, language, release_year, rating, review, image_url)
        st.error(f"Error adding movie: {str(e)}")  # Include the exception message

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

# Function to search for movies in Supabase
def search_movies(search_query, genres=None):
    try:
        query = supabase.table('movies').select('*')

        if search_query:
            query = query.ilike('title', f'%{search_query}%')

        if genres:
            # Convert the list of genres to a comma-separated string
            genres_str = ', '.join(genres)
            query = query.ilike('genre', f'%{genres_str}%')

        response = query.execute()

        if response.data:
            return response.data
        else:
            st.warning("No movies found.")
            return []
    except Exception as e:
        st.error(f"Error searching for movies: {e}")
        return []

# Function to signup a new user in Supabase with admin option
def signup(username, password, is_admin=False):
    try:
        # Properly hash the password
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        data = {
            "username": username,
            "password_hash": hashed_pw.decode('utf-8'),  # Store as string
            "is_admin": True if is_admin else False  # Assign role
        }
        response = supabase.table('users').insert(data).execute()
        if response.data:
            st.success("Account created successfully!")
        else:
            st.error("Failed to create account.")
    except Exception as e:
        st.error(f"Error creating account: {e}")

# Function to login a user with role-based logic
def login(username, password):
    try:
        response = supabase.table('users').select('*').eq('username', username).execute()
        user = response.data[0] if response.data else None

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            st.session_state.logged_in = True
            st.session_state.user_role = user['is_admin']
            st.success(f"Logged in successfully as {username} ({'Admin' if user['is_admin'] else 'User'})!")
        else:
            st.error("Invalid username or password.")
    except Exception as e:
        st.error(f"Error logging in: {e}")

def main():
    st.markdown("<h1 style='text-align: center; color: #2980b9;'>🎬 Movie Database Management System</h1>", unsafe_allow_html=True)

    # Initialize session state for tracking login and role
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''

    # Sidebar for Login/Signup
    if not st.session_state.logged_in:
        option = st.sidebar.selectbox("Select Action", ["Login", "Signup"])
        
        
        # Signup Option
        if option == "Signup":
            st.sidebar.markdown("<h2 style='color: #27ae60;'>🔑 Signup</h2>", unsafe_allow_html=True)
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            is_admin = st.sidebar.checkbox("Admin Account")
            if st.sidebar.button("Create Account"):
                signup(username, password, is_admin)

        # Login Option
        elif option == "Login":
            st.sidebar.markdown("<h2 style='color: #3498db;'>🔐 Login</h2>", unsafe_allow_html=True)
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                login(username, password)
    else:
        # Once logged in, show the action options dropdown
        action_option = st.sidebar.selectbox("Select Action", ["Search Movies", "Library", "Add Movies"])
            
        # Add Movie Option
        if action_option == "Add Movies":
            st.subheader("Add a New Movie")
            title = st.text_input("Title")
            director = st.text_input("Director")
            
            genre_options = ["Action", "Adventure", "Animation", "Biography", "Comedy", "Dark Comedy", "Satire", "Crime", 
                             "Documentary", "Drama", "Historical Drama", "Crime Drama", "Psychological Drama", "Family", 
                             "Fantasy", "Horror", "Psychological Horror", "Supernatural Horror", "Slasher", "Musical", 
                             "Mystery", "Romance", "Sci-Fi", "Space Opera", "Cyberpunk", "Dystopian", "Sport", 
                             "Thriller", "War", "Western", "Martial Arts", "Superhero", "Spy"]
            genres = st.multiselect("Select Genre(s)", genre_options)
            language = st.text_input("Language")
            release_year = st.number_input("Release Year", min_value=1900, max_value=2100, value=2024)
            rating = st.number_input("Rating", min_value=0.0, max_value=10.0, value=0.0)
            review = st.text_area("Review")
            image_url = st.text_input("Image URL")

            if st.button("Add Movie"):
                add_movie(title, director, [genre.strip() for genre in genres], language, release_year, rating, review, image_url)

        # Search Movies Option
        if st.session_state.logged_in and action_option == "Search Movies":
            st.subheader("Search Movies")
            search_query = st.text_input("Search for a movie")
            genre_options = ["Action", "Adventure", "Animation", "Biography", "Comedy", "Dark Comedy", "Satire", "Crime", "Documentary", "Drama", "Historical Drama", "Crime Drama", "Psychological Drama", "Family", "Fantasy", "Horror", "Psychological Horror", "Supernatural Horror", "Slasher", "Musical", "Mystery", "Romance", "Sci-Fi", "Space Opera", "Cyberpunk", "Dystopian", "Sport", "Thriller", "War", "Western", "Martial Arts", "Superhero", "Spy"]
            genres = st.multiselect("Select Genre(s)", genre_options)
            if st.button("Search"):
                # Call search_movies with the title and genre parameters
                movies = search_movies(search_query, genres if genres else None)
                if movies:
                    display_movies(movies)
                else:
                    st.warning("No movies found.")
        elif st.session_state.logged_in and action_option == "View Movies":
            st.subheader("View All Movies")
            response = supabase.table('movies').select('*').execute()
            if response.error is None:
                display_movies(response.data)
            else:
                st.error("Error retrieving movies.")

        # View Movies Option
        elif action_option == "Library":
            st.subheader("View All Movies")
            response = supabase.table('movies').select('*').execute()
            if response.error is None:
                display_movies(response.data)
            else:
                st.error("Error retrieving movies.")

if __name__ == "__main__":
    main()

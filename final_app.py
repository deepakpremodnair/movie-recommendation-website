import streamlit as st
from supabase import create_client, Client
import bcrypt


# Initialize Supabase client
SUPABASE_URL = "https://nfjmbgngzrwzaoclnfdi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mam1iZ25nenJ3emFvY2xuZmRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkwMTMyNzQsImV4cCI6MjA0NDU4OTI3NH0.6G8SSUVrsaDWcgvwfmlS2e2z4M8jsQAcfJ7saQZHWbY"  # Replace with your actual Supabase key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.session_state.watchlist_plausible_dict = {}

# Function to add a movie to Supabase
def add_movie(title, director, genres, language, release_year, rating, review, image_url):
    try:
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
        st.error(f"Error adding movie: {str(e)}")  # Include the exception message

def add_to_watchlist(final_user_id, watchlist):
    try:
        # Loop through the watchlist dictionary and insert each movie
        for movie_id, movie_title in watchlist.items():
            # Check if the movie is already in the user's watchlist
            existing_entry = supabase.table('watchlist').select('*').eq('movie_id', movie_id).eq('user_id', final_user_id).execute()
            
            if existing_entry.data:
                st.warning(f"Movie '{movie_title}' is already in your watchlist.")
            else:
                watchlist_entry = {
                    "movie_id": movie_id,
                    "user_id": final_user_id
                }
                # Insert the watchlist entry for the movie
                response = supabase.table('watchlist').insert(watchlist_entry).execute()
                st.success(f"Added '{movie_title}' to your watchlist.")

    except Exception as e:
        st.error(f"Error adding movies to the watchlist: {str(e)}")


# Function to display movies as cards
def display_movies(movies, users):
    final_user_id = st.session_state.user_id
    watchlist_plausible_dict = {}
    
    # Initialize session state for watchlist selection
    if 'selected_movies' not in st.session_state:
        st.session_state.selected_movies = []

    for movie in movies:
        watchlist_plausible_dict.update({movie['id']: movie['title']})
        with st.container():
            st.markdown(f"""
                <div style='border: 1px solid #ddd; border-radius: 5px; margin: 20px; width: 40%; display: flex; flex-direction: column; align-items: center;'>
                    <div style='width: 100%;'>
                        <img src='{movie["image_url"]}' style='width: 100%; height: auto; object-fit: cover; border-top-left-radius: 5px; border-top-right-radius: 5px;'>
                    </div>
                    <div style='padding: 10px; text-align: center;'>
                        <h4 style='margin: 0;'>{movie["title"]}</h4>
                        <p style='margin: 0;'>⭐ Rating: {movie["rating"]}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.write('current user', final_user_id, movie['id'])

    # Use multiselect to allow users to select movies to add to the watchlist
    selected_movies = st.multiselect("Select movies to add to watchlist", list(watchlist_plausible_dict.values()))

    # Update session state with selected movies
    if selected_movies:
        st.session_state.selected_movies = selected_movies

    # Button to add selected movies to the watchlist
    if st.button("Add to watchlist"):
        add_to_watchlist(final_user_id, {movie_id: movie_title for movie_id, movie_title in watchlist_plausible_dict.items() if movie_title in st.session_state.selected_movies})

# Function to display movies in the user's watchlist
def display_watchlist_movies(user_id):
    try:
        # Get the watchlist for the logged-in user
        watchlist_response = supabase.table('watchlist').select('movie_id').eq('user_id', user_id).execute()
        watchlist_movie_ids = {entry['movie_id'] for entry in watchlist_response.data}  # Create a set of movie IDs

        # Get movies from the database
        movies_response = supabase.table('movies').select('*').execute()
        movies = movies_response.data if movies_response.data else []

        # Filter movies based on user's watchlist
        filtered_movies = [movie for movie in movies if movie['id'] in watchlist_movie_ids]

        if filtered_movies:
            for movie in filtered_movies:
                with st.container():
                    st.markdown(f"""
                        <div style='border: 1px solid #ddd; border-radius: 5px; margin: 20px; width: 40%; display: flex; flex-direction: column; align-items: center;'>
                            <div style='width: 100%;'>
                                <img src='{movie["image_url"]}' style='width: 100%; height: auto; object-fit: cover; border-top-left-radius: 5px; border-top-right-radius: 5px;'>
                            </div>
                            <div style='padding: 10px; text-align: center;'>
                                <h4 style='margin: 0;'>{movie["title"]}</h4>
                                <p style='margin: 0;'>⭐ Rating: {movie["rating"]}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No movies found in your watchlist.")
    except Exception as e:
        st.error(f"Error fetching watchlist movies: {str(e)}")
        
# Function to search for movies in Supabase
@st.cache
def search_movies(search_query, genres=None):
    try:
        query = supabase.table('movies').select('*')

        if search_query:
            query = query.ilike('title', f'%{search_query}%')

        if genres:
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

# Function to get all the users in the database
@st.cache
def get_users():
    try:
        query = supabase.table('users').select('*')
        response = query.execute()
        
        if response.data:
            return response.data
        else:
            st.warning("No users found.")
            return []
    except Exception as e:
        st.error(f"Error searching for users: {e}")
        return []

# Function to signup a new user in Supabase with admin option
def signup(username, password, is_admin=False):
    try:
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        data = {
            "username": username,
            "password_hash": hashed_pw.decode('utf-8'),
            "is_admin": is_admin
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
            st.session_state.user_id = user['id']  # Store user ID
            user_identity = user['id']
            st.success(f"Logged in successfully as {username} ({'Admin' if user['is_admin'] else 'User'})!")
        else:
            st.error("Invalid username or password.")
    except Exception as e:
        st.error(f"Error logging in: {e}")

def delete_movie(movie_id):
    try:
        response1 = supabase.table('watchlist').delete().eq('movie_id', movie_id).execute()
        response = supabase.table('movies').delete().eq('id', movie_id).execute()
        if response.data:
            st.success(f"Movie with ID {movie_id} deleted successfully!")
        else:
            st.error("Failed to delete movie.")
    except Exception as e:
        st.error(f"Error deleting movie: {e}")
        
def main():
    st.markdown("<h1 style='text-align: center; color: #2980b9;'>🎬 Movie Database Management System</h1>", unsafe_allow_html=True)
    
    # Initialize session state for tracking login and role
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = ''
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

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
        users = get_users()
        action_options = ["Search Movies", "watchlist"]  # Always include these options
        
        # Only add "Add Movies" option if the user is an admin
        if st.session_state.user_role:
            action_options.append("Add Movies")
            action_options.append("Delete Movies")
        
        action_option = st.sidebar.selectbox("Select Action", action_options)
        
        # Add Movie Option
        if action_option == "Add Movies":
            st.subheader("Add a New Movie")
            title = st.text_input("Title")
            director = st.text_input("Director")
            
            genre_options = ["Action", "Adventure", "Animation", "Biography", "Comedy", "Dark Comedy", "Satire", "Crime", 
                             "Documentary", "Drama", "Historical Drama", "Crime Drama", "Psychological Drama", "Family", 
                             "Fantasy", "Horror", "Psychological Horror", "Supernatural Horror", "Slasher", 
                             "Science Fiction", "Mystery", "Romantic Comedy", "Romance", "Thriller", "Western"]
            genres = st.multiselect("Genres", genre_options)
            language = st.text_input("Language")
            release_year = st.number_input("Release Year", min_value=1900, max_value=2100, value=2024)
            rating = st.number_input("Rating", min_value=0.0, max_value=10.0, value=0.0, format="%.1f")
            review = st.text_area("Review")
            image_url = st.text_input("Image URL")
            
            if st.button("Add Movie"):
                add_movie(title, director, genres, language, release_year, rating, review, image_url)
        
        # Delete movie option
        elif action_option == "Delete Movies":
            st.subheader("Delete a Movie")
            
            # Fetch all movies for the admin to select
            movies_response = supabase.table('movies').select('*').execute()
            movies = movies_response.data if movies_response.data else []

            if movies:
                movie_titles = {movie['id']: movie['title'] for movie in movies}  # Create a dictionary for easy access
                movie_to_delete = st.selectbox("Select Movie to Delete", list(movie_titles.values()))

                if st.button("Delete Movie"):
                    movie_id = [id for id, title in movie_titles.items() if title == movie_to_delete][0]  # Get the ID from the title
                    delete_movie(movie_id)
            else:
                st.warning("No movies available to delete.")

        # Search Movies Option
        elif action_option == "Search Movies":
            st.subheader("Search for Movies")
            search_query = st.text_input("Search Movies")
            genres = st.multiselect("Select Genres", ["Action", "Adventure", "Comedy", "Drama", "Horror"])  # Add more genres as needed
            
            movies = search_movies(search_query, genres)
            display_movies(movies, users)
        
        # Display user's watchlist
        elif action_option == "watchlist":
            st.subheader("Your Watchlist")
            display_watchlist_movies(st.session_state.user_id)

# Run the app
if __name__ == "__main__":
    main()

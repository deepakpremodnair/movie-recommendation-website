import streamlit as st
import mysql.connector
from mysql.connector import Error

# Database connection function
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',     # Replace with your MySQL username
        password='Lamiya@2004',  # Replace with your MySQL password
        database='movie_db'       # Your database name
    )

# Function to add a movie to the database
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
        return True
    except Error as e:
        st.error(f"Error adding movie: {e}")
        return False

# Function to display movies as cards
def display_movies():
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Movies")
        movies = cursor.fetchall()
        cursor.close()
        connection.close()

        for movie in movies:
            with st.container():  # Create a container for each movie
                st.subheader(movie['title'])  # Movie Title
                col1, col2 = st.columns([1, 1])  # Create two columns for image and details

                with col1:
                    st.image(movie['image_url'], use_column_width=True)  # Movie Image

                with col2:
                    st.write(f"**Director:** {movie['director']}")
                    st.write(f"**Genre:** {movie['genre']}")
                    st.write(f"**Language:** {movie['language']}")
                    st.write(f"**Release Year:** {movie['release_year']}")
                    st.write(f"**Rating:** {movie['rating']}")
                    st.write(f"**Review:** {movie['review']}")  # Display review

                st.write("---")  # Divider between movie cards
    except Error as e:
        st.error(f"Error fetching movies: {e}")

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

# Function to update a movie in the database
def update_movie(movie_id, title, director, genre, language, release_year, rating, review, image_url):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE Movies SET title = %s, director = %s, genre = %s, language = %s, release_year = %s, rating = %s, review = %s, image_url = %s WHERE movie_id = %s",
            (title, director, genre, language, release_year, rating, review, image_url, movie_id)
        )
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        st.error(f"Error updating movie: {e}")
        return False

# Function to delete a user from the database
def delete_user(user_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        st.error(f"Error deleting user: {e}")
        return False

# Function to display user comments and reviews
def display_user_reviews(movie_id):
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Reviews WHERE movie_id = %s", (movie_id,))
        reviews = cursor.fetchall()
        cursor.close()
        connection.close()

        if reviews:
            for review in reviews:
                st.write(f"**{review['username']}**: {review['comment']} (Rating: {review['rating']})")
        else:
            st.write("No reviews available for this movie.")
    except Error as e:
        st.error(f"Error fetching reviews: {e}")

# Main function to run the Streamlit application
def main():
    st.title("Movie Database Management System")

    # User login and signup section
    option = st.sidebar.selectbox("Select Action", ["Login", "Signup"])

    if option == "Signup":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Create Account"):
            # Add signup logic here (add to Users table)
            st.success("Account created successfully!")

    elif option == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        if st.sidebar.button("Login"):
            # Add login validation logic here
            st.success("Logged in successfully!")

            # Admin functionalities
            if username == 'admin':  # Simple admin check
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
                        st.success("Movie added successfully!")

                st.subheader("Update Movie")
                movie_id = st.number_input("Movie ID to update", min_value=1)
                update_title = st.text_input("New Title")
                update_director = st.text_input("New Director")
                update_genre = st.text_input("New Genre")
                update_language = st.text_input("New Language")
                update_release_year = st.number_input("New Release Year", min_value=1900, max_value=2100, value=2023)
                update_rating = st.slider("New Rating", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
                update_review = st.text_area("New Review")
                update_image_url = st.text_input("New Image URL")

                if st.button("Update Movie"):
                    update_movie(movie_id, update_title, update_director, update_genre, update_language, update_release_year, update_rating, update_review, update_image_url)
                    st.success("Movie updated successfully!")

                st.subheader("Delete User")
                user_id = st.number_input("User ID to delete", min_value=1)
                if st.button("Delete User"):
                    delete_user(user_id)
                    st.success("User deleted successfully!")

            else:  # Regular user functionalities
                st.subheader("User Functionality")
                search_query = st.text_input("Search for a movie")
                if st.button("Search"):
                    movies = search_movies(search_query)
                    if movies:
                        for movie in movies:
                            with st.container():  # Create a container for each movie
                                st.subheader(movie['title'])  # Movie Title
                                col1, col2 = st.columns([1, 1])  # Create two columns for image and details

                                with col1:
                                    st.image(movie['image_url'], use_column_width=True)  # Movie Image

                                with col2:
                                    st.write(f"**Director:** {movie['director']}")
                                    st.write(f"**Genre:** {movie['genre']}")
                                    st.write(f"**Language:** {movie['language']}")
                                    st.write(f"**Release Year:** {movie['release_year']}")
                                    st.write(f"**Rating:** {movie['rating']}")
                                    st.write(f"**Review:** {movie['review']}")
                                    
                                    display_user_reviews(movie['movie_id'])  # Display reviews for the movie
                                st.write("---")  # Divider between movie cards
                    else:
                        st.warning("No movies found.")

    # Display available movies
    st.subheader("Available Movies")
    display_movies()

# Run the application
if __name__ == "__main__":
    main()

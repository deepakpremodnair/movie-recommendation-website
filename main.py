import streamlit as st
from streamlit_navigation_bar import st_navbar

# Create navigation bar
page = st_navbar(["Home", "About", "My List"])

# Function to display the Home page
def show_home():
    # Centered title
    st.markdown("<h2 style='text-align: center;'>Welcome to the Home Page</h2>", unsafe_allow_html=True)

    # Centered search bar
    search_query = st.text_input("Search", "")

    # Genre and Release Date fields
    st.write("### Filter options:")
    genre = st.text_input("Genre", "")
    release_date = st.date_input("Release Date")

    # Rating slider (1.0 to 10.0 with one decimal place)
    rating = st.slider("Rate (1.0 - 10.0)", min_value=1.0, max_value=10.0, value=5.0, step=0.1)

    # Made three columns to center the button
    col1, col2, col3 = st.columns([1, 0.4, 1])
    
    # Button Clicking Action
    with col2:
        if st.button("Submit"):
            st.write(f"Search Query: {search_query}")
            st.write(f"Genre: {genre}")
            st.write(f"Release Date: {release_date}")
            st.write(f"Rating: {rating:.1f}")  # Display rating with one decimal place

# Function to display the About page
def show_about():
    st.markdown("<h2 style='text-align: center;'>About Us</h2>", unsafe_allow_html=True)
    st.write("This is a simple Streamlit application with a navigation bar at the top.")

# Function to display the My List page with movie cards
def show_my_list():
    st.markdown("<h2 style='text-align: center;'>My List</h2>", unsafe_allow_html=True)
    
    # Example movie data (replace with actual data as needed)
    movies = [
        {"title": "Movie 1", "rating": 8.5, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 2", "rating": 7.0, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 3", "rating": 9.0, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 4", "rating": 6.5, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 5", "rating": 8.0, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 6", "rating": 7.5, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 7", "rating": 9.5, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 8", "rating": 6.0, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 9", "rating": 9.5, "image": "https://via.placeholder.com/150"},
        {"title": "Movie 10", "rating": 6.0, "image": "https://via.placeholder.com/150"},
    ]

    # Create 4 columns for the cards
    cols = st.columns(4)  
    for index, movie in enumerate(movies):
        with cols[index % 4]:  # Use modulo to alternate columns
            st.markdown(f"""
                <div style='border: 1px solid #ddd; border-radius: 5px; margin: 20px; width: 100%; display: flex; flex-direction: column; align-items: center;'>
                    <div style='width: 100%;'>
                        <img src='{movie["image"]}' style='width: 100%; height: auto; object-fit: cover; border-top-left-radius: 5px; border-top-right-radius: 5px;'>
                    </div>
                    <div style='padding: 10px; text-align: center;'>
                        <h4 style='margin: 0;'>{movie["title"]}</h4>
                        <p style='margin: 0;'>Rating: {movie["rating"]}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            

# Render the corresponding page based on the navigation bar selection
if page == "Home":
    show_home()
elif page == "About":
    show_about()
elif page == "My List":
    show_my_list()

import azure.identity as AzureIdentity
import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient
import config
from movie import Movie
from azure.cosmos.partition_key import PartitionKey

HOST = config.settings['host'].value
MASTER_KEY = config.settings['master_key'].value
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

#Get movies to seed DB
def get_seed_movies():
   movies = [ 
        Movie("The Godfather", "1972", 9.2, "Crime, Drama"),
        Movie("The Shawshank Redemption", "1994", 9.2, "Drama")
    ]

   return movies

#function to setup new db and container
def init():
    #connect to azure cosmos db
    client = CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        db = client.create_database(id=DATABASE_ID)
        print("Created database: {0}".format(db.id))

    except exceptions.CosmosResourceExistsError:
        db = client.get_database_client(DATABASE_ID)
        print("Database {0} already exists".format(DATABASE_ID))

    #Remove this after running once
    # container = db.get_container_client(CONTAINER_ID)
    # db.delete_container(container=container)

    #setup container
    try:
        container = db.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path='/title'))
        print("Created container: {0}".format(container.id))

    except exceptions.CosmosResourceExistsError:
        container = db.get_container_client(CONTAINER_ID)
        print("Container {0} already exists".format(CONTAINER_ID))

    #add items to container
    movies = get_seed_movies()

    for movie in movies:
        movie_to_add = {
            "id": movie.title,
            "title": movie.title,
            "releaseYear": movie.release_year,
            "rating": movie.rating,
            "genre": movie.genre
            }
        
        print(movie_to_add)
        try:
            container.create_item(body=movie_to_add)
            print(f"Created movie with title: {movie.title}")
        except exceptions.CosmosResourceExistsError:
            print(f"Movie with title: {movie.title} already exists")

if __name__ == "__main__":
    init()
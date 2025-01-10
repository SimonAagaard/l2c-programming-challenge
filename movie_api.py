import uvicorn
import config
import azure.cosmos.exceptions as exceptions
import azure.identity as AzureIdentity
from fastapi import FastAPI, Response, status
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from movie import Movie

HOST = config.settings['host'].value
MASTER_KEY = config.settings['master_key'].value
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']
STORAGE_ACCOUNT_URL = config.settings['storage_account_url']

app = FastAPI()
default_credential = AzureIdentity.DefaultAzureCredential()
cosmos_client = CosmosClient(HOST, {'masterKey': MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
blob_service_client = BlobServiceClient(STORAGE_ACCOUNT_URL, credential=default_credential)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/getmovies")
def get_movies():
    #Get movies from cosmos db
    db_client = cosmos_client.get_database_client(DATABASE_ID)
    container_client = db_client.get_container_client(CONTAINER_ID)
    items_list = list(container_client.read_all_items(max_item_count=10))

    movies = list(map(map_movie, items_list))
    for movie in movies:
        if movie.title == "The Shawshank Redemption":
            movie.cover_url = blob_service_client.get_blob_client(container="images", blob="godfather-cover.jpg").url
        elif movie.title == "The Godfather":
            movie.cover_url = blob_service_client.get_blob_client(container="images", blob="5051892225281.webp").url
            
    return movies

@app.get("/getmoviesbyyear/{year}")
def get_movies_by_year(year: int, response: Response):
     #Get movies from cosmos db
    db_client = cosmos_client.get_database_client(DATABASE_ID)
    container_client = db_client.get_container_client(CONTAINER_ID)
    items_list = list(container_client.query_items(
        query="SELECT * FROM m WHERE m.releaseYear = @year",
        parameters=[
            {"name": "@year", "value": f"{year}"}
        ],
        enable_cross_partition_query=True
    ))

    if len(items_list) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": "No movies found for year " + str(year)}

    movies = list(map(map_movie, items_list))
    for movie in movies:
        if movie.title == "The Shawshank Redemption":
            movie.cover_url = blob_service_client.get_blob_client(container="images", blob="godfather-cover.jpg").url
        elif movie.title == "The Godfather":
            movie.cover_url = blob_service_client.get_blob_client(container="images", blob="5051892225281.webp").url
            
    return movies

@app.get("/getmoviesummary/{title}")
def get_movie_summary(title: str):
    pass

def map_movie(item):
    return Movie(item.__getitem__("title"), item.__getitem__("releaseYear"), item.__getitem__("rating"), item.__getitem__("genre"))

if __name__ == "__main__":
    uvicorn.run("movie_api:app", port=8010, log_level="info")
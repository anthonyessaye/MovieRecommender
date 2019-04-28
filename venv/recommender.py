import os
import time
import gc
import argparse
import pandas as pd
from fuzzywuzzy import fuzz
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

class KnnClass:

    def __init__(self, movies_path, ratings_path):

        # Path for movie csv containing movies data
        self.movies_path = movies_path
        # Path for ratings csv containing ratings data
        self.ratings_path = ratings_path
        # Movie rating (0-5)
        self.movie_rating_thres = 0
        # # of User raiting for a movie
        self.user_rating_thres = 0
        self.model = NearestNeighbors()
        # Create t0 to calculate estimated finish time
        self.t0 = 0

    def SetFilterParams(self, movie_rating_thres, user_rating_thres):

        # Set movie and user rating frequency threshold
        self.movie_rating_thres = movie_rating_thres
        self.user_rating_thres = user_rating_thres

        # Start the timer
        self.t0 = time.time()

    def SetModelParams(self, n_neighbors, algorithm, metric, jobs=None):
     
        # Setting up the model parameters for the sklearn NearestNeighbors
        if jobs and (jobs > 1 or jobs == -1):
            os.environ['JOBLIB_TEMP_FOLDER'] = '/tmp'
        self.model.set_params(**{
            'n_neighbors': n_neighbors,
            'algorithm': algorithm,
            'metric': metric,
            'n_jobs': jobs})

    def PrepareData(self):
    
        ### Prepate the data for the recommender

        # Read the data from movies csv
        movies = pd.read_csv(
            os.path.join(self.movies_path),
            usecols=['movieId', 'title'],
            dtype={'movieId': 'int32', 'title': 'str'})
        ratings = pd.read_csv(
            os.path.join(self.ratings_path),
            usecols=['userId', 'movieId', 'rating'],
            dtype={'userId': 'int32', 'movieId': 'int32', 'rating': 'float32'})
        # Filter the data
        movies_count = pd.DataFrame(
            ratings.groupby('movieId').size(),
            columns=['count'])
        popular_movies = list(set(movies_count.query('count >= @self.movie_rating_thres').index))
        movies_filter = ratings.movieId.isin(popular_movies).values

        users_count = pd.DataFrame(
            ratings.groupby('userId').size(),
            columns=['count'])
        active_users = list(set(users_count.query('count >= @self.user_rating_thres').index))  
        users_filter = ratings.userId.isin(active_users).values

        ratings_filtered = ratings[movies_filter & users_filter]

        # Move pivot and create movie/user matrix
        movie_user_mat = ratings_filtered.pivot(
            index='movieId', columns='userId', values='rating').fillna(0)
        # Create mapper from movie title to index
        hashmap = {
            movie: i for i, movie in
            enumerate(list(movies.set_index('movieId').loc[movie_user_mat.index].title)) 
        }
        # Transform matrix to scipy sparse matrix
        movie_user_mat_sparse = csr_matrix(movie_user_mat.values)

        # Cleam the memory
        del movies, movies_count, users_count
        del ratings, ratings_filtered, movie_user_mat
        gc.collect()
        return movie_user_mat_sparse, hashmap


    def FindMovieMatch(self, hashmap, user_move_input):

        ### Transform the movie name inputted by the user to lower case
        ### Map movie title name to index of the movie in data
        ### And use the fuzz library ratio function to find a match

        match = []
        # get match
        for move_title, index in hashmap.items():
            ratio = fuzz.ratio(move_title.lower(), user_move_input.lower())
            if ratio >= 60:
                match.append((move_title, index, ratio))
        # sort
        match = sorted(match, key=lambda x: x[2])[::-1]
        if not match:
            print('No match is found')
        else:
            print('Found matches in our database: '
                  '{0}\n'.format([x[0] for x in match]))
            return match[0][1]

    def FindData(self, model, data, hashmap,
                  movie_chosen, n_recommendations):
      
        ### Return top movies that are similar to the user's movie input

        # Fit the data to our model
        model.fit(data)

        # Get movie index
        print('You have input movie:', movie_chosen)
        index = self.FindMovieMatch(hashmap, movie_chosen)
        # FindData
        print('Finding movies..')
        print('......\n')

        distances, indices = model.kneighbors(
            data[index],
            n_neighbors=n_recommendations+1)
        # Get list of raw index of recommendations
        raw_recommends = \
            sorted(
                list(
                    zip(
                        indices.squeeze().tolist(),
                        distances.squeeze().tolist()
                    )
                ),
                key=lambda x: x[1]
            )[:0:-1]
        self.timeNeeded = 'It took {:.2f}s to finish \n\
              '.format(time.time() - self.t0)

        # return recommendation (movieId, distance)
        return raw_recommends

    def Recommend(self, movie_chosen, recommendations_count):
       
        # Prepare the data, load the sparse matrix and the hashmap
        movieUserMatSparse, hashmap = self.PrepareData()
        # Find recommendations
        rawRecommends = self.FindData(
            self.model, movieUserMatSparse, hashmap,
            movie_chosen, recommendations_count)

        # Create the return string of the recommended movies
        recommended_movies = ""

        # Print the results
        reversed_hashmap = {v: k for k, v in hashmap.items()}
        print('Recommendations for {}:'.format(movie_chosen))
        for i, (index, dist) in enumerate(rawRecommends):
            print('{0}: {1}, with distance '
                  'of {2}'.format(recommendations_count - i, reversed_hashmap[index], dist))
           # recommended_movies = '{0}: {1}, with distance ''of {2}'.format(recommendations_count - i, reversed_hashmap[index], '%.3f'%dist) + "\n" + recommended_movies
            recommended_movies = '{0}: {1}'.format(recommendations_count - i, reversed_hashmap[index]) + "\n" + recommended_movies

        return recommended_movies + '\n\n' + str(self.timeNeeded)


# --------------------- Functions for GUI class will be written below here -----------------------
def ApplicationSubmit(moviename, count):
    print(moviename)

    parser = argparse.ArgumentParser(
        prog="Movie Recommender",
        description="Run KNN Movie Recommender")
    parser.add_argument('--path', nargs='?', default='./data/MovieLens/',
                        help='input data path')
    parser.add_argument('--movies_filename', nargs='?', default='movies.csv',
                        help='provide movies filename')
    parser.add_argument('--ratings_filename', nargs='?', default='ratings.csv',
                        help='provide ratings filename')
    parser.add_argument('--movie_name', nargs="?" , default=moviename,
                        help='provide your favoriate movie name')
    parser.add_argument('--top_n', type=int, default=count,
                        help='top n movie recommendations')
    return parser.parse_args() 


def MyMain(moviename, count, minimumRating, userQuality, chosenMetric):

    # Get args and set the paths
    args = ApplicationSubmit(moviename, count)
    data_path = args.path
    movies_filename = args.movies_filename
    ratings_filename = args.ratings_filename
    movie_name = args.movie_name
    top_n = args.top_n

    # Initiate the knn class
    recommender = KnnClass(
        os.path.join(data_path, movies_filename),
        os.path.join(data_path, ratings_filename))

    # Set filters and model
    recommender.SetFilterParams(minimumRating, userQuality)
    recommender.SetModelParams(20, "auto", chosenMetric, -1)

    # Make recommendations
    rec = recommender.Recommend(movie_name, top_n) or "Something Went Wrong"

    return rec


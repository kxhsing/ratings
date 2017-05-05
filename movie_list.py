
def algorithm(user1, user2):
    ratings1 = user1.ratings
    ratings2 = user2.ratings

    movies1 = set()
    movies2 = set()

    for r1 = in ratings1:
        movies1.add(r1.movie_id)

    for r2 = in ratings2:
        movies2.add(r2.movie_id)

    common_movies = list(r1 & r2).sort()

    score_list = []

    for movie_id in common_movies:

        score1 = Rating.query.filter(Rating.movie_id==movie_id, Rating.user_id==user1.user_id).one().score
        score2 = Rating.query.filter(Rating.movie_id==movie_id, Rating.user_id==user2.user_id).one().score

        pair = (score1, score2)
        score_list.append(pair)

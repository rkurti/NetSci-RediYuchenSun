import itertools
from typing import Dict, List, Tuple

principals_file_name = 'usa.movie.principals.tsv'
basics_file_name = 'usa.movie.basics.tsv'
edge_file_name = 'edges.tsv'



def create_nodes(nodes_file, start_year, end_year, genre_list):
    """
    Create a list of movies within the given years and having all the given genres
    @param nodes_file: file to write the nodes to
    @param start_year: filter movies by start year
    @param end_year: filter movies by end year
    @param genre_list: filters movies by genres, keeping movies for which genre_list is a subset of its genres
    @return: nothing
    """
    in_file = open(basics_file_name, 'r', encoding="utf-8")
    out_file = open(nodes_file, 'w', encoding="utf-8")


    movie_index = 0
    title_index = 2
    year_index = 5
    genre_index = 8

    out_file.write('Id \t Label\n')

    # list of tuples of a movie_id with its title
    movie_list: List[Tuple] = []

    # build up movie_list
    for line in in_file.readlines():
        values: List[str] = line.split('\t')
        try:
            year = int(values[year_index])
            if start_year <= year <= end_year:
                movie_genres = values[genre_index]
                # check that all the genres in genre_list are in the movies' genres
                if any([genre in movie_genres for genre in genre_list]):
                    movie_list.append((values[movie_index], values[title_index]))
        except (ValueError, IndexError):
            pass

    print(f"Length of movie_list: {len(movie_list)}")
    # generate nodes
    for movie_id, title in movie_list:
        out_file.write('\t'.join((movie_id, title)))
        out_file.write('\n')

    movie_id_list = [line[movie_index] for line in movie_list]

    return movie_id_list



def create_edges(edges_file, roles, movies_id_list) -> None:
    """
    @param edges_file: file to write the edges to
    @param roles: filter principals by role
    @return: nothing
    """
    in_file = open(principals_file_name, 'r', encoding='utf-8')
    out_file = open(edges_file, 'w', encoding='utf-8')


    movie_index = 0
    principal_index = 2
    role_index = 3

    out_file.write('Source \t Target\n')

    # dictionary of principals to a list of movies
    principals: Dict[str, List] = {}

    # build up principals dict
    for line in in_file.readlines():
        values: List[str] = line.split('\t')
        movie_id = values[movie_index]

        if movie_id in movies_id_list:
            principal_id = values[principal_index]

            if values[role_index] in roles:
                principals[principal_id] = principals[principal_id] + [movie_id] if principal_id in principals else [movie_id]

    print(f"Length of principals dict: {len(principals)}")
    # generate edges
    for person in principals:
        movies = principals[person]
        # create an edge for each possible combination of movies
        movie_pairs = itertools.combinations(movies, 2)

        for pair in movie_pairs:
            out_file.write('\t'.join(pair))
            out_file.write('\n')


if __name__ == '__main__':
    allGenres = ["Documentary","News","Sport","Adventure","Fantasy","NA","Biography",
                 "Drama","Family","War","History","Comedy","Western","Crime","Romance",
                 "Action","Thriller","Horror","Mystery","Music","Sci-Fi","Animation",
                 "Musical","Film-Noir","Talk-Show","Adult"]
    movies = create_nodes("nodes.tsv", 1990, 1999, allGenres)
    create_edges("edges.tsv", ["actor", "actress"], movies)
    horror = create_nodes("horrorNodes.tsv", 1990, 1999, ["Horror"])
    create_edges("horrorEdges.tsv", ["actor", "actress"], horror)
    comedy = create_nodes("comedyNodes.tsv", 1990, 1999, ["Comedy"])
    create_edges("comedyEdges.tsv", ["actor", "actress"], comedy)
    action = create_nodes("actionNodes.tsv", 1990, 1999, ["Action"])
    create_edges("actionEdges.tsv", ["actor", "actress"], action)
    drama = create_nodes("dramaNodes.tsv", 1990, 1999, ["Drama"])
    create_edges("DramaEdges.tsv", ["actor", "actress"], drama)
    romance = create_nodes("romanceNodes.tsv", 1990, 1999, ["Romance"])
    create_edges("romanceEdges.tsv", ["actor", "actress"], romance)




"""
options for category in principals.tsv:
 "self"                "director"            "producer"            "actor"              
 "composer"            "actress"             "writer"              "cinematographer"    
 "editor"              "production_designer" "archive_footage"     "archive_sound"      

options for genres in basics.tsv:
 "Documentary" "News"        "Sport"       "Adventure"   "Fantasy"     NA           
 "Biography"   "Drama"       "Family"      "War"         "History"     "Comedy"     
 "Western"     "Crime"       "Romance"     "Action"      "Thriller"    "Horror"     
 "Mystery"     "Music"       "Sci-Fi"      "Animation"   "Musical"     "Film-Noir"  
 "Talk-Show"   "Adult"

options for primaryProfession in names.tsv:
"actress"                   "soundtrack"                "producer"                 
 "actor"                     "writer"                    "director"                 
 "make_up_department"        "miscellaneous"             "composer"                 
 "music_department"          "assistant_director"        "camera_department"        
 "cinematographer"           "casting_director"          "editor"                   
 "set_decorator"             "stunts"                    "editorial_department"     
 "costume_department"        "animation_department"      "art_department"           
 "executive"                 "special_effects"           "production_designer"      
 "production_manager"        "sound_department"          "casting_department"       
 "costume_designer"          "visual_effects"            "art_director"             
 "location_management"       "transportation_department" "manager"                  
 "legal"                     "publicist"                 "talent_agent"             
 "assistant"             
"""
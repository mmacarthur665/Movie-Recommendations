"""
Program Name: Movie Recommendation Creator
Author: Michael Macarthur
Date: 4/22/2020

Summary: This program is intended to be fed the names of folders and files which contain data about movies and movie
ratings. The program manipulates these pieces of information and will produce recommendations for movies specified
individuals have not seen based upon average reviewer scores.
"""

# imports and pandas view settings below

import os
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.width', 1000)


def createpath():
    """
    This function will request the user to tell it where the data files are located and which ones to use. It will
    create data frames based upon where it was directed by the user
    :return: movies data frame, critics data frame, personal ratings data frame, and name of the person
    """

    file_loc = input("Please enter the name of the folder with files, the name of the movies file, the name of the "
                     "critics file, and the name of personal ratings file separated by spaces:")
    loc_lst = file_loc.split()
    folder = loc_lst[0]
    movies = loc_lst[1]
    c_ratings = loc_lst[2]
    p_ratings = loc_lst[3]

    # sends program to specified directory
    path = os.path.join(os.getcwd(), folder)
    moviespath = os.path.join(os.getcwd(), folder + '\\' + movies)
    criticspath = os.path.join(os.getcwd(), folder + '\\' + c_ratings)
    personalpath = os.path.join(os.getcwd(), folder + '\\' + p_ratings)

    # creates dataframes from each file
    movies = pd.read_csv(moviespath, index_col='Title', usecols=['Title', 'Genre1', 'Year', 'Runtime'], na_filter=False)
    critics = pd.read_csv(criticspath, index_col='Title')
    personal = pd.read_csv(personalpath, index_col='Title')
    p = personal.columns.tolist()

    return movies, critics, personal, p


def findclosestcritics(critics, personal):
    """
    This function will take the critics and personal ratings data frames and find the critics who have the most similar
    ratings as the person based on euclidean distance
    :return: a list of the three closest critics
    """
    critics = critics
    personal = personal
    p = personal.columns.tolist()  # puts person's name into a list
    # inner joins critics and personal ratings so we only see those that are shared
    temp = pd.merge(critics, personal, how='inner', on='Title')
    temp2 = (temp.values - temp[p].values) ** 2  # takes difference of critics and person - then squares it
    temp3 = pd.DataFrame(temp2, index=temp.index, columns=temp.columns)  # puts array from temp2 into new dataframe
    temp3 = temp3.drop(p, axis=1)  # drops person
    temp4 = temp3.sum(axis=0).sort_values(ascending=True)  # creates and sorts column sums
    closest_critics = temp4[0:3].index.to_list()  # produces the list of top 3 closest critics
    print("The following critics had the closest ratings to ", ''.join(map(str, p)), ":")
    print(closest_critics[0]+', '+closest_critics[1]+', '+closest_critics[2])
    print(" ")
    return closest_critics


def recommendmovies(critics, personal, closest_critics, movies):
    """
    This function takes list of closest critics and uses it to determine which critics ratings to use to make
    recommendations. It will use the average of the 3 critics as a baseline to determine if various movies in 8 genres
    are appropriate to recommend to the person.
    :return: data frame of recommendations
    """

    critics = critics
    personal = personal
    closest_critics = closest_critics
    movies = movies

    critics2 = critics.loc[:, closest_critics]  # selects columns for only the closest critics
    critics2['rating'] = round(critics2.mean(axis=1), 2)  # calcs avg for each movie

    # left joins data so we can see which movies have been reviewed and not watched
    rec_temp = pd.merge(critics2, personal, how='left', on='Title')

    unwatch = rec_temp[rec_temp.iloc[:, -1].isnull()]  # selects only rows where person has not rated movie

    # joins to larger dataset so we see all data for unwatched movies
    unwatch_wdata = pd.merge(unwatch, movies, how='inner', on='Title')
    unwatch_wdata1 = unwatch_wdata.groupby(by=['Genre1']).max()  # calcs max rating by genre and puts in a different df
    genre_max = unwatch_wdata1['rating']

    # joins genre_max to larger dataframe for filtering
    unwatch_wdata2 = unwatch_wdata.join(genre_max, on='Genre1', lsuffix='x', rsuffix='y')

    # leverages query to simply filter down to top rated films by genre
    recs = unwatch_wdata2.query('ratingx >= ratingy')

    return recs


def printrecommendations(recs, p):
    """
    This function will take the recommendations data frame, do some final formatting, and print out the results based
    along with the person's name.
    :return: none
    """

    recs = recs
    p = p

    # this part sorts the dataframe
    recs = recs.sort_values(by=['Genre1'])

    # these blocks add string stuff to make output look like Profs
    recs['ratingx'] = 'rating: ' + recs['ratingx'].astype(str)  # adds rating: string
    recs['runs'] = 'runs ' + recs['Runtime'].astype(str)  # adds run string
    recs['runs'].mask(recs['runs'] == 'runs ', '', inplace=True)  # replaces all rows with 'runs ' with blanks
    recs['Genre'] = '(' + recs['Genre1'] + ')'  # adds parentheses around genre
    recs_final = pd.DataFrame(recs, index=recs.index, columns=['Genre', 'ratingx', 'Year', 'runs'])  # creates final df

    recs_final.index.name = None  # removes awkward extra space
    print("Recommendations for", ''.join(map(str, p)), ":")  # prints recommendations for 'person's name'
    print(recs_final.to_string(index=True, header=False))  # prints data frame of recommendations and relevant info


def main():
    """
    This function serves only to call the previously defined functions
    :return: none
    """

    movies, critics, personal, p = createpath()
    closest_critics = findclosestcritics(critics=critics, personal=personal)
    recs = recommendmovies(critics=critics, personal=personal, closest_critics=closest_critics, movies = movies)
    printrecommendations(recs=recs, p=p)

main()



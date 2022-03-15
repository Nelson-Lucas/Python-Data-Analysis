#The following 10 questions were answered, based on the DSA Academy course.

#1- What are the most common movie categories on IMDB?
#2- How many titles by genre?
#3- What is the median rating of films by genre?
#4- What is the median rating of films in relation to the year they were released?
#5- What is the number of films evaluated by genre in relation to the year of release?
#6- What is the longest running movie? Calculate percentiles.
#7- What is the relationship between duration and gender?
#8- What is the number of films produced per country?
#9- What are the Top 10 best movies?
#10- What are the Top 10 worst movies?

!pip install -q imdb-sqlite

import re
import time
import sqlite3
import pycountry
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from sklearn.feature_extraction.text import CountVectorizer
import warnings
warnings.filterwarnings("ignore")
sns.set_theme(style = "whitegrid")

%%time
!imdb-sqlite

conn = sqlite3.connect("imdb.db")

tabelas = pd.read_sql_query("SELECT NAME AS 'Table_Name' FROM sqlite_master WHERE type = 'table'", conn)

type(tabelas)

tabelas.head()

tabelas = tabelas["Table_Name"].values.tolist()

for tabela in tabelas:
    consulta = "PRAGMA TABLE_INFO({})".format(tabela)
    resultado = pd.read_sql_query(consulta, conn)
    print("Esquema da tabela:", tabela)
    display(resultado)
    print("-"*100)
    print("\n")


#Answering the questions.

#1- What are the most common movie categories on IMDB?

# Create the SQL query
consulta1 = '''SELECT type, COUNT(*) AS COUNT FROM titles GROUP BY type''' 

# Extract the result
resultado1 = pd.read_sql_query(consulta1, conn)

# View the result
display(resultado1)

# Calculating the percentage for each type
resultado1['percentual'] = (resultado1['COUNT'] / resultado1['COUNT'].sum()) * 100

# View the result
display(resultado1)

# Creating a chart with only 4 categories:
# The 3 categories with the most titles and 1 category with everything else

# Creating an empty dictionary
others = {}

# Filter the percentage by 5% and add the total
others['COUNT'] = resultado1[resultado1['percentual'] < 5]['COUNT'].sum()

# Write the percentage
others['percentual'] = resultado1[resultado1['percentual'] < 5]['percentual'].sum()

# Set the name
others['type'] = 'others'

# viewing
others

# Filter the result dataframe
resultado1 = resultado1[resultado1['percentual'] > 5]

# Append with dataframe from other categories
resultado1 = resultado1.append(others, ignore_index = True)

# Sort the result
resultado1 = resultado1.sort_values(by = 'COUNT', ascending = False)

# view
resultado1.head()

# Adjust labels
labels = [str(resultado1['type'][i])+' '+'['+str(round(resultado1['percentual'][i],2)) +'%'+']' for i in resultado1.index]

# Plot

# color map
# https://matplotlib.org/stable/tutorials/colors/colormaps.html
cs = cm.Set3(np.arange(100))

# Create the figure
f = plt.figure()

# Pie Plot
plt.pie(resultado1['COUNT'], labeldistance = 1, radius = 3, colors = cs, wedgeprops = dict(width = 0.8))
plt.legend(labels = labels, loc = 'center', prop = {'size':12})
plt.title("Distribuição de Títulos", loc = 'Center', fontdict = {'fontsize':20,'fontweight':20})
plt.show()

#2- How many titles by genre?

# Create the SQL query
consulta2 = '''SELECT genres, COUNT(*) FROM titles WHERE type = 'movie' GROUP BY genres''' 

# Result
resultado2 = pd.read_sql_query(consulta2, conn)

# View the result
display(resultado2)

# Convert strings to lowercase
resultado2['genres'] = resultado2['genres'].str.lower().values

# Remove NA (missing) values
temp = resultado2['genres'].dropna()

# Creating an array using regular expression to filter strings

# https://docs.python.org/3.8/library/re.html
padrao = '(?u)\\b[\\w-]+\\b'

# https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
vetor = CountVectorizer(token_pattern = padrao, analyzer = 'word').fit(temp)

type(vetor)
sklearn.feature_extraction.text.CountVectorizer

# Apply vectorization to dataset without NA values
bag_generos = vetor.transform(temp)

type(bag_generos)

# Return unique genres
generos_unicos =  vetor.get_feature_names()

# Create the genre dataframe
generos = pd.DataFrame(bag_generos.todense(), columns = generos_unicos, index = temp.index)

# view
generos.info()

# Drop from column n
generos = generos.drop(columns = 'n', axis = 0)

# Calculate the percentage
generos_percentual = 100 * pd.Series(generos.sum()).sort_values(ascending = False) / generos.shape[0]

# view
generos_percentual.head(10)

# Plot
plt.figure(figsize = (16,8))
sns.barplot(x = generos_percentual.values, y = generos_percentual.index, orient = "h", palette = "terrain")
plt.ylabel('Gênero')             
plt.xlabel("\nPercentual de Filmes (%)")
plt.title('\nNúmero (Percentual) de Títulos Por Gênero\n')
plt.show()

#3- What is the median rating of films by genre?

# SQL Query
consulta3 = '''
            SELECT rating, genres FROM 
            ratings JOIN titles ON ratings.title_id = titles.title_id 
            WHERE premiered <= 2022 AND type = 'movie'
            ''' 

# Result
resultado3 = pd.read_sql_query(consulta3, conn)

# view
display(resultado3)

# Creating a function to return the genres
def retorna_generos(df):
    df['genres'] = df['genres'].str.lower().values
    temp = df['genres'].dropna()
    vetor = CountVectorizer(token_pattern = '(?u)\\b[\\w-]+\\b', analyzer = 'word').fit(temp)
    generos_unicos =  vetor.get_feature_names()
    generos_unicos = [genre for genre in generos_unicos if len(genre) > 1]
    return generos_unicos

# Apply the function
generos_unicos = retorna_generos(resultado3)

# view
generos_unicos

# Creating empty lists
genero_counts = []
genero_ratings = []

# Loop
for item in generos_unicos:
    
    # Returns the movie count by genre
    consulta = 'SELECT COUNT(rating) FROM ratings JOIN titles ON ratings.title_id=titles.title_id WHERE genres LIKE '+ '\''+'%'+item+'%'+'\' AND type=\'movie\''
    resultado = pd.read_sql_query(consulta, conn)
    genero_counts.append(resultado.values[0][0])
  
    # Returns the rating of movies by genre
    consulta = 'SELECT rating FROM ratings JOIN titles ON ratings.title_id=titles.title_id WHERE genres LIKE '+ '\''+'%'+item+'%'+'\' AND type=\'movie\''
    resultado = pd.read_sql_query(consulta, conn)
    genero_ratings.append(np.median(resultado['rating']))
    
# Prepare the final dataframe
df_genero_ratings = pd.DataFrame()
df_genero_ratings['genres'] = generos_unicos
df_genero_ratings['count'] = genero_counts
df_genero_ratings['rating'] = genero_ratings

# view
df_genero_ratings.head(20)

# Drop from index 18 (news), just taking out the information like genre
df_genero_ratings = df_genero_ratings.drop(index = 18)

# Sort the result
df_genero_ratings = df_genero_ratings.sort_values(by = 'rating', ascending = False)

# Plot

# Figure
plt.figure(figsize = (16,10))

# Barplot
sns.barplot(y = df_genero_ratings.genres, x = df_genero_ratings.rating, orient = "h")

# Graph texts
for i in range(len(df_genero_ratings.index)):
    
    plt.text(4.0, 
             i + 0.25, 
             str(df_genero_ratings['count'][df_genero_ratings.index[i]]) + " filmes")
    
    plt.text(df_genero_ratings.rating[df_genero_ratings.index[i]],
             i + 0.25,
             round(df_genero_ratings["rating"][df_genero_ratings.index[i]],2))

plt.ylabel('Gênero')             
plt.xlabel('Mediana da Avaliação')
plt.title('\nMediana de Avaliação Por Gênero\n')
plt.show()

#4- What is the median rating of films in relation to the year they were released?

# SQL Query
consulta4 = '''
            SELECT rating AS Rating, premiered FROM 
            ratings JOIN titles ON ratings.title_id = titles.title_id 
            WHERE premiered <= 2022 AND type = 'movie'
            ORDER BY premiered
            ''' 

# Result
resultado4 = pd.read_sql_query(consulta4, conn)

display(resultado4)

# We calculate the median over time (years)
ratings = []
for year in set(resultado4['premiered']):
    ratings.append(np.median(resultado4[resultado4['premiered'] == year]['Rating']))
    
# Checking the type    
type(ratings)

# Checking as list
ratings[1:10]

# List of years
anos = list(set(resultado4['premiered']))

#Checking the list of years
anos[1:10]

# Plot
plt.figure(figsize = (16,8))
plt.plot(anos, ratings)
plt.xlabel('\nAno')
plt.ylabel('Mediana de Avaliação')
plt.title('\nMediana de Avaliação dos Filmes Em Relação ao Ano de Estréia\n')
plt.show()

#5- What is the number of films evaluated by genre in relation to the year of release?

# SQL Query
consulta5 = '''SELECT genres FROM titles ''' 

# Result
resultado5 = pd.read_sql_query(consulta5, conn)

# Viewing the result
display(resultado5)

# Return unique genres
generos_unicos = retorna_generos(resultado5)

# View the result
generos_unicos

# Making the count
genero_count = []
for item in generos_unicos:
    consulta = 'SELECT COUNT(*) COUNT FROM  titles  WHERE genres LIKE '+ '\''+'%'+item+'%'+'\' AND type=\'movie\' AND premiered <= 2022'
    resultado = pd.read_sql_query(consulta, conn)
    genero_count.append(resultado['COUNT'].values[0])

# Preparing the dataframe
df_genero_count = pd.DataFrame()
df_genero_count['genre'] = generos_unicos
df_genero_count['Count'] = genero_count

# Calculating the top 5
df_genero_count = df_genero_count[df_genero_count['genre'] != 'n']
df_genero_count = df_genero_count.sort_values(by = 'Count', ascending = False)
top_generos = df_genero_count.head()['genre'].values

# Plot

# Figure
plt.figure(figsize = (16,8))

# Loop and Plot
for item in top_generos:
    consulta = 'SELECT COUNT(*) Number_of_movies, premiered Year FROM  titles  WHERE genres LIKE '+ '\''+'%'+item+'%'+'\' AND type=\'movie\' AND Year <=2022 GROUP BY Year'
    resultado = pd.read_sql_query(consulta, conn)
    plt.plot(resultado['Year'], resultado['Number_of_movies'])

plt.xlabel('\nAno')
plt.ylabel('Número de Filmes Avaliados')
plt.title('\nNúmero de Filmes Avaliados Por Gênero Em Relação ao Ano de Estréia\n')
plt.legend(labels = top_generos)
plt.show()

#6- What is the longest running movie? Calculating percentiles.

# SQL Query
consulta6 = '''
            SELECT runtime_minutes Runtime 
            FROM titles 
            WHERE type = 'movie' AND Runtime != 'NaN'
            ''' 

# Result
resultado6 = pd.read_sql_query(consulta6, conn)

# view
display(resultado6)

# Loop to calculate percentiles
for i in range(101): 
    val = i
    perc = round(np.percentile(resultado6['Runtime'].values, val), 2)
    print('{} percentil da duração (runtime) é: {}'.format(val, perc))

# Redoing the query and returning the movie with the longest duration
consulta6 = '''
            SELECT runtime_minutes Runtime, primary_title
            FROM titles 
            WHERE type = 'movie' AND Runtime != 'NaN'
            ORDER BY Runtime DESC
            LIMIT 1
            ''' 
# Reading the query
resultado6 = pd.read_sql_query(consulta6, conn)

# view
resultado6

#7- What is the Relationship Between Duration and Genre?

# SQL Query
consulta7 = '''
            SELECT AVG(runtime_minutes) Runtime, genres 
            FROM titles 
            WHERE type = 'movie'
            AND runtime_minutes != 'NaN'
            GROUP BY genres
            ''' 

# Result
resultado7 = pd.read_sql_query(consulta7, conn)

# Return unique genres
generos_unicos = retorna_generos(resultado7)

# view
generos_unicos

# Calculate duration by genre
genero_runtime = []
for item in generos_unicos:
    consulta = 'SELECT runtime_minutes Runtime FROM  titles  WHERE genres LIKE '+ '\''+'%'+item+'%'+'\' AND type=\'movie\' AND Runtime!=\'NaN\''
    resultado = pd.read_sql_query(consulta, conn)
    genero_runtime.append(np.median(resultado['Runtime']))
    
# Prepare the dataframe
df_genero_runtime = pd.DataFrame()
df_genero_runtime['genre'] = generos_unicos
df_genero_runtime['runtime'] = genero_runtime

# Remove index 18 (news)
df_genero_runtime = df_genero_runtime.drop(index = 18)

# Sort the data
df_genero_runtime = df_genero_runtime.sort_values(by = 'runtime', ascending = False)

# Plot

# Figure size
plt.figure(figsize = (16,8))

# Barplot
sns.barplot(y = df_genero_runtime.genre, x = df_genero_runtime.runtime, orient = "h")

# Loop
for i in range(len(df_genero_runtime.index)):
    plt.text(df_genero_runtime.runtime[df_genero_runtime.index[i]],
             i + 0.25,
             round(df_genero_runtime["runtime"][df_genero_runtime.index[i]], 2))

plt.ylabel('Gênero')             
plt.xlabel('\nMediana de Tempo de Duração (Minutos)')
plt.title('\nRelação Entre Duração e Gênero\n')
plt.show()

#8- What is the Number of Films Produced by Country?

# SQL Query
consulta8 = '''
            SELECT region, COUNT(*) Number_of_movies FROM 
            akas JOIN titles ON 
            akas.title_id = titles.title_id
            WHERE region != 'None'
            AND type = \'movie\'
            GROUP BY region
            ''' 

# Result
resultado8 = pd.read_sql_query(consulta8, conn)

# view
display(resultado8)

# Checking the Shape
resultado8.shape

# Number of lines
resultado8.shape[0]

# auxiliary lists
nomes_paises = []
contagem = []

# Loop to get country according to region
for i in range(resultado8.shape[0]):
    try:
        coun = resultado8['region'].values[i]
        nomes_paises.append(pycountry.countries.get(alpha_2 = coun).name)
        contagem.append(resultado8['Number_of_movies'].values[i])
    except: 
        continue
        
# Prepare the dataframe
df_filmes_paises = pd.DataFrame()
df_filmes_paises['country'] = nomes_paises
df_filmes_paises['Movie_Count'] = contagem

# Sort the result
df_filmes_paises = df_filmes_paises.sort_values(by = 'Movie_Count', ascending = False)

# view
df_filmes_paises.head(10)

# Plot

# Figure
plt.figure(figsize = (20,8))

# Barplot
sns.barplot(y = df_filmes_paises[:20].country, x = df_filmes_paises[:20].Movie_Count, orient = "h")

# Loop
for i in range(0,20):
    plt.text(df_filmes_paises.Movie_Count[df_filmes_paises.index[i]]-1,
             i + 0.30,
             round(df_filmes_paises["Movie_Count"][df_filmes_paises.index[i]],2))

plt.ylabel('País')             
plt.xlabel('\nNúmero de Filmes')
plt.title('\nNúmero de Filmes Produzidos Por País\n')
plt.show()

#9- What are the Top 10 best movies?

# SQL Query
consulta9 = '''
            SELECT primary_title AS Movie_Name, genres, rating
            FROM 
            titles JOIN ratings
            ON  titles.title_id = ratings.title_id
            WHERE titles.type = 'movie' AND ratings.votes >= 25000
            ORDER BY rating DESC
            LIMIT 10          
            ''' 

# Result
top10_melhores_filmes = pd.read_sql_query(consulta9, conn)

# View
display(top10_melhores_filmes)

#10- What are the Top 10 Worst Movies?

# SQL Query
consulta10 = '''
            SELECT primary_title AS Movie_Name, genres, rating
            FROM 
            titles JOIN ratings
            ON  titles.title_id = ratings.title_id
            WHERE titles.type = 'movie' AND ratings.votes >= 25000
            ORDER BY rating ASC
            LIMIT 10
            ''' 

# Result
top10_piores_filmes = pd.read_sql_query(consulta10, conn)

# View
display(top10_piores_filmes)


#End

#Prevendo o preço de casas em Boston usando o Scikit-Learn

#Explorando o Dataset Boston Housing disponível no seguinte link: http://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_boston.html

# Importando os módulos necessários
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import sklearn
%matplotlib inline

# O dataset boston já está disponível no scikit-learn, basta apenas carregá-lo.
from sklearn.datasets import load_boston
boston = load_boston()

# Verificando o tipo da variável boston
type(boston)

# Visualizando o shape do dataset, neste caso 506 instâncias (linhas) e 13 atributos (colunas)
boston.data.shape

# Descrição do dataset
print(boston.DESCR)

# Visualizando os atributos do Dataset
print(boston.feature_names)
['CRIM' 'ZN' 'INDUS' 'CHAS' 'NOX' 'RM' 'AGE' 'DIS' 'RAD' 'TAX' 'PTRATIO'
 'B' 'LSTAT']

# Convertendo o dataset em um DataFrame pandas
df = pd.DataFrame(boston.data)
df.head()


# Convertendo o título das colunas
df.columns = boston.feature_names
df.head()

# boston.target é uma array com o preço das casas, visualizando ele:
boston.target

# Adicionando o preço da casa ao DataFrame
df['PRICE'] = boston.target
df.head()

#Prevendo o preço das casas em Boston

#Y - variável dependente (preço das casas em Boston)
#X - variáveis independentes ou explanatórias (todas as outras caracterísricas da casa)

# Importando o módulo de regressão linear 
from sklearn.linear_model import LinearRegression

# Não queremos o preço da casa como variável dependente
X = df.drop('PRICE', axis = 1)

# Definindo Y
Y = df.PRICE

#Plot do Y
plt.scatter(df.RM, Y)
plt.xlabel("Média do Número de Quartos por Casa")
plt.ylabel("Preço da Casa")
plt.title("Relação entre Número de Quartos e Preço")
plt.show()

# Criando o objeto de regressão linear
regr = LinearRegression()

# Visualizando o tipo do objeto
type(regr)

# Treinando o modelo
regr.fit(X, Y)

# Coeficientes
print("Coeficiente: ", regr.intercept_)
print("Número de Coeficientes: ", len(regr.coef_))

# Prevendo o preço da casa
regr.predict(X)

# Comparando preços originais x preços previstos utilizando plotagem
plt.scatter(df.PRICE, regr.predict(X))
plt.xlabel("Preço Original")
plt.ylabel("Preço Previsto")
plt.title("Preço Original x Preço Previsto")
plt.show()

#Podemos ver que existem alguns erros na predição do preço das casas
# Vamos calcular o MSE (Mean Squared Error)
mse1 = np.mean((df.PRICE - regr.predict(X)) ** 2)
print(mse1)

# Aplicando regressão linear para apenas uma variável e calculando o MSE
regr = LinearRegression()
regr.fit(X[['PTRATIO']], df.PRICE)
mse2 = np.mean((df.PRICE - regr.predict(X[['PTRATIO']])) ** 2)
print(mse2)

#O MSE aumentou, indicando que uma única característica não é um bom predictor para o preço das casas.
#Na prática, você não vai implementar regressão linear em todo o dataset. Você vai dividir o dataset em datasets de treino e de teste. Assim, você treina seu modelo nos dados de treino e depois verifica como o modelo se comporta nos seus dados de teste. Vejamos:
# Dividindo X em dados de treino e de teste
X_treino = X[:-50]
X_teste = X[-50:]

# Dividindo Y em dados de treino e de teste
Y_treino = df.PRICE[:-50]
Y_teste = df.PRICE[-50:]

# Imprimindo o shape dos datasets
print(X_treino.shape, X_teste.shape, Y_treino.shape, Y_teste.shape)

# Podemos criar nossos datasets de treino de forma manual, mas claro este não é método correto. Vamos então dividir os datasets randomicamente. O Scikit-Learn provê uma função chamada train_test_split() para isso.
from sklearn.model_selection import train_test_split

# Dividindo X e Y em dados de treino e de teste
X_treino, X_teste, Y_treino, Y_teste = train_test_split(X, df.PRICE, test_size = 0.33, random_state = 5)

# Imprimindo o shape dos datasets
print(X_treino.shape, X_teste.shape, Y_treino.shape, Y_teste.shape)

# Construindo um modelo de regressão
regr = LinearRegression()

# Treinando o modelo
regr.fit(X_treino, Y_treino)

# Definindo os dados de treino e teste
pred_treino = regr.predict(X_treino)
pred_teste = regr.predict(X_teste)

# Comparando preços originais x preços previstos utilizando plotagem
plt.scatter(regr.predict(X_treino), regr.predict(X_treino) - Y_treino, c = 'b', s = 40, alpha = 0.5)
plt.scatter(regr.predict(X_teste), regr.predict(X_teste) - Y_teste, c = 'g', s = 40, alpha = 0.5)
plt.hlines(y = 0, xmin = 0, xmax = 50)
plt.ylabel("Resíduo")
plt.title("Residual Plot - Treino(Azul), Teste(Verde)")
plt.show()

# Fim

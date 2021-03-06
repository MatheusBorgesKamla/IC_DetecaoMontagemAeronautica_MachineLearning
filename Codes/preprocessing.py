import numpy as np
import pandas as pd
import random

#Função utilizada para carregar os dados de força e torque das csv's 
#presente na pasta que passo como parâmetro. Como cada experimento é uma csv,
#deve ser passado como parâmetro também o número de experimentos de parâmetros(data_num)
#e o numero de intervalos que estou considerando para cada força/torque, preciso que tenha mesmo tamanho para não
#gerar erros na hora de aplicar os modelos
def load(folder_name, data_num, num_intervalos):
    X = []
    for i in range(1,data_num+1):
        #Reproduzo o nome do arquivo csv e seu caminho para ser buscado
        name_file = ''.join([folder_name,'data_adjust-',str(i),'.csv'])
        #Leio o csv
        dataset_adj = pd.read_csv(name_file)
        #Mx_thr = dataset_thr.iloc[:,10].values
        #My_thr = dataset_thr.iloc[:,11].values
        #Dados de torque retirados padronizados para 3
        #Mx = dataset_adj.iloc[:num_intervalos,10].values/3
        #My = dataset_adj.iloc[:num_intervalos,11].values/3
        Mz = dataset_adj.iloc[:num_intervalos,12].values/3
        #Fx_thr = dataset_thr.iloc[:,7].values
        #Fy_thr = dataset_thr.iloc[:,8].values
        #Dados de força retirados padronizados para 30
        #Fx = dataset_adj.iloc[:num_intervalos,7].values/30
        #Fy = dataset_adj.iloc[:num_intervalos,8].values/30
        Fz = dataset_adj.iloc[:num_intervalos,9].values/30
        #Gero um vetor em que primeiro insiro  todos os dados de Fx, depois Fy e assim por diante
        #aux = np.concatenate([Fx, Fy, Fz, Mz, My, Mx])
        aux = np.concatenate([Fz, Mz])
        #Adiciono elas no final de X formando uma matriz
        X.append(aux)
    
    #Passo X para array - possuira dimensao 2 (primeiro indice o experimento, segundo a força/torque)
    X = np.array(X)
    #Elaboro o nome do arquivo csv e seu caminho para o label.csv
    name_label = ''.join([folder_name,'labels.csv'])
    #Leio o csv
    dataset_label = pd.read_csv(name_label)
    #Pego somente a coluna de classificação dos experimentos
    y = dataset_label.iloc[:,1].values
    return X, y
#Realiza a mesma coisa que a load() porem gerando uma estrutura tridimensional (n_experimento, n_intervalos, n_features)
def load_3dim(folder_name, data_num, num_intervalos):
    X = []
    for i in range(1,data_num+1):
        #Reproduzo o nome do arquivo csv e seu caminho para ser buscado
        name_file = ''.join([folder_name,'data_adjust-',str(i),'.csv'])
        #Leio o csv
        dataset_adj = pd.read_csv(name_file)
        #Mx_thr = dataset_thr.iloc[:,10].values
        #My_thr = dataset_thr.iloc[:,11].values
        #Dados de torque retirados padronizados para 3
        #Mx = dataset_adj.iloc[:num_intervalos,10].values/3
        #My = dataset_adj.iloc[:num_intervalos,11].values/3
        Mz = dataset_adj.iloc[:num_intervalos,12].values/3
        #Fx_thr = dataset_thr.iloc[:,7].values
        #Fy_thr = dataset_thr.iloc[:,8].values
        #Dados de força retirados padronizados para 30
        #Fx = dataset_adj.iloc[:num_intervalos,7].values/30
        #Fy = dataset_adj.iloc[:num_intervalos,8].values/30
        Fz = dataset_adj.iloc[:num_intervalos,9].values/30
        #Gero uma matriz unindo todas as colunas lado a lado
        #aux = np.column_stack((Fx,Fy,Fz,Mx,My,Mz))
        aux = np.column_stack((Fz,Mz))
        #Adiciono elas no final de X formando um cubo
        X.append(aux)
    
    #Passo X para array - possuira dimensao 3 (primeiro indice o experimento, segundo o intervalo do exp., terceiro a força/torque)
    X = np.array(X)
    #Elaboro o nome do arquivo csv e seu caminho para o label.csv
    name_label = ''.join([folder_name,'labels.csv'])
    #Leio o csv
    dataset_label = pd.read_csv(name_label)
    #Pego somente a coluna de classificação dos experimentos
    y = dataset_label.iloc[:,1].values
    return X, y

#Função em que a partir dos dados carregados em X e y irei manipular de forma que fique com os dados balanceados
#pegos de forma aleatória (para os estados de mounted e not mounted))
#tem que passar o numero de experimentos que estou usando, sendo data_num>61
def proc_balanceado(X, y, data_num):
    #Divido X e y em arrays para cada classificação
    # label 1 - mounted
    # label 2 - jammed
    # label 3 - not mounted
   
    X_mont, X_jam, X_nmont = separate_class(X,y,data_num)       
    #Gero uma lista de 61 números aleátorios para cada estado
    #Serão os experimentos que estarei pegando e só 61 porque quero eles balanceados (o estado jam é o que tem menos exp. com 61)
    X_new = []
    y_new = []
    data_select = 61
    list_sample_mont = random.sample(range(len(X_mont)),data_select)
    list_sample_jam = random.sample(range(len(X_jam)),data_select)
    list_sample_nmont = random.sample(range(len(X_nmont)),data_select)
    
    for i in range(0,data_select):
        X_new.append(X_mont[list_sample_mont[i]])
        y_new.append([1])
        X_new.append(X_jam[list_sample_jam[i]])
        y_new.append([2])
        X_new.append(X_nmont[list_sample_nmont[i]])
        y_new.append([3])
    
    #Embaralho os vetores para não ficar muito ordenado a classificação dos dados
    '''random.shuffle(X_new)
    random.shuffle(y_new)'''
    #Atualizo como vetores X e y para os novos valores
    X = np.array(X_new)
    y = np.array(y_new)
    return X, y

def dummy_variables(y):
    #Passando para dummy variables os rotulos de y utilizando o modulo OneHorEncoder
    from sklearn.preprocessing import OneHotEncoder
    onehotencoder = OneHotEncoder()
    y_new = onehotencoder.fit_transform(y).toarray()
    #Retiro uma coluna, pois somente com os estados 10,01,00 eu já consigo realizar a classificação
    #se não retirasse, ficaria com uma redundancia em meu dataset
    #y_new = y_new[:,0:2] 
    return y_new


#Função utilizada para padronizar os dados
def standardize_data(X_train, X_test):
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler()
    #Caso possuir 3 dimensoes o X_train e X_test
    if len(X_train.shape) == 3:
        for i in range(0,X_train.shape[0]):
            X_train[i] = sc.fit_transform(X_train[i])
        if X_test is not None:
            for i in range(0,X_test.shape[0]):
                X_test[i] = sc.transform(X_test[i])
    else:
        X_train = sc.fit_transform(X_train)
        if X_test is not None:
            X_test = sc.transform(X_test)
    return X_train, X_test


#Função que separa o dataset em treino e teste.
def split_data(X, y, test_percent, random_s):
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = test_percent, random_state = random_s)
    return X_train, X_test, y_train, y_test


#Função que irá gerar a média das componentes de cada grandeza (Força e Torque ) em um determinado numero de intervalos
def med_intervalo(X,n_inter):
    inter_length = int(X.shape[1]/(2*n_inter))
    X_new = np.zeros((X.shape[0],n_inter*2))
    for exp in range(0,X.shape[0]):
        for i in range(0,n_inter*2):
            ind = i*inter_length
            X_new[exp][i] = np.mean(X[exp,ind:ind+inter_length])
            
    return X_new
#Realiza a mesma coisa que a med_intervalo porem para 3 dimensoes
def med_intervalo_3dim(X,n_inter):
    inter_length = int(X.shape[1]/n_inter)
    X_new = np.zeros((X.shape[0],n_inter,2))
    for exp in range(0,X.shape[0]):
        for var in range(0,2):
            for it in range(0,n_inter):
                ind = it*inter_length
                X_new[exp][it][var] = np.mean(X[exp,ind:ind+inter_length,var])
            
            
    return X_new

def separate_class(X, y, data_num):
    y = y.reshape((data_num))
    X_mont = []
    X_jam = []
    X_nmont = []
    for i in range(0,data_num):
        if y[i] == 1:
            X_mont.append(X[i])
        elif y[i] == 2:
            X_jam.append(X[i])
        else :
            X_nmont.append(X[i])
    return X_mont, X_jam, X_nmont


        






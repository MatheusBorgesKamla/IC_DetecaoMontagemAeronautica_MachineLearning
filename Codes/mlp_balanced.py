import numpy as np
import preprocessing as pre


# --- MLP balanceada tomando todos os intervalos ---

data_num = 500
num_int = 2560
#Lendo todos os dados do experimento
X, y = pre.load('dataset/',data_num,num_int)
#Balanceando os dados entre os estados (aleatorizando variaveis idependentes para cada estado)
X, y = pre.proc_balanceado(X, y, data_num)
#Passando y para dummy variables
y_dummy = pre.dummy_variables(y)
#Separando em conjunto de treino e teste (pego de forma aleatoria, aleatorizando também as variáveis dependentes)
X_train, X_test, y_train, y_test = pre.split_data(X,y_dummy,0.1,None)
#Padronizando dados
X_train, X_test = pre.standardize_data(X_train,X_test)

#Implementando a MLP
from keras.models import Sequential
#modulo responsavel por inicializar a rede
from keras.layers import Dense, Dropout
#modulo responsavel por gerar as camadas da rede
mlp_cls = Sequential()

#Saidas do primeiro layer : (183+1)/2 = 92
mlp_cls.add(Dense(units=92, kernel_initializer='uniform', activation='sigmoid', input_dim=X_train.shape[1]))
mlp_cls.add(Dropout(0.5))
mlp_cls.add(Dense(units=y_train.shape[1], kernel_initializer='uniform', activation='softmax'))
mlp_cls.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

epochs = 200
mlp_cls.fit(X_train, y_train, epochs=epochs, batch_size=10, verbose=0)
y_predict = mlp_cls.predict(X_test)

y_pred_fin = np.zeros(y_predict.shape[0])
for i in range(0,y_predict.shape[0]):
    state = np.argmax(y_predict[i])
    if state == 0 :
        y_pred_fin[i] = 1
    elif state == 1 :
        y_pred_fin[i] = 2
    else:
        y_pred_fin[i] = 3
            
#Retornando o y_test para rotulos normais para conseguir chamar a confusion matrix
y_test_fin = np.zeros(y_test.shape[0])
for i in range(0,y_test.shape[0]):
    state = np.argmax(y_test[i])
    if state == 0 :
        y_test_fin[i] = 1
    elif state == 1 :
        y_test_fin[i] = 2
    else:
        y_test_fin[i] = 3
# Produzindo a confusing matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test_fin, y_pred_fin)
print('\n\nConfusion Matrix: \n', cm)
print('Accuracy: ',(cm[0,0]+cm[1,1]+cm[2,2])/np.sum(cm))

#Realizando K-fold Cross Validation com 10 folders
X_K, X_Knone, y_K, y_Knone = pre.split_data(X,y_dummy,0,None)
from sklearn.model_selection import StratifiedKFold
cvscores =[]
kfold = StratifiedKFold(n_splits=10, shuffle=True)
for train, test in kfold.split(X_K, y_K[:,0]):
    mlp_model = Sequential()
    mlp_model.add(Dense(units=92, activation='sigmoid', input_dim=np.shape(X)[1]))
    mlp_model.add(Dropout(0.5))
    mlp_model.add(Dense(units=np.shape(y_K)[1], kernel_initializer='uniform', activation='softmax'))
    mlp_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    mlp_model.fit(X_K[train], y_K[train], epochs=epochs, batch_size=10, verbose=0, validation_data=(X_K[test], y_K[test]))
    scores = mlp_model.evaluate(X_K[test], y_K[test], verbose=0)
    print("%s: %.2f%%" % (mlp_model.metrics_names[1], scores[1]*100))
    cvscores.append(scores[1] * 100)
print("%.2f%% (+/- %.2f%%)" % (np.mean(cvscores), np.std(cvscores)))

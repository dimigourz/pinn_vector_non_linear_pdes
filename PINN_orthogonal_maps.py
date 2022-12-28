#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 18:18:11 2022

@author: dimi
"""


import numpy as np
import torch
import torch.autograd as autograd         # computation graph
from torch import Tensor                  # tensor node in the computation graph
import torch.nn as nn                     # neural networks
import torch.optim as optim               # optimizers e.g. gradient descent, ADAM, etc.
import time
from pyDOE import lhs         #Latin Hypercube Sampling
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.cm as cm
#Set default dtype to float32
torch.set_default_dtype(torch.float)

#PyTorch random number generator
torch.manual_seed(1234)

# Random number generators in other libraries
np.random.seed(1234)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# device="cpu"
print(device)

if device == 'cuda': print(torch.cuda.get_device_name()) 


x_1 = np.linspace(0,1,256)  # 256 points between -1 and 1 [256x1]
x_2 = np.linspace(0,1,256)  # 256 points between 1 and -1 [256x1]

X, Y = np.meshgrid(x_1,x_2) 


X_u_test = np.hstack((X.flatten(order='F')[:,None], Y.flatten(order='F')[:,None]))

# Domain bounds
lb = np.array([0,0]) #lower bound
ub = np.array([1, 1])  #upper bound

a_1 = 1 
a_2 = 1

k = 1

#usol_1 =X+0*np.abs(X-Y) #solution chosen for convinience  
#usol_1= np.multiply(X,(X<1./4))+np.multiply((2./4-X),np.logical_and((X>=1./4),(X<2./4)))+np.multiply((-(1.-X)+2./4),np.logical_and((X>=2./4),(X<3./4)))+np.multiply((1.-X),(X>=3./4));


#usol_1= np.multiply(X,(X<1./4))+np.multiply((2./4-X),np.logical_and((X>=1./4),(X<2./4)))+np.multiply((-(1.-X)+2./4),np.logical_and((X>=2./4),(X<3./4)))+np.multiply((1.-X),(X>=3./4));

#usol_1=np.multiply(X,(X<1./3))+np.multiply((2./3-X),np.logical_and(X>=1./3,X<2./3))+np.multiply((X-2./3),(X>=2./3))
usol_1=np.multiply(X,(X<1./2))+np.multiply(1-X,(X>=1./2))
u_true = usol_1.flatten('F')[:,None] 
#return (x<y && x<1./2)*(x) +(x<y && x>1./2 && y>1./2)*(x)+(x>1./2 && y<1./2)*(-x)+(y>x &&  x<1./2 && y<1./2)*(-x)
#//                +(y>x &&  x>1./2)*(-x)+(x<1./2 && y>1./2)*(x);

#usol_2=np.multiply(Y,(Y<1./3))+np.multiply((2./3-Y),np.logical_and(Y>=1./3,Y<2./3))+np.multiply((Y-2./3),(Y>=2./3))

usol_2=np.multiply(Y,(Y<1./2))+np.multiply(1-Y,(Y>=1./2))
#usol_2=Y
#usol_2=np.multiply(X<Y,np.minimum(Y,1-X))+np.multiply(X>=Y,np.minimum(X,1-Y))
u_true_2 = usol_2.flatten('F')[:,None] 

# usol_3=np.abs(Y-X)
# u_true_3 = usol_3.flatten('F')[:,None] 


#usol_1 =X #solution chosen for convinience  
#u_true = usol_1.flatten('F')[:,None] 

#usol_2=np.multiply(np.sign(Y),1-np.cos(Y))
#u_true_2 = usol_2.flatten('F')[:,None] 

#usol_3=np.sin(np.abs(Y))
#u_true_3 = usol_3.flatten('F')[:,None] 


def trainingdata(N_u,N_f):
    
    leftedge_x = np.hstack((X[:,0][:,None], Y[:,0][:,None]))
    rightedge_x = np.hstack((X[:,-1][:,None], Y[:,-1][:,None]))
    topedge_x = np.hstack((X[0,:][:,None], Y[0,:][:,None]))
    bottomedge_x = np.hstack((X[-1,:][:,None], Y[-1,:][:,None]))
    all_X_u_train = np.vstack([leftedge_x, rightedge_x, bottomedge_x, topedge_x])


    leftedge_u = usol_1[:,0][:,None]
    rightedge_u = usol_1[:,-1][:,None]
    topedge_u = usol_1[0,:][:,None]
    bottomedge_u = usol_1[-1,:][:,None]
    all_u_train = np.vstack([leftedge_u, rightedge_u, bottomedge_u, topedge_u])  
     
    #choose random N_u points for training
    idx = np.random.choice(all_X_u_train.shape[0], N_u, replace=False) 
    X_u_train_1 = all_X_u_train[idx[0:N_u], :] #choose indices from  set 'idx' (x,t)
    u_train = all_u_train[idx[0:N_u],:]      #choose corresponding u_1 component
    
    leftedge_u = usol_2[:,0][:,None]
    rightedge_u = usol_2[:,-1][:,None]
    topedge_u = usol_2[0,:][:,None]
    bottomedge_u = usol_2[-1,:][:,None]
    all_u_train = np.vstack([leftedge_u, rightedge_u, bottomedge_u, topedge_u])  
     
    #choose random N_u points for training
    #idx = np.random.choice(all_X_u_train.shape[0], N_u, replace=False) 
    X_u_train_2 = all_X_u_train[idx[0:N_u], :] #choose indices from  set 'idx' (x,t)  
    u_train_2 = all_u_train[idx[0:N_u],:]      #choose corresponding u_2 component
    
    
    '''Collocation Points'''

    # Latin Hypercube sampling for collocation points 
    # N_f sets of tuples(x,t)
    X_f =lb+ (ub-lb)*lhs(2,N_f)
    X_f_train = np.vstack((X_f,X_u_train_1)) # append training points to collocation points 
    
    
    return X_f_train, X_u_train_1, u_train, u_train_2

class Sequentialmodel(nn.Module):
    
    def __init__(self,layers):
        super().__init__() #call __init__ from parent class 
              
        'activation function'
        self.activation = nn.ReLU()

        'loss function'
        self.loss_function =nn.MSELoss(reduction ='mean')
    
        'Initialise neural network as a list using nn.Modulelist'  
        self.linears = nn.ModuleList([nn.Linear(layers[i], layers[i+1]) for i in range(len(layers)-1)])
        
        '''
        Alternatively:
        
        *all layers are callable 
    
        Simple linear Layers
        self.fc1 = nn.Linear(2,50)
        self.fc2 = nn.Linear(50,50)
        self.fc3 = nn.Linear(50,50)
        self.fc4 = nn.Linear(50,1)
        
        '''
    
        'Xavier Normal Initialization'
        # std = gain * sqrt(2/(input_dim+output_dim))
        for i in range(len(layers)-1):
            
            # weights from a normal distribution with 
            # Recommended gain value for tanh = 5/3?
            nn.init.xavier_normal_(self.linears[i].weight.data, gain=1.0)
            
            # set biases to zero
            nn.init.zeros_(self.linears[i].bias.data)
            

    def forward(self,x):
        
        if torch.is_tensor(x) != True:         
            x = torch.from_numpy(x)                
        
        u_b = torch.from_numpy(ub).float().to(device)
        l_b = torch.from_numpy(lb).float().to(device)
                      
        #preprocessing input 
        x = (x - l_b)/(u_b - l_b) #feature scaling
        
        #convert to float
        a = x.float()
                        
        '''     
        Alternatively:
        
        a = self.activation(self.fc1(a))
        a = self.activation(self.fc2(a))
        a = self.activation(self.fc3(a))
        a = self.fc4(a)
        
        '''
        
        for i in range(len(layers)-2):
            
            z = self.linears[i](a)
                        
            a = self.activation(z)
            
        a = self.linears[-1](a)
        
        return a
                        

    

    def loss_BC_4(self,x_1,y_1,x_2,y_2):
        u = self.forward(x_1)
        u1=u[:,[0]]
        loss_u1 = self.loss_function(u1, y_1)
        u = self.forward(x_2)
        u2=u[:,[1]]
        loss_u2 = self.loss_function(u2, y_2)

        
        return loss_u1+loss_u2
    
    

    
    def loss_PDE_4(self, x_to_train_f):
                
        # x_1_f = x_to_train_f[:,[0]]
        # x_2_f = x_to_train_f[:,[1]]
                        
        g = x_to_train_f.clone()
       
        g.requires_grad = True
        
        u = self.forward(g)

        u1=u[:,[0]]
        u2=u[:,[1]]
        u3=u[:,[2]]

        u1_x = autograd.grad(u1,g,torch.ones([x_to_train_f.shape[0], 1]).to(device), retain_graph=True, create_graph=True)[0]
        u1_x_1 = u1_x[:,[0]]
        u1_x_2 = u1_x[:,[1]]
        
        u1_xx = autograd.grad(u1_x,g,torch.ones(x_to_train_f.shape).to(device), create_graph=True)[0]
                                                     
        u1_xx_1 = u1_xx[:,[0]]
         
        u1_xx_2 = u1_xx[:,[1]]
                                               
        u2_x = autograd.grad(u2,g,torch.ones([x_to_train_f.shape[0], 1]).to(device), retain_graph=True, create_graph=True)[0]
        u2_x_1 = u2_x[:,[0]]
        u2_x_2 = u2_x[:,[1]]
        
        u2_xx = autograd.grad(u2_x,g,torch.ones(x_to_train_f.shape).to(device), create_graph=True)[0]                                                     
        u2_xx_1 = u2_xx[:,[0]]
        u2_xx_2 = u2_xx[:,[1]]
                                          
        # q = ( -(a_1*np.pi)**2 - (a_2*np.pi)**2 + k**2 ) * torch.sin(a_1*np.pi*x_1_f) * torch.sin(a_2*np.pi*x_2_f)
                        
        f = u1_x_1*u1_x_1 + u1_x_2*u1_x_2-1
        loss_f = self.loss_function(f,f_hat)
        f2 = u2_x_1*u2_x_1 + u2_x_2*u2_x_2-1
        loss_f2 = self.loss_function(f2,f_hat)
        f3 = u1_x_1*u2_x_1 + u1_x_2*u2_x_2
        loss_f3 = self.loss_function(f3,f_hat)


        return loss_f+loss_f2+loss_f3
    

    def loss_4(self,x_1,y_1,x_2,y_2,x_to_train_f):

        loss_u = self.loss_BC_4(x_1,y_1,x_2,y_2)
        
        loss_f = self.loss_PDE_4(x_to_train_f)

        loss_val = loss_u + loss_f
        
        return loss_val
     
    'callable for optimizer'                                       
    def closure(self):
        
        optimizer.zero_grad()
        
        loss_val = self.loss(X_u_train_1, u_train,X_u_train_2,u_train_2, X_f_train)
        
        error_vec, _, _,_ = PINN.test()
        
        # print(loss,error_vec)
        
        loss_val.backward()

        return loss_val        
    
    def test(self):
                
        u_pred = self.forward(X_u_test_tensor)
        u_pred1=u_pred[:,[0]]
        u_pred2=u_pred[:,[1]]

        error_vec = torch.linalg.norm((u-u_pred1),2)/torch.linalg.norm(u,2)        # Relative L2 Norm of the error (Vector)
        
        u_pred1 = np.reshape(u_pred1.cpu().detach().numpy(),(256,256),order='F') 
        u_pred2 = np.reshape(u_pred2.cpu().detach().numpy(),(256,256),order='F') 

        return error_vec,u_pred1, u_pred2


def solutionplot(u_pred1,u_pred2,X_u_train,u_train):

    fig_1 = plt.figure(1, figsize=(18, 5))
    plt.subplot(1, 2, 1)
    plt.pcolor(x_1, x_2, u_pred1, cmap='jet')
    plt.colorbar()
    plt.xlabel(r'$x_1$', fontsize=18)
    plt.ylabel(r'$x_2$', fontsize=18)
    plt.title('u_1', fontsize=15)

    plt.subplot(1, 2, 2)
    plt.pcolor(x_1, x_2, u_pred2, cmap='jet')
    plt.colorbar()
    plt.xlabel(r'$x_1$', fontsize=18)
    plt.ylabel(r'$x_2$', fontsize=18)
    plt.title('u_2', fontsize=15)


def solutionsurf(u_pred1,u_pred2,X,Y):

    fig = plt.figure(1, figsize=(18, 5))
    
    ax = fig.add_subplot(121, projection='3d')

    surf = ax.plot_surface(X, Y, u_pred1, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
    
    ax = fig.add_subplot(122, projection='3d')

    surf = ax.plot_surface(X, Y, u_pred2, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)    
   


N_u = 200 #Total number of data points for 'u'
N_f = 600 #Total number of collocation points 

# Training data
X_f_train_np_array, X_u_train_np_array_1, u_train_np_array, u_train_2_np_array= trainingdata(N_u,N_f)

'Convert to tensor and send to GPU'
X_f_train = torch.from_numpy(X_f_train_np_array).float().to(device)
X_u_train_1 = torch.from_numpy(X_u_train_np_array_1).float().to(device)
X_u_train_2 = torch.from_numpy(X_u_train_np_array_1).float().to(device)

u_train = torch.from_numpy(u_train_np_array).float().to(device)
u_train_2 = torch.from_numpy(u_train_2_np_array).float().to(device)

X_u_test_tensor = torch.from_numpy(X_u_test).float().to(device)
u = torch.from_numpy(u_true).float().to(device)
f_hat = torch.zeros(X_f_train.shape[0],1).to(device)

layers = np.array([2, 200,200,200,200,3]) #3 hidden layers

PINN = Sequentialmodel(layers)
       
PINN.to(device)

'Neural Network Summary'

print(PINN)

params = list(PINN.parameters())

'''Optimization'''

'L-BFGS Optimizer'

# optimizer = torch.optim.LBFGS(PINN.parameters(), lr=0.1, 
#                               max_iter = 1000, 
#                               max_eval = None, 
#                               tolerance_grad = 1e-06, 
#                               tolerance_change = 1e-09, 
#                               history_size = 100, 
#                               line_search_fn = 'strong_wolfe')

# start_time = time.time()
# 
# optimizer.zero_grad()     # zeroes the gradient buffers of all parameters

# optimizer.step(PINN.closure)


'Adam Optimizer'

optimizer = optim.Adam(PINN.parameters(), lr=0.001,betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False)

max_iter = 10000

start_time = time.time()

for i in range(max_iter):
    # loss1 = PINN.loss_1(X_u_train_1, u_train,X_u_train_2,u_train_2, X_f_train)
    # optimizer.zero_grad()     # zeroes the gradient buffers of all parameters
    # loss1.backward() #backprop
    # optimizer.step()
    
    # loss2 = PINN.loss_2(X_u_train_1, u_train,X_u_train_2,u_train_2, X_f_train)
    # optimizer.zero_grad()     # zeroes the gradient buffers of all parameters
    # loss2.backward() #backprop
    # optimizer.step()
    
    # loss3 = PINN.loss_3(X_u_train_1, u_train,X_u_train_2,u_train_2, X_f_train)
    # optimizer.zero_grad()     # zeroes the gradient buffers of all parameters
    # loss3.backward() #backprop
    # optimizer.step()



    loss = PINN.loss_4(X_u_train_1, u_train,X_u_train_2,u_train_2,X_f_train)
    optimizer.zero_grad()     # zeroes the gradient buffers of all parameters
    loss.backward() #backprop
    optimizer.step()

    
    # loss = PINN.loss(X_u_train_1, u_train,X_u_train_2,u_train_2, X_f_train)
    # optimizer.zero_grad()     # zeroes the gradient buffers of all parameters
    # loss.backward() #backprop
    # optimizer.step()
    
    if i % (max_iter/100) == 0:

        error_vec,u_pred1,u_pred2 = PINN.test()
        solutionplot(u_pred1,u_pred2,X_u_train_1,u_train)
        plt.show()
        print(loss)
    
    
elapsed = time.time() - start_time                
print('Training time: %.2f' % (elapsed))


''' Model Accuracy ''' 
error_vec,u_pred1,u_pred2  = PINN.test()

print('Test Error: %.5f'  % (error_vec))


''' Solution Plot '''
solutionplot(u_pred1,u_pred2,X_u_train_1,u_train)

''' Solution Surf '''
solutionsurf(u_pred1,u_pred2,X,Y)

fig = plt.figure(figsize=(6,5))
ax = fig.add_subplot(111, projection='3d')

# Surface Plot


# ax.plot_surface(X, Y,u_pred1, cmap=cm.flag)
ax.scatter(u_pred1.flatten('F')[:,None] ,u_pred2.flatten('F')[:,None] )
# Labels


ax.set_xlabel('X-Axis')
ax.set_ylabel('Y-Axis')

# Display

plt.show()




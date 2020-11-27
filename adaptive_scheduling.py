import math
import numpy as np
from scipy.linalg import expm, inv
from scipy.optimize import minimize
from scipy.stats import poisson

def find_Salpha(mean, SCV, u):
    """
    Returns the transition rate matrix, initial distribution
    and parameters of the phase-fitted service times given
    the mean, SCV, and the time that the client is in service at time 0.
    """
    
    # weighted Erlang case
    if SCV < 1:
        
        # parameters
        K = math.floor(1/SCV)
        p = ((K + 1) * SCV - math.sqrt((K + 1) * (1 - K * SCV))) / (SCV + 1)
        mu = (K + 1 - p) / mean
        
        # initial dist. client in service
        alpha_start = np.zeros((1,K+1))
        B_sf = poisson.cdf(K-1, mu*u) + (1 - p) * poisson.pmf(K,mu*u)
        for z in range(K+1):
            alpha_start[0,z] = poisson.pmf(z,mu*u) / B_sf
        alpha_start[0,K] *= (1 - p) 
        
        # initial dist. other clients
        alpha = np.zeros((1,K+1))
        alpha[0,0] = 1
        
        # transition rate matrix
        S = -mu * np.eye(K+1)
        
        for i in range(K-1):
            S[i,i+1] = mu
        
        S[K-1,K] = (1-p) * mu
            
    # hyperexponential case
    else:
        
        # parameters
        p = (1 + np.sqrt((SCV - 1) / (SCV + 1))) / 2
        mu1 = 2 * p / mean
        mu2 = 2 * (1 - p) / mean
        
        # initial dist. client in service
        alpha_start = np.zeros((1,2))
        B_sf = p * np.exp(-mu1 * u) + (1 - p) * np.exp(-mu2 * u)
        alpha_start[0,0] = p * np.exp(-mu1 * u) / B_sf
        alpha_start[0,1] = 1 - alpha_start[0,0]
        
        # initial dist. other clients
        alpha = np.zeros((1,2))
        alpha[0,0] = p
        alpha[0,1] = 1 - p
        
        # transition rate matrix
        S = np.zeros((2,2))
        S[0,0] = -mu1
        S[1,1] = -mu2
            
    return S, alpha_start, alpha


def create_Sn(S, alpha_start, alpha, N):
    """
    Creates the matrix Sn as given in Kuiper, Kemper, Mandjes, Sect. 3.2.
    """

    m = S.shape[0]
    S_new = np.zeros(((N+1)*m, (N+1)*m))
    
    # compute S2
    S_new[0:m,0:m] = S
    S_new[m:2*m, m:2*m] = S
    S_new[0:m, m:2*m] = np.dot(np.matrix(-sum(S.T)).T,alpha_start)
    
    # compute Si
    for i in range(1,N+1):
        S_new[i*m:((i+1)*m), i*m:(i+1)*m] = S
        S_new[(i-1)*m:i*m, i*m:(i+1)*m] = np.dot(np.matrix(-sum(S.T)).T,alpha)
    
    return S_new


def Transient_EIEW(x, alpha_start, alpha, Sn, Sn_inv, omega, wis):
    """
    Computes the cost function given all parameters.
    """
    
    x = np.pad(x, (wis,0))
    
    N = x.shape[0]
    m = alpha.shape[1]
    EIEW = [0] * N
    P_alpha_F = alpha_start
    
    for i in range(1,N+1):
        EIEW[i-1] = omega * (x[i-1] + P_alpha_F @ np.sum(Sn_inv[0:i*m,0:i*m],1)) \
                             - P_alpha_F @ Sn_inv[0:i*m,0:i*m] @ np.sum(expm(Sn[0:i*m,0:i*m] * x[i-1]),1)
        
        P = P_alpha_F @ expm(Sn[0:i*m,0:i*m] * x[i-1])
        F = 1 - np.sum(P)
        if i <= N-1:
            P_alpha_F = np.hstack((P, alpha * F))
            
    return sum(EIEW)


def Transient_IA(SCV, u, omega, N, x0, wis=0):
    """
    Computes the optimal schedule.
    wis = waiting in system.
    """
    
    # sojourn time distribution transition rate matrices
    S, alpha_start, alpha = find_Salpha(1, SCV, u)
    Sn = create_Sn(S, alpha_start, alpha, N)
    Sn_inv = inv(Sn)
        
    # minimization
    if not x0:
        x0 = np.array([1.5] * (N - wis))
    
    cons = [{"type": "ineq", "fun": lambda x: x}]
    optimization = minimize(Transient_EIEW, x0, args=(alpha_start,alpha,Sn,Sn_inv,omega,wis), constraints=cons)
    x = optimization.x
    fval = optimization.fun
        
    return x, fval

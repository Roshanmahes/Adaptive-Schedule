import math, time
import numpy as np

from scipy.stats import poisson
from scipy.optimize import minimize, LinearConstraint  # optimization
from scipy.linalg import inv  # matrix inversion
from scipy.sparse.linalg import expm  # matrix exponential


def phase_parameters(mean, SCV, u):
    """
    Returns the initial distribution gamma and the transition rate
    matrix T of the phase-fitted service times given the mean, SCV,
    and the elapsed service time u of the client in service.
    """
    
    # weighted Erlang case
    if SCV < 1:
        
        # parameters
        K = math.floor(1/SCV)
        p = ((K + 1) * SCV - math.sqrt((K + 1) * (1 - K * SCV))) / (SCV + 1)
        mu = (K + 1 - p) / mean
        
        # initial distribution
        gamma_i = np.zeros((1,K+1))
        B_sf = poisson.cdf(K-1,mu*u) + (1 - p) * poisson.pmf(K,mu*u)
        for z in range(K+1):
            gamma_i[0,z] = poisson.pmf(z,mu*u) / B_sf
        gamma_i[0,K] *= (1 - p) 
        
        # transition rate matrix
        Ti = -mu * np.eye(K+1)
        for i in range(K-1):
            Ti[i,i+1] = mu
        Ti[K-1,K] = (1-p) * mu
            
    # hyperexponential case
    else:
        
        # parameters
        p = (1 + np.sqrt((SCV - 1) / (SCV + 1))) / 2
        mu1 = 2 * p / mean
        mu2 = 2 * (1 - p) / mean
        
        # initial distribution
        gamma_i = np.zeros((1,2))
        B_sf = p * np.exp(-mu1 * u) + (1 - p) * np.exp(-mu2 * u)
        gamma_i[0,0] = p * np.exp(-mu1 * u) / B_sf
        gamma_i[0,1] = 1 - gamma_i[0,0]
        
        # transition rate matrix
        Ti = np.zeros((2,2))
        Ti[0,0] = -mu1
        Ti[1,1] = -mu2
            
    return gamma_i, Ti


def create_Vn(gamma, T):
    """
    Creates the matrix Vn given the initial
    distributions and transition matrices.
    """
    
    # initialize Vn
    n = len(T)
    d = [T[i].shape[0] for i in range(n)]
    D = np.cumsum([0] + d)
    Vn = np.zeros((D[n], D[n]))
    
    # compute Vn recursively
    for i in range(1,n):
        Vn[D[i-1]:D[i], D[i-1]:D[i]] = T[i-1]
        Vn[D[i-1]:D[i], D[i]:D[i+1]] = np.matrix(-T[i-1] @ np.ones((d[i-1],1))) @ gamma[i]
    
    Vn[D[n-1]:D[n], D[n-1]:D[n]] = T[n-1]
    
    return Vn


def cost(x, EB, gamma, Vn, Vn_inv, omega, k, fixed_inter_times):
    """
    Evaluates the cost function given all parameters.
    """

    x = np.concatenate((fixed_inter_times, x))

    n = len(gamma)  # total number of clients
    x = np.pad(x,(k,0))  # add clients who are already in system
    D = np.cumsum([gamma_i.shape[1] for gamma_i in gamma])

    G = [0] * n
    P = [0] * (n - 1)

    G[0] = gamma[0]
    P[0] = G[0] @ expm(Vn[:D[0],:D[0]] * x[1])

    for i in range(1, n):

        F = 1 - np.sum(P[i-1])
        G[i] = np.hstack((P[i-1], gamma[i] * F))

        if i == n - 1:
            break

        P[i] = G[i] @ expm(Vn[:D[i],:D[i]] * x[i+1])

    ES = [-np.sum(G[i] @ Vn_inv[:D[i],:D[i]]) for i in range(n)]
    EW = [0] + [ES[i] - EB[i] for i in range(1,n)]
    EI = [0] + [x[i] + EW[i] - ES[i-1] for i in range(1,n)]

    return omega * np.sum(EI) + (1 - omega) * np.sum(EW)


def optimal_schedule(EB, SCV, omega, fixed_inter_times, tau, k=1, u=0):
    """
    Computes the optimal schedule, given that the
    first clients arrive according to the interarrival 
    times fixed_inter_times, after which the next client
    arrives (at least) after interarrival time tau.
    """
        
    N = len(EB)
    m = len(fixed_inter_times)

    if N == 1 and (k,u) == (1,0):  # system is idle, one client to schedule
        if not m:  ### TODO: redundant?
            return np.array([tau]), 0

    u_full = [u] + [0] * (N - 1)
    gamma, T = zip(*[phase_parameters(EB[i], SCV[i], u_full[i]) for i in range(N)])
    Vn = create_Vn(gamma, T)
    Vn_inv = inv(Vn)
    
    # initial guess minimization
    if m:
        x0 = np.array([tau] + [EB[i] for i in range(k+1+m,N)])
        lower_bounds = [tau] + [0] * (N-k-m-1)
    else:
        x0 = np.array([EB[0] + k] + [EB[i] for i in range(k+1,N)])
        lower_bounds = [tau] + [0] * (N-k-1)
    
    lin_cons = LinearConstraint(np.eye(N - k - m), lower_bounds, np.inf)
    cost_fun = lambda x: cost(x, EB, gamma, Vn, Vn_inv, omega, k, fixed_inter_times)
    tol = None if N <= 30 else 1e-4
    optim = minimize(cost_fun, x0, constraints=lin_cons, method='SLSQP', tol=tol)
    inter_times, optimal_cost = optim.x, optim.fun

    inter_times = np.concatenate((fixed_inter_times, inter_times))

    if (k,u) == (1,0):  # system is idle
        inter_times = np.pad(inter_times, (1,0))

    schedule = np.cumsum(inter_times)

    return schedule, optimal_cost

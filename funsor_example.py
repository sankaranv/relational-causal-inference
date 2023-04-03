from collections import OrderedDict

import torch
# import funsor
# from funsor.domains import reals, bint
# from funsor.gaussian import Gaussian
# from funsor.terms import Variable
# from funsor.torch import Tensor
# from funsor.ops import add, logaddexp

import pyro.distributions as dist
from pyro.distributions import constraints
import pyro

from matplotlib import pyplot as plt

def gaussian_mixture_model(x, i_z, prec_z, i_x, prec_x):
    x = Tensor(x, OrderedDict(), 'real')
    z = Variable('z', reals(2,3))
    c = Variable('c', bint(2))
    j = Variable('j', bint(50))
    logp_c = Tensor(torch.tensor([0.5,0.5]).log(), OrderedDict(c = bint(2)))
    logp_z = Gaussian(i_z, prec_z, OrderedDict(z = reals(3)))
    logp_xc = Gaussian(i_x, prec_x, OrderedDict(c = bint(2), z = reals(3), x = reals(3)))

    logp_x = logp_c + logp_xc(z = z[c], x = x[j])
    logp_x = logp_x.reduce(logaddexp, 'c').reduce(add, 'j')
    logp_x = logp_x + logp_z(z = z[c]).reduce(add, 'c')
    logp_x = logp_x.reduce(logaddexp, 'z')
    return logp_x

def marginalize_gaussian_model(sigma_sq = 1):

    x = Gaussian(0, sigma_sq)

def generate_data():

    n = 1000
    x = torch.randn(n,1)
    sigma = 4
    mu = 2
    x = x * sigma + mu
    return x

def model(params):
    mu = pyro.sample('mu', dist.Normal(params[0], params[1]))
    sigma = pyro.sample('sigma', dist.Gamma(torch.abs(params[2]), torch.abs(params[3])))
    return pyro.sample('x', dist.Normal(mu, sigma))

def guide(params):
    mu_prior_mean = pyro.param('mu_prior_mean', params[0])
    mu_prior_std = pyro.param('mu_prior_std', params[1], constraint=constraints.positive)
    sigma_prior_a = pyro.param('sigma_prior_a', params[2], constraint=constraints.positive)
    sigma_prior_b = pyro.param('sigma_prior_b', params[3], constraint=constraints.positive)

    mu = pyro.sample('mu', dist.Normal(mu_prior_mean, mu_prior_std))
    sigma = pyro.sample('sigma', dist.Gamma(sigma_prior_a, sigma_prior_b))
    x = pyro.sample('x', dist.Normal(mu, sigma))
    return x

if __name__ == "__main__":

    # marginalize_gaussian_model()
    x = generate_data()
    conditional_model = pyro.condition(model, data = {'x': x.flatten()})

    svi = pyro.infer.SVI(model=conditional_model,
                        guide=guide,
                        optim=pyro.optim.SGD({"lr": 0.00001, "momentum": 0.8}),
                        loss=pyro.infer.Trace_ELBO(),
                        )
    
    prior_params = torch.Tensor([0.0, 10.0, 1.0, 0.1])
    losses, mu_prior_mean_samples, mu_prior_std_samples, sigma_prior_a_samples, sigma_prior_b_samples = [], [], [], [], []
    pyro.clear_param_store()
    num_iterations = 5000

    for i in range(num_iterations):
        loss = svi.step(prior_params)
        losses.append(loss)
        mu_prior_mean_samples.append(pyro.param('mu_prior_mean').item())
        mu_prior_std_samples.append(pyro.param('mu_prior_std').item())
        sigma_prior_a_samples.append(pyro.param('sigma_prior_a').item())
        sigma_prior_b_samples.append(pyro.param('sigma_prior_b').item())

    # plt.figure(figsize=(12, 8))
    plt.plot(losses)
    plt.xlabel('iteration')
    plt.ylabel('loss')
    plt.title('ELBO')
    plt.show()




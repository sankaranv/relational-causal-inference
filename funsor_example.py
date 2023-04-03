import argparse

import torch
import sys
import funsor
import funsor.ops as ops
import funsor.torch.distributions as dist
from funsor.interpreter import reinterpret
from funsor.optimizer import apply_optimizer


def kalman_filter(args):
    funsor.set_backend("torch")

    # Declare parameters.
    trans_noise = torch.tensor(0.1, requires_grad=True)
    emit_noise = torch.tensor(0.5, requires_grad=True)
    params = [trans_noise, emit_noise]

    # A Gaussian HMM model.
    def model(data):
        log_prob = funsor.to_funsor(0.0)

        x_curr = funsor.Tensor(torch.tensor(0.0))
        for t, y in enumerate(data):
            x_prev = x_curr
            # print(y)
            # A delayed sample statement.
            x_curr = funsor.Variable("x_{}".format(t), funsor.Real)
            val1= dist.Normal(1 + x_prev / 2.0, trans_noise, value=x_curr)
            print(val1)
            log_prob += val1
            # print(val1)
            # print(log_prob)

            # Optionally marginalize out the previous state.
            if t > 0 and not args.lazy:
                log_prob = log_prob.reduce(ops.logaddexp, x_prev.name)

            # An observe statement.
            val2 = dist.Normal(0.5 + 3 * x_curr, emit_noise, value=y)
            log_prob += val2
            # print(log_prob.inputs)
            # print(val2)
            # print(log_prob)
            # sys.exit()

        # Marginalize out all remaining delayed variables.
        log_prob = log_prob.reduce(ops.logaddexp)
        return log_prob

    # Train model parameters.
    torch.manual_seed(0)
    data = torch.randn(args.time_steps)
    optim = torch.optim.Adam(params, lr=args.learning_rate)
    for step in range(args.train_steps):
        optim.zero_grad()
        if args.lazy:
            with funsor.interpretations.lazy:
                log_prob = apply_optimizer(model(data))   
            log_prob = reinterpret(log_prob)
        else:
            log_prob = model(data)
        assert not log_prob.inputs, "free variables remain"
        loss = -log_prob.data
        loss.backward()
        optim.step()
        if args.verbose and step % 10 == 0:
            print("step {} loss = {}".format(step, loss.item()))

def gaussian_funsor_elim():

    x1 = funsor.Variable("x_1", funsor.Real)
    x2 = funsor.Variable("x_2", funsor.Real)
    x3 = funsor.Variable("x_3", funsor.Real)

    # Prior over x1
    mu = funsor.Tensor(torch.tensor(0.0))
    sigma = torch.tensor(1., requires_grad=True)

    # Build joint over x1, x2, x3
    joint_log_prob = funsor.to_funsor(0.0)
    joint_log_prob += dist.Normal(mu, sigma, value=x1)
    joint_log_prob += dist.Normal(x1, sigma, value=x2)
    joint_log_prob += dist.Normal(x2, sigma, value=x3)

    # Marginalize
    marginalized_vars = set([x2.name])
    joint_log_prob = joint_log_prob.reduce(ops.logaddexp, reduced_vars=marginalized_vars)
    return joint_log_prob

if __name__ == "__main__":

    with funsor.interpretations.lazy:
        joint_log_prob = gaussian_funsor_elim()
        print("Inputs: ", joint_log_prob.inputs)
        print("Joint Dist: ", joint_log_prob)

    # parser = argparse.ArgumentParser(description="Kalman filter example")
    # parser.add_argument("-t", "--time-steps", default=10, type=int)
    # parser.add_argument("-n", "--train-steps", default=101, type=int)
    # parser.add_argument("-lr", "--learning-rate", default=0.05, type=float)
    # parser.add_argument("--lazy", action="store_false")
    # parser.add_argument("--filter", action="store_false")
    # parser.add_argument("-v", "--verbose", action="store_true")
    # args = parser.parse_args()
    # kalman_filter(args)
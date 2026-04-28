# DATA8003 Assignment Design

AutoResearch Agent for Improving Diffusion Sampling on CIFAR-10

### 1. Background

This assignment isolates the sampling problem in diffusion models. The dataset and pretrained model are fixed, and students are not asked to train a model. Instead, they will build a simple AutoResearch agent that explores better sampling strategies under fixed budgets and analyzes the search process. The emphasis is on running a working baseline, modifying the sampler, and interpreting results rather than building a large research system.

#### Students should:

- run a diffusion sampling baseline successfully;
- understand which parts of the sampling process can be modified;
- use a simple agent to propose and test modifications;
- analyze the experimental results clearly.

# 2. Base Setup

#### Recommended codebase:

- NVIDIA EDM repository: [https://github.com/NVlabs/edm](https://github.com/NVlabs/edm)
- Recommended checkpoint: [https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/baseline/baseline](https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/baseline/baseline-cifar10-32x32-uncond-vp.pkl) [-cifar10-32x32-uncond-vp.pkl](https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/baseline/baseline-cifar10-32x32-uncond-vp.pkl)
- Recommended reference for the AutoResearch loop: karpathy/autoresearch: [https://github.com/kar](https://github.com/karpathy/autoresearch) [pathy/autoresearch](https://github.com/karpathy/autoresearch)

The EDM repository and checkpoint are the recommended base for the diffusion model and evaluation setup. karpathy/autoresearch is recommended as a reference for the research loop because it illustrates the cycle "propose a change → run an experiment → read the result → decide what to try next." You will likely need to simplify or modify that structure for this assignment. You may also design your own AutoResearch agent from scratch, or use another GitHub AutoResearch-style agent if you believe it is better suited to this task.

#### Fixed setting:

• Dataset: CIFAR-10

• Pretrained model: course-provided checkpoint

• Model architecture and weights: fixed

• Random seeds: fixed

• Budget cases: NFE ≤ 50 and NFE ≤ 20

Here NFE means number of function evaluations, i.e., the total number of diffusion model calls during sampling. The budget is defined by NFE, not by the number of loop iterations in code. You should consider both cases throughout the assignment: a moderate-budget case with NFE ≤ 50 and a low-budget case with NFE ≤ 20.

### 3. Task

Using the fixed CIFAR-10 pretrained diffusion model, modify only the sampling algorithm and improve sample quality under the two budget settings NFE ≤ 50 and NFE ≤ 20. You should analyze the exploration process of your AutoResearch agent and compare the behavior of your method in the two cases.

### 4. What Can and Cannot Be Modified

#### Allowed modifications:

- timestep or noise schedule;
- update rule at each step;
- solver type, such as Euler, Heun, or multistep methods;
- whether to use stochastic or noise-injected updates during sampling;
- how the limited budget is allocated across the sampling trajectory;
- smart manipulation of the score function during sampling, as long as it only uses the given pretrained model and does not require retraining;
- other hyperparameters directly related to sampling.

#### Not allowed:

- retraining the diffusion model;
- changing the network architecture;
- using extra training data;
- introducing an extra guidance model;
- manually selecting images as the final result.

# 5. Minimum Requirement for the AutoResearch Agent

Implement a simple AutoResearch agent that performs the following loop:

- 1. read the current sampler configuration;
- 1. propose a new sampler modification;
- 1. run generation and evaluation;
- 1. record the result;
- 1. use the result to decide the next modification.

The AutoResearch agent does not need to be sophisticated, but it should reflect the basic workflow

hypothesis → sampler change → experiment → analysis

### 6. Evaluation

The main metric is FID. To keep the workload manageable, all students can be required to:

- use a fixed set of random seeds;
- generate a fixed number of samples, for example 5,000;
- use course-provided reference statistics for evaluation.

Evaluation should be reported for both budget cases:

- Case 1: NFE ≤ 50;
- Case 2: NFE ≤ 20.

At minimum, students should report:

- the FID of the baseline sampler for both budget cases;
- the best FID achieved by their method for both budget cases;
- the improvement over the baseline in each case.

## 7. Submission

Students should submit:

- code;
- instructions for running the code;
- experiment logs;
- a short report.

The report should be about 2–4 pages and answer at least the following questions:

- 1. What is the baseline, and what is its FID?
- 1. What modifications did the AutoResearch agent try?
- 1. Which modifications helped, and which did not?
- 1. How do you interpret these results?
- 1. How much did your final sampler improve over the baseline?

### 8. Grading

- 40%: final result (whether the method improves over the baseline FID);
- 40%: process analysis (whether the agent's attempts and outcomes are analyzed clearly);
- 20%: code quality and reproducibility (whether the submission runs cleanly and is easy to follow).


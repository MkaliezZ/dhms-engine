# DHMS Isolation Spec v1

## 1. Memory Model

DHMS defines memory as a bounded informational condition that may influence a model's observable response to a given input. Memory is not identified with storage, retrieval, persistence, or any particular mechanism. It is defined only by its theoretical role: the presence, absence, or alteration of prior informational context relative to an otherwise fixed input condition.

A memory state is the conceptual set of information made available to the model prior to response formation. It may include retained facts, prior interactions, latent associations, contextual framing, or externally supplied records, provided that such information can be treated as distinct from the immediate input under evaluation.

Memory in DHMS is therefore a controlled variable. Its relevance is established only through differences in output behavior under matched input conditions. DHMS does not require memory to be human-like, explicit, complete, or introspectable. It requires only that memory be separable as an experimental condition.

## 2. Perturbation Model

A perturbation is a deliberate modification of the memory condition while preserving the immediate input condition. A valid perturbation changes only the memory-relevant informational context and does not alter the evaluated input itself.

Perturbations may vary in presence, absence, specificity, consistency, salience, or conflict within the memory condition. A perturbation is valid only if it is attributable to the memory condition rather than to changes in the input, task framing, evaluation criterion, or observational procedure.

Perturbations must be well-bounded. Each perturbation must have a defined target, a defined direction of alteration, and a defined relation to the unperturbed memory condition. A perturbation is invalid if its behavioral effect cannot be distinguished from ordinary variation in input interpretation.

## 3. Experimental Regimes

DHMS-A is the baseline regime. In this condition, the model is observed under the immediate input condition without a memory perturbation. DHMS-A establishes the reference behavior against which other regimes are compared.

DHMS-B is the perturbed-memory regime. In this condition, the immediate input remains identical to DHMS-A, while the memory condition is modified by a valid perturbation. DHMS-B measures the behavioral effect of altered memory under input invariance.

DHMS-C is the isolation-control regime. In this condition, the immediate input remains identical to DHMS-A and DHMS-B, while the memory condition is constrained to test whether observed behavioral differences are specifically attributable to the perturbation rather than to uncontrolled contextual variation.

Across DHMS-A, DHMS-B, and DHMS-C, input identity is mandatory. Any comparison in which the evaluated input differs across regimes is outside the DHMS specification.

## 4. Output Behavior Space

DHMS observes model outputs as behavioral traces. A behavioral trace is the externally observable response produced under a specified regime for a fixed input condition.

The output behavior space consists of properties of these traces, including content, stance, specificity, continuity, contradiction, uncertainty, reference behavior, and response structure. DHMS treats outputs as observations, not as explanations of internal state.

No claim about the internal cause of a behavioral trace is valid unless it is grounded in cross-regime comparison under input identity. The object of observation is therefore not memory itself, but the behavioral consequences of controlled memory conditions.

## 5. Metrics (Conceptual Only)

DHMS metrics describe differences and invariances in behavioral traces across regimes. Metrics are conceptual criteria for evaluation, not commitments to a particular measurement procedure.

Relevant metric categories include:

- Stability: the degree to which behavior remains consistent under repeated observation of the same regime.
- Sensitivity: the degree to which behavior changes when the memory condition is perturbed.
- Specificity: the degree to which observed change is attributable to the intended perturbation rather than unrelated variation.
- Continuity: the degree to which output behavior preserves coherent relation to the fixed input across regimes.
- Contradiction: the degree to which a regime introduces mutually incompatible claims or positions.
- Memory Dependence: the degree to which output behavior differs as a function of memory condition while input remains fixed.
- Isolation Strength: the degree to which the evaluation separates memory effects from non-memory effects.

Metrics must remain deterministic in interpretation: the same set of observed traces under the same regime definitions must support the same evaluation judgment.

## 6. Evaluation Protocol

A DHMS evaluation proceeds as a conceptual sequence:

1. Define the immediate input condition to be held constant.
2. Define the baseline memory condition corresponding to DHMS-A.
3. Define a valid memory perturbation for DHMS-B.
4. Define an isolation-control memory condition for DHMS-C.
5. Observe behavioral traces under DHMS-A, DHMS-B, and DHMS-C using the identical input condition.
6. Compare traces only across regimes with verified input identity.
7. Evaluate behavioral differences according to the conceptual metric categories.
8. Attribute memory dependence only when DHMS-B differs from DHMS-A in a manner not reproduced by DHMS-C.
9. Treat any unresolved ambiguity as a limit of the evaluation rather than as evidence of memory effect.

A DHMS claim is valid only if it preserves regime separation, input identity, perturbation boundedness, and observational consistency. Any claim that depends on implementation assumptions, unobserved internal states, or uncontrolled variation lies outside the scope of DHMS Isolation Spec v1.

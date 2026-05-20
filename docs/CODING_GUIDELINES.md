# Coding Guidelines

Symmetry follows a very strict set of coding guidelines to keep the maintainability of the backend at a high level. These guidelines are largely inspired by:
- [Clean Code Notes](https://github.com/JuanCrg90/Clean-Code-Notes)
- *Clean Code* by Robert C. Martin
- The pain of debugging large Django codebases at 3am.

## Who enforces these guidelines?
These guidelines are enforced by code reviewers (senior engineers) on a per-pull-request basis.

*This of course does not apply to this test — you are reviewing your own work.*

## What are the consequences of violating these guidelines?
Any violation can result in requests for changes in your pull request, a rejected pull request, or in the worst case, a closed one.

In the context of this test: each violation we spot in your submission is a request-for-changes we would have written if this were a real PR. The fewer, the better.

## The Guidelines
*Reviewers refer to these as `CG{n}` in PR comments. `CG3.2` means "rule 3, sub-rule 2".*

### CG1 — Always apply the Boy Scout Rule
The Boy Scout Rule says **"always leave the campground cleaner than you found it"**.

If you update a feature whose tests are missing, you write them. If you find a smell next to the line you came to change, you fix it — or at the very least, you flag it in the PR description. This is a requirement of the job, not an extra-credit task.

### CG2 — One feature, one folder
Every endpoint lives in its own folder under `<app>/features/<action>_<noun>_feature/`.

  - **CG2.1** Folder structure:
    ```
    <feature>/
    ├── __init__.py                  Re-exports the public service callable.
    ├── api/
    │   ├── <feature>_api.py         The APIView. HTTP concerns only.
    │   └── <feature>_serializers.py Input + output serializers.
    ├── services/
    │   └── <action>.py              The business logic, importable from outside.
    └── tests/
    ```
  - **CG2.2** Reading the whole feature should require opening **one folder**. If you find yourself jumping across five apps to follow a request, the feature is wrong.
  - **CG2.3** Logic that genuinely needs to live in more than one feature is promoted to `<app>/core/services/`. The bar for promotion is "two real callers", not "I might need this later".
  - **CG2.4** Public service callables are re-exported from `__init__.py`. The pattern `from <app>.features.<feature> import <callable>` should be the only import other code needs. Internal helpers stay private (`_helper_x`).

### CG3 — Views handle HTTP, services handle work
The view layer and the service layer have non-overlapping responsibilities. Crossing them is a smell.

  - **CG3.1** The `APIView` may: read query params, validate the input serializer, raise `NotAuthenticated` / `NotFound` / `PermissionDenied`, delegate to a service, serialize the result.
  - **CG3.2** The service may: query the ORM, mutate state, raise domain exceptions, call other services.
  - **CG3.3** A view that touches `Model.objects.filter(...)` "to save a step" is a violation of CG3.1. A service that imports `rest_framework` is a violation of CG3.2.
  - **CG3.4** Services raise **domain** exceptions; the view translates them to HTTP. Services that raise DRF exceptions are services that have leaked their layer.

### CG4 — Validation in the serializer, persistence in the service
The input serializer's job is to turn the request body into a typed, validated value. The view passes that value to the service.

  - **CG4.1** The cleanest pattern in this codebase is:
    ```python
    class CreateXInputSerializer(serializers.Serializer):
        ...

        def to_domain_input(self) -> CreateXInput:
            return CreateXInput(...)
    ```
  - **CG4.2** Validation never touches the database. Serializers do not call `.save()` and do not make ORM queries.
  - **CG4.3** Persistence never re-validates input shapes. The service trusts what it received.

### CG5 — Names earn their length
- **CG5.1** A function called `process_data` does not deserve to be on `git blame`. Use intention-revealing names.
- **CG5.2** A variable called `tmp` is only allowed inside a 5-line block where its meaning is obvious from context.
- **CG5.3** A boolean argument called `flag` is wrong. If you need a boolean, the name says what it controls: `atomic=True`, `include_drafts=True`.
- **CG5.4** Local style is American English, not abbreviated. `workout_session`, not `ws`. `exercise_template`, not `etmpl`.
- **CG5.5** Class names are nouns. Function names are verbs. `WorkoutSession`, `create_workout_session`.

### CG6 — Use the database to express invariants
- **CG6.1** If the rule is "a user cannot follow themselves," it lives in a `CheckConstraint`. If the rule is "at most one active routine per user," it lives in a `OneToOneField`.
- **CG6.2** Python code can rely on those guarantees and stop guarding against impossible states.
- **CG6.3** Never catch `IntegrityError` to paper over a missing constraint. Either the constraint exists (and the catch is dead code), or the constraint is missing (and the catch is hiding a bug).

### CG7 — Read paths prefetch, write paths transact
- **CG7.1** Any view that serializes a child collection must `prefetch_related` it. The detail endpoint for a workout session is the local template — copy the shape of its `get_workout_details` service.
- **CG7.2** Any view that returns counts must use `annotate(Count(...))`. Counting in Python is a request-for-changes.
- **CG7.3** Any service that touches more than one row must wrap the work in `transaction.atomic`. The `create_workout_session` service is the local template.

### CG8 — Tests communicate intent
- **CG8.1** Test names describe the contract under test, not the implementation:
    ```python
    def test_user_cannot_follow_themselves():
        ...

    def test_private_workout_returns_404_for_non_owner():
        ...
    ```
  Both forms are better than `test_follow_user_view_post_400`. Behavior-first naming wins.
- **CG8.2** Tests live inside the feature folder they cover, not in a sibling tree.

---

## What this codebase is *not* strict about
You will find features in this repo that bend (or break) these rules on purpose. They are intentional and serve to test whether you notice and why. Calling them out, leaving them alone, or refactoring them are all defensible choices. Not noticing is the one that isn't.

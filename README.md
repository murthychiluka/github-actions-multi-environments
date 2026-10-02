```text

                    Git Push
                       │
                       ▼
                 Build + Test
                       │
                    Success
                       │
                       ▼
                      DEV
                  APP_ENV=dev
                       │
                    Success
                       │
                       ▼
                       QA
                  APP_ENV=qa
                       │
                    Success
                       │
                       ▼
              ┌─────────────────┐
              │ PROD APPROVAL   │
              │                 │
              │ @murthychiluka  │
              │     APPROVED    │
              └────────┬────────┘
                       │
                       ▼
                      PROD
                  APP_ENV=prod
```
```text

GitHub Actions Multi-Environment Lab — Key Pointers
1. Repository structure
.github/
└── workflows/
    ├── main.yml
    ├── build-test.yml
    └── deploy.yml

Important: reusable workflows must be directly under .github/workflows/; don't put them inside a templates/ subdirectory.
```
```text
2. main.yml = pipeline orchestration
Its job is to control the flow:
Build/Test → DEV → QA → PROD

Example:
jobs:

  build-test:
    uses: ./.github/workflows/build-test.yml

  deploy-dev:
    needs: build-test
    uses: ./.github/workflows/deploy.yml
    with:
      environment: dev

  deploy-qa:
    needs: deploy-dev
    uses: ./.github/workflows/deploy.yml
    with:
      environment: qa

  deploy-prod:
    needs: deploy-qa
    uses: ./.github/workflows/deploy.yml
    with:
      environment: prod
```
```text

3. needs controls sequencing
needs: build-test

means:
Run this job only after build-test succeeds.

Therefore:
build-test
    ↓
deploy-dev
    ↓
deploy-qa
    ↓
deploy-prod

```
```text

4. Reusable workflow = GitHub Actions equivalent of a template concept
build-test.yml:
on:
  workflow_call:

deploy.yml:
on:
  workflow_call:

These workflows are called by main.yml rather than triggered directly by a push.
Call them using:
uses: ./.github/workflows/deploy.yml
```
```text
5. Pass values using with
main.yml:
with:
  environment: dev

The reusable workflow declares:
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

Then uses:
${{ inputs.environment }}

Think:
main.yml
   │
   │ environment: dev
   ▼
deploy.yml
   │
   │ inputs.environment
   ▼
GitHub Environment: dev

```
```text
6. GitHub Environments
You created:
dev
qa
prod

Each can have its own:
- Variables
- Secrets
- Deployment protection rules
- Required reviewers
- Environment-specific configuration
Your example:
dev
 └── APP_ENV=dev

qa
 └── APP_ENV=qa

prod
 └── APP_ENV=prod
```

```text
7. Environment variables
Access environment variables with:
${{ vars.APP_ENV }}

For example:
- name: Show environment
  run: |
    echo "Environment = ${{ vars.APP_ENV }}"

The value changes according to the selected GitHub Environment.

```
```text
8. Secrets
Use:
${{ secrets.SECRET_NAME }}

for sensitive information such as:
API keys
Passwords
Cloud credentials
SSH keys
Database credentials

```
```text

Never hard-code secrets in YAML or application code.
9. Production approval
Your prod environment has:
Required reviewer
       ↓
@murthychiluka

Therefore:
Build
  ↓
DEV
  ↓
QA
  ↓
⏸ PROD approval
  ↓
PROD

This is one of the most important real-world concepts from this lab.

```
```text
10. The big picture
Remember this architecture:
                 GitHub Actions
                       │
                       ▼
                   main.yml
                  /         \
                 /           \
                ▼             ▼
       build-test.yml     deploy.yml
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
                DEV          QA           PROD
                 │            │             │
              variables    variables     variables
                                            │
                                         approval
```
```text
11. Azure DevOps → GitHub Actions mapping
Since you're also learning Azure DevOps, this comparison is useful:
Azure DevOps	GitHub Actions
azure-pipelines.yml	main.yml
Template	Reusable workflow
template.yml	workflow_call workflow
Stage	Job / environment flow
Variables	vars / env
Variable groups	Variables/secrets
Secret variables	Secrets
Environment	Environment
Approvals	Environment required reviewers
dependsOn	needs
Pipeline task	Action / run step
Agent pool	runs-on

```
```text

12. Most important lessons from this lab
If you remember only these 8 points, you're in good shape:
1. main.yml = orchestrator
2. workflow_call = reusable workflow
3. uses = call reusable workflow
4. needs = dependency/order
5. with = pass inputs
6. vars = configuration
7. secrets = sensitive configuration
8. environment protection = production approval

And the final mental model:
Don't duplicate the pipeline for DEV, QA and PROD. Create reusable workflows once, then pass the environment as an input and let GitHub Environment configuration provide the environment-specific values.

That pattern is directly applicable when you later build AWS, Azure, or GCP deployment pipelines.
```
```text
I have a query  in the build-test.yml:  we have run tests. How will this be called to test_app.py?
 name: Run tests
        run: |
          pytest

Yes. This is an important point to understand because pytest automatically discovers test_app.py. You don't explicitly call test_app.py in the YAML.
What happens in your build-test.yml

You have:

- name: Run tests
  run: |
    pytest

When GitHub Actions reaches this step, the runner is already in your repository's working directory because of:

- name: Checkout code
  uses: actions/checkout@v4

So the runner has something like:
repository/
├── app.py
├── requirements.txt
├── test_app.py
└── .github/
    └── workflows/
        └── ...
```
```text

Then this command:

pytest

starts the pytest test runner.
How does pytest find test_app.py?

By default, pytest uses test discovery rules.

A file named:
test_app.py

matches pytest's default test-file pattern:
test_*.py

So pytest finds:
test_app.py

Then inside it, suppose you have:
from app import app


def test_home():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200

Pytest discovers:
test_home()

because its name starts with:
test_

So the chain is:
GitHub Actions
      │
      ▼
run:
  pytest
      │
      ▼
pytest test discovery
      │
      ▼
test_app.py
      │
      ▼
test_home()
      │
      ▼
assert response.status_code == 200
Why don't we write this?

You could technically write:

- name: Run tests
  run: |
    pytest test_app.py

That explicitly tells pytest:

    Run the tests in test_app.py.

But:

run: |
  pytest

is more commonly used because pytest automatically discovers all matching test files.

For example, if tomorrow you add:
test_app.py
test_api.py
test_database.py
test_security.py

you don't need to modify your YAML.

Just:

pytest

will discover them.
pytest
 │
 ├── test_app.py
 │     └── test_home()
 │
 ├── test_api.py
 │     ├── test_get_books()
 │     └── test_create_book()
 │
 ├── test_database.py
 │     └── test_connection()
 │
 └── test_security.py
       └── test_headers()
One more important thing in your workflow

Before pytest runs, we install the dependencies:

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt

So if requirements.txt contains:
Flask
pytest

the GitHub runner gets both Flask and pytest.

Therefore:
requirements.txt
       │
       ▼
pip install
       │
       ├── Flask
       └── pytest
                  │
                  ▼
             pytest command
                  │
                  ▼
             test_app.py

In short: pytest is the test runner; test_app.py is the test file; test_home() is the individual test. Pytest's discovery rules connect them automatically.
```

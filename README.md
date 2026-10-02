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

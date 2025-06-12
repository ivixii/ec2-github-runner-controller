# EC2 GitHub Actions Runner Controller (Container Mode)

This project allows you to run GitHub Actions self-hosted runners as containers on a single EC2 instance, using the `container:` definition from the workflow job.

👉 Example of a supported job:

```yaml
jobs:
  build:
    runs-on: [self-hosted, linux]
    container: node:20
    steps:
      - run: node -v
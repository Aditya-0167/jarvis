# JARVIS CLOUD START

This package is designed so your PC does not have to stay on after you upload
the project to a public GitHub repository.

## Steps

1. Create a GitHub account.
2. Create a PUBLIC repository named `jarvis`.
3. Upload every file inside this folder to the repository root.
4. Open the repository's Actions tab.
5. Enable actions if GitHub asks.
6. Choose **JARVIS Continuous Development**.
7. Click **Run workflow**.

The workflow:
- starts a fresh temporary Linux runner
- installs Python and PyTorch CPU
- resumes the latest checkpoint/state from the repo
- trains the from-scratch model
- evolves the software-level mind
- commits the new state
- ends
- resumes on the next scheduled/manual run

Your Windows PC can be turned off after the upload.

## Reality check

GitHub-hosted compute is temporary. This project therefore uses checkpoint/resume
instead of pretending to have one permanent machine.

Standard runners are free for public repositories, but they have finite resources
and job-duration limits. This is suitable for experimentation, not unlimited
frontier-model training.

Do NOT put passwords, API keys, private data, or other secrets in the repository.

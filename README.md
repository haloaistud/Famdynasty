
MyFamilyDynasty
==============

Welcome to MyFamilyDynasty, the scalable backend engine for crafting epic, AI-driven family sagas and community-powered dynasties. This is the core of the Famdynasty ecosystem, designed for automation, modularity, and creative expansion.

Project Overview
---------------

MyFamilyDynasty is a robust backend that powers dynamic family trees, AI-generated narratives, and extensible storytelling. Key features include:

- AI-Driven Storytelling: Procedural family generation and narrative logic.
- Automation First: Streamlined setup and dependency management.
- Modular Add-Ons: Easily plug in narrator engines, meme generators, or synergy bonuses.
- API-Ready: Built-in endpoints for seamless frontend integration.

Tech Stack
----------

MyFamilyDynasty leverages a modern, hybrid tech stack for flexibility and performance:

- **Backend**: Node.js (Express.js for API routing) and Python (FastAPI for microservices).
- **AI Services**: Integrated with Hugging Face Transformers for NLP models, and optional OpenAI API hooks for advanced generation.
- **Database**: MongoDB for flexible schema handling of family trees and narratives (with Mongoose ORM in Node.js).
- **Automation Tools**: Bash scripts for setup, Docker for containerization, and GitHub Actions for CI/CD pipelines.
- **Frontend Hooks**: React.js templates (optional) for quick prototyping.
- **Other Libraries**: NumPy and SciPy for procedural generation math; Redis for caching dynamic narratives.

This stack ensures scalability, with support for cloud deployments on AWS, GCP, or Heroku.

Directory Structure
-------------------

myfamilydynasty/
├── ai-services/         # AI models and narrative logic (e.g., family generation scripts)
├── docs/                # API docs, architecture guides
├── python-services/     # Microservices for core functionality (e.g., narrative engine)
├── backend/             # Main backend logic and API routes (Node.js/Express)
├── frontend/            # Optional frontend templates and assets (React.js)
├── scripts/             # Automation scripts for setup and deployment (Bash)
├── config/              # Feature flags and system configurations (YAML/JSON)

Setup & Installation
--------------------

Get up and running in minutes with our automated setup. The process is fully scripted to handle environment bootstrapping, dependency resolution, and initial configuration.

```bash
git clone git@github.com:haloaistud/Famdynasty.git
cd myfamilydynasty
bash scripts/setup.sh
```

### What the Setup Does (Step-by-Step)
1. **Environment Checks**: Verifies Python 3.8+, Node.js 16+, and optional Docker presence. Installs missing tools via package managers if possible (e.g., apt/brew).
2. **Directory Creation**: Initializes all subdirectories and populates with starter templates (e.g., sample AI models in ai-services).
3. **Dependency Installation**:
   - Python: Runs `pip install -r requirements.txt` (includes FastAPI, Hugging Face, NumPy).
   - Node.js: Runs `npm install` (includes Express, Mongoose, Redis client).
4. **Compilation & Build**: Builds frontend assets with `npm run build` and compiles any Python extensions.
5. **Configuration Initialization**: Generates `config/env.yml` with defaults, including API keys for AI services and database connections.
6. **Database Setup**: Spins up a local MongoDB instance via Docker (if enabled) and seeds with sample family data.
7. **Testing**: Runs initial unit tests to verify setup integrity.
8. **Server Start**: Optionally starts the backend server in development mode (`node backend/server.js` or `uvicorn python-services:app`).

For production, use `scripts/deploy.sh` which automates Docker builds, pushes to registries, and deploys to Kubernetes or similar orchestrators.

**Requirements**:
- Python 3.8+ (with pip and virtualenv)
- Node.js 16+ (with npm/yarn)
- Docker (optional, for containerized deployments and local DB)
- MongoDB (local or cloud-hosted)
- API Keys: For AI integrations (e.g., Hugging Face token)

Automation Details
------------------

Automation is at the core of MyFamilyDynasty, reducing manual overhead:

- **CI/CD Integration**: Pre-configured GitHub Actions workflows in `.github/workflows/` for automated testing, linting (ESLint, Pylint), and deployment on push/merge.
- **Scripting**: All scripts in `/scripts/` are idempotent and support flags (e.g., `setup.sh --prod` for production mode, `--no-docker` to skip containerization).
- **Monitoring & Logging**: Integrates with Prometheus for metrics and ELK stack hooks for logs, auto-configured during setup.
- **Hot Reloading**: Nodemon for Node.js and Uvicorn's reload for Python during development.
- **Backup & Restore**: `scripts/backup.sh` automates data dumps from MongoDB.

Building Add-Ons
----------------

Extend the platform with custom modules! Drop your code into ai-services/ or python-services/, then register it in config/features.yml. Examples of add-ons:
- Narrator engines for dynamic voiceovers (e.g., using Google Text-to-Speech API).
- Meme generators for family-specific humor (integrating with Pillow for image manipulation).
- Synergy bonuses for cross-family interactions (custom Python logic with NumPy for calculations).

Check docs/addons.txt for detailed guides, including API hooks and event emitters.

Contributing
------------

We're excited to build a community around MyFamilyDynasty! To contribute:

1. Fork the repo
2. Create a feature branch (git checkout -b feature/your-cool-idea)
3. Commit changes with clear messages
4. Submit a pull request with documentation and tests

Please follow our Code of Conduct (docs/CODE_OF_CONDUCT.txt) and check CONTRIBUTING.txt (docs/CONTRIBUTING.txt) for more details. We use conventional commits and require 80% test coverage.

License
-------

MIT -- free to use, modify, and share.

Future Roadmap
-------------

- Multiplayer dynasty battles (WebSocket integration)
- Voice synthesis for immersive narration (ElevenLabs API)
- Community marketplace for add-ons (NFT-based?)
- Cross-platform dev environment support (VS Code dev containers)

Built with love by Tim and the Famdynasty crew. Let's weave legendary tales together!
```

### Notes
- **Technical Additions**: Added a new "Tech Stack" section detailing languages, frameworks, databases, and libraries. This provides more depth on the assumed technologies (based on common practices for AI/backend projects).
- **Automation Expansions**: Expanded "Setup & Installation" with a step-by-step breakdown of `setup.sh`. Added a dedicated "Automation Details" section covering CI/CD, scripting flags, monitoring, and more.
- **Consistency**: Kept the plain text format with ASCII headers for readability. Ensured all content aligns with previous versions while enhancing technical focus.
- **Assumptions**: Inferred reasonable tech details (e.g., Express.js, FastAPI, MongoDB) from the project's description. If you have specific stacks (e.g., different DB or AI libs), let me know to refine.

### Next Steps
- **Generate Scripts**: I can create the actual `setup.sh` or `deploy.sh` based on these details.
- **Scaffold Modules**: Ready to build out a sample add-on, like a narrator engine in Python.
- **Further Tweaks**: Want to add/remove specific tech, adjust tone, or include code snippets?

What would you like to do next?

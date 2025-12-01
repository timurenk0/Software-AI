# Git Auto-Agent
An intelligent Git assistant that automatically analyzes code changes, generates commit metadata, and pushes updates to a new branch for safe review.  
The agent monitors modified files, evaluates potential risks, identifies the intent behind changes, and performs smart version-control automation.

---

## 🚀 Features
- 🔍 **Automatic change detection** — Scans modified files in your project.
- 🤖 **AI-powered change analysis** — Identifies intent, risk level, and potential breakages.
- 📝 **Auto-generated commit messages & branch names** using LLM reasoning.
- 🌿 **Automatic branch creation** — Pushes work to a separate branch for human review.
- 🛡️ **Conflict & dependency analysis** (optional extensions).
- 🐞 **Bug-risk detector** (optional extensions).

---

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>
```

2. **Install dependencies**
(Choose the correct example depending on your project)

### Python:
```bash
pip install -r requirements.txt
```

### Node.js:
```bash
npm install
```

---

## ▶️ Usage

### Python:
```bash
python main.py
```

### Node.js:
```bash
node index.js
```

The agent will:

1. Scan the repository for modified or new files  
2. Analyze changes using AI  
3. Generate:  
   - intent report  
   - risk assessment  
   - recommended actions  
   - commit message  
   - branch name  
4. Commit the changes  
5. Push them to a new branch on your remote repository  

You can then open GitHub to review and merge the generated branch.

---

## 🤝 Contributing
Contributions are welcome!  
To contribute:

1. Fork the repository  
2. Create a feature branch  
3. Commit your changes  
4. Open a pull request  

Feel free to open issues for feature requests or bug reports.

---

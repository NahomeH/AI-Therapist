Hi! 👋 We’re building Talk2Me, an affordable AI therapy solution which can serve as an on-demand, low-cost resource for crisis support, emotional expression, and preliminary mental health insights. Continue reading to learn how to run our agent!

Info on general sprint progress and individual contributions are in the `progress` folder.

[Link to Sprint 3 progress and contributions](https://github.com/winsonc7/CS224G/blob/main/progress/SPRINT_THREE.md)

# Project Setup 🤖

## 1. Clone repo

To begin, clone the repository to your local machine using the following command:
```bash
  git clone https://github.com/winsonc7/CS224G.git
```

## 2. Set up environment variables and authentication

### a. Obtain an OpenAI API key

To run the agent, you'll need an OpenAI API key.

### b.  Save API keys in .env files

  Store your OpenAI API key, along with our Supabase URL/key (provided below) in TWO `.env` files. Follow these steps:

- Create a .env file in the root directory

  In this .env file, add your OpenAI API key, as well as our Supabase environment variables:
  ```
  OPENAI_API_KEY=xxxxx
  SUPABASE_URL=https://trrdexwjqyxrnznydglv.supabase.co
  SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRycmRleHdqcXl4cm56bnlkZ2x2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAwMjgyMzMsImV4cCI6MjA1NTYwNDIzM30.oumkAp8lkQmCsT-lQ-WWqf33TKY6zMOwa2LtcgmqAEY
  ```
  (We've privated this project in the meantime to prevent this key from being exposed to the public.)
  
  Replace `xxxxx` with your actual API key.

- Create another .env file in the `frontend` directory

  In this .env file, add our Supabase environment variables again (**please make note of the different naming**):

  ```
  REACT_APP_SUPABASE_URL=https://trrdexwjqyxrnznydglv.supabase.co
  REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRycmRleHdqcXl4cm56bnlkZ2x2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDAwMjgyMzMsImV4cCI6MjA1NTYwNDIzM30.oumkAp8lkQmCsT-lQ-WWqf33TKY6zMOwa2LtcgmqAEY
  ```

### c. Authorize with Google Cloud API
- [Install](https://cloud.google.com/sdk/docs/install) the gcloud CLI

- Set up local authroization credentials for your account and set up project ID (talk2me-451917):
  ```
  gcloud init
  
  gcloud auth application-default login
  ```
  
## 3. Install Backend Dependencies

This project manages backend Python dependencies using Poetry. Follow these steps:

### a. Install Poetry (if not already installed)

If Poetry is not installed, you can install it globally using the following command:

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

If you run into issues, check out the [Poetry docs](https://python-poetry.org/docs/#installing-with-the-official-installer) for help.

### b. Install / update dependencies

Install all project dependencies by running:

  ```bash
  poetry install --no-root
  ```
---

# Run our Talk2Me app 💬:

Our app allows you to talk to our agent via either speech or text.

## 1. Start the Flask server

In your terminal, navigate to the project root directory and run the following command to start the Flask server:
```bash
poetry run python -m backend.run
```
## 2. Start the UI

Open a new terminal window and navigate to the `frontend` directory:
```bash
cd frontend
```
Install the frontend dependencies by running:
```bash
npm install
```
Then, start the React development server:
```bash
npm start
```
This will open the app in your browser at `http://localhost:3000/`.

## 3. Start Chatting!

You should now be able to chat with our agent through the UI. If the agent isn't responding as expected, double-check that the Flask server is still running. If the UI is entirely blank, double-check that you've included the Supabase environment variables in the **frontend** .env file, not the root directory .env file.

---

# Developer Culture 🔧
- If you’re working on a task, create an issue for it and assign it to yourself. Write updates as comments on your issue until you complete your task, upon which you can close your issue.
- If you’re writing new code, create a branch with the naming format "FIRSTNAME-BRANCH-REASON" (for example, winson-cot-prompts).
- The main branch should ideally never have any bugs, and represents our overall progress. **Commits should only be pushed to main in the cases of (1) minor bug fixes or (2) markdown file updates.**
- When you want to merge your changes to main, submit a pull request and have another team member review your code prior to completing the merge. For cleanliness, make sure to delete your branch after it's been merged.

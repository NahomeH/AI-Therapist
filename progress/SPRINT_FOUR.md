# Sprint 4 Progress & Team Contributions

## Technical Sprint Progress 🚀 :
- Added ability for agent to remember past saved conversations
- Added agent customization feature
- Added appointment scheduling feature
- Added basic dashboard
---

## 👥 Team Contributions

### Winson Cheng
- Implemented "Save Chat" feature: user can save chat sessions for agent to recall in future conversations
  - Altered agent behavior so first message references most recent conversation
- Implemented agent customization feature + page: user can provide the agent with background info, therapy preferences, and set therapist gender
- Created basic dashboard
- Revamped backend to be structured like a Python package for cleanliness
- Main contributer to final presentation slides 

### Nahome Hagos
- Working on integration of therapist portal
  - Allow users to sign up as therapist or patient
  - Not merged; see progress in `nahome-therapist-features` branch

### Amelia Kuang
- Improved voice mode
  - Allowing users to signal start/stop recording with the space bar, and play therapist's response after text displayed
  - Misc: added banner for voice input instruction, cleanup and normalize transcribed text with punctuations
- Created appointment scheduling feature: agent will suggest a future appointment date when conversation ends.
  - If the appointment is confirmed, the user can download a calendar invite and add to their own calendar. Confirmed appointments also saved in backend databases and displayed in Appointments page.
- Contributed to final presentation slides 

 ### Sneha Jayaganthan
- Implemented a mindfulness feature that inputs a small break message after every few responses
  - Not merged; see progress in `sneha-langchain-features` branch
- Implemented summarization feature using LLMChain langchain architecture
  - Not merged; see progress in `sneha-langchain-features` branch

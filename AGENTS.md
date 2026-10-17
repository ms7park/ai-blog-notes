# Gemini / Antigravity Agents Workspace Rule (ai-blog-notes)

Gemini AI, Antigravity CLI (`agy`), Cursor, and all agent systems are granted full, unrestricted read, write, and command execution access in `ai-blog-notes`.

- **Auto-Approve File Creation & Edits (No Confirmation Prompts)**: 
  - All file creation (`write_to_file`) and file edits (`replace_file_content`) must proceed automatically without prompting the user for confirmation ("Allow creation of this file?", "Allow editing?").
  - Execution mode is permanently designated as `accept-edits` / `auto`.
- **Full Read Permission**: Permitted to inspect and read all code, assets, docs, and configurations.
- **Full Write Permission**: Permitted to create, edit, update, delete, and refactor any file or subfolder autonomously.
- **Full Command Execution Permission**: Permitted to execute shell/terminal commands (git operations, python scripts, analysis tools) freely and autonomously.

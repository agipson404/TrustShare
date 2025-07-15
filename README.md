# TrustShare
**Created By:** Arthur Gipson 
📺 YouTube Video: [https://youtu.be/d28OVuhgGQE](https://youtu.be/6E3PoU6JFGY)

**TrustShare** is a secure file storage and sharing platform. Built with FastAPI (Python) for the backend and React for the frontend, it’s designed to keep your files protected, private, and only accessible to those you trust.

## Why TrustShare Was Created
Most companies and agencies rely on third-party applications from big tech companies (like Microsoft, Google, or Dropbox) to share and store their most sensitive files. While these platforms offer convenience, they often store your data on external servers, and you have limited control over true privacy, access, or compliance.

## TrustShare was built because:

Sensitive information deserves better protection:
Relying on outside vendors can expose you to unnecessary risks if their security is breached or their policies change.

Control matters:
With in-house file sharing, you decide who can access, audit, and manage critical data—no hidden admin, no silent changes.

Compliance is easier:
For organizations with strict privacy, regulatory, or data residency needs, running your own secure sharing platform puts you in charge.

Zero trust, by design:
Only you and trusted users ever see your data, encrypted at every step—no one else.

<br>
TrustShare makes it simple for teams, businesses, and agencies to share and manage files safely—without giving up control to outside companies.



---

## 🔒 Security-First Features

- **End-to-End Encryption:**  
  Every file uploaded is encrypted *before* being saved to disk using Fernet symmetric encryption. Each user gets a unique encryption key. No file is ever stored in plaintext.

- **User Authentication:**  
  All access requires registration and login. JWT tokens are used for every request to protect your data and sessions.

- **Per-User File Ownership:**  
  Files are “owned” by users, and every file operation checks both authentication and ownership. No one else can see or access your files unless you share them.

- **Secure File Sharing:**  
  Share files directly with other registered users by username. Recipients can only access files shared with them—never your whole storage.

- **Controlled Access:**  
  File downloads, sharing, and lists are all strictly locked down:
  - Only owners or trusted (shared) users can decrypt/download.
  - Attempting access without permission returns an error.

- **Brute-Force Protection:**  
  Login endpoints are rate-limited using SlowAPI, stopping brute-force password attacks.

- **Full Audit Logging:**  
  All actions (registration, login, upload, download, sharing) are logged to a local `trustshare.log` file for security and traceability.

- **Strict File Validation:**  
  Only certain file types and sizes are accepted, reducing risk of unwanted uploads.

---

## 🛠 Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite  
- **Frontend:** React (JavaScript)  
- **Encryption:** cryptography.Fernet  
- **Authentication:** JWT (JSON Web Tokens)  
- **Rate Limiting:** SlowAPI  

---

## 🚀 Local Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/agipson404/trustshare.git
    cd trustshare/trustshare
    ```
2. **Install Python dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3. **Start the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    - API at: [http://localhost:8000](http://localhost:8000)
    - Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Frontend setup:**  
    (See `/frontend` for setup; run `npm install` then `npm start`)

---

## 📦 Usage

- **Register:** `POST /register`
- **Login:** `POST /login` (get JWT token)
- **Upload Encrypted File:** `POST /upload`
- **List Your Files:** `GET /files`
- **Download File:** `GET /files/{filename}`
- **Share File:** `POST /share-file` (with username)
- **See Shared With You:** `GET /shared-files`

---

## ⚠️ Security Notes

- Encryption keys are never exposed or sent over the network.
- No plaintext files are stored—everything is encrypted at rest.
- All actions require authentication.
- Full traceability: All file and user actions are logged.

---

**Arthur Gipson**  
[GitHub](https://github.com/agipson404) | [LinkedIn](https://www.linkedin.com/in/arthur-gipson-709688184/)

---

*Security is the core of TrustShare. PRs and feedback welcome!*

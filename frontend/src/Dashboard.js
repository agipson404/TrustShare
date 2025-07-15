import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard({ setLoggedIn }) {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [files, setFiles] = useState([]);
  const [sharedFiles, setSharedFiles] = useState([]);
  const [shareUsername, setShareUsername] = useState("");
  const [fileToShare, setFileToShare] = useState(null);

  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) return;

    axios.get("http://localhost:8000/files", {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(res => setFiles(res.data.files))
    .catch(() => setFiles([]));

    axios.get("http://localhost:8000/shared-files", {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(res => setSharedFiles(res.data.shared_files))
    .catch(() => setSharedFiles([]));
  }, [token]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });
      setMessage("Upload successful!");
      setFile(null);

      const res = await axios.get("http://localhost:8000/files", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFiles(res.data.files);
    } catch {
      setMessage("Upload failed.");
    }
  };

  const handleDownload = async (filename) => {
    try {
      const response = await axios.get(`http://localhost:8000/files/${filename}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch {
      setMessage("Failed to download file.");
    }
  };

  const openShareDialog = (filename) => {
    setFileToShare(filename);
    setShareUsername("");
    setMessage("");
  };

  const handleShare = async (e) => {
    e.preventDefault();
    if (!fileToShare || !shareUsername) return;

    try {
      await axios.post("http://localhost:8000/share-file", null, {
        params: {
          file_name: fileToShare,
          shared_with_username: shareUsername,
        },
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessage(`Shared "${fileToShare}" with ${shareUsername}`);
      setFileToShare(null);
      setShareUsername("");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Failed to share file.");
    }
  };


  return (
    <div className="dashboard-container">
      <h2>Dashboard</h2>
      <h3>Upload a File</h3>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          onChange={e => setFile(e.target.files[0])}
          required
        />
        <button type="submit">Upload</button>
      </form>

      {message && <div>{message}</div>}

        <h3>Your Files</h3>
	<ul>
	  {files.map(f => (
	    <li key={f.stored_name}>
	      {f.display_name}{" "}
	      <button onClick={() => handleDownload(f.stored_name)}>Download</button>{" "}
	      <button onClick={() => openShareDialog(f.stored_name)}>Share</button>
	    </li>
	  ))}
	</ul>

	{fileToShare && (
	  <form onSubmit={handleShare} style={{ marginTop: "1rem" }}>
	    <h4>Share "{fileToShare.split("_").slice(3).join("_") || fileToShare}" with:</h4>
	    <input
	      type="text"
	      placeholder="Enter username"
	      value={shareUsername}
	      onChange={e => setShareUsername(e.target.value)}
	      required
	    />
	    <button type="submit">Share File</button>{" "}
	    <button type="button" onClick={() => setFileToShare(null)}>Cancel</button>
	  </form>
	)}

	<h3>Files Shared With You</h3>
	<ul>
	  {sharedFiles.length === 0 && <li>No files shared with you.</li>}
	  {sharedFiles.map(f => (
	    <li key={f.file_name}>
	      {f.file_name.split("_").slice(3).join("_") || f.file_name} (Owner: {f.owner}){" "}
	      <button onClick={() => handleDownload(f.file_name)}>Download</button>
	    </li>
	  ))}
	</ul>


    </div>
  );
}

export default Dashboard;

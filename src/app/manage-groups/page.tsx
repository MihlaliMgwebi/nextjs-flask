"use client";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useReceiptContext } from "../scan-bill/ReceiptContext";


export default function JoinSessionPage() {
  const { socket, receipt, setReceipt } = useReceiptContext();
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string>("");
  useEffect(() => {
    // Retrieve receipt from local storage
    const storedReceipt = localStorage.getItem("receipt");
    if (storedReceipt) {
      setReceipt(JSON.parse(storedReceipt));
    }

    if (socket) {
      socket.on("session_update", (data: any) => {
        setReceipt(data);
        // Save receipt to local storage
        localStorage.setItem("receipt", JSON.stringify(data));
      });
    }
  }, [socket, setReceipt]);
  
  function joinSession() {
    if (socket && receipt) {
      socket.emit("join_session", {
        session_id: sessionId,
        user_id: receipt.user_id, // Use user_id as username
      });
      router.push(`session/${sessionId}?userId=${receipt.user_id}`); // Add userId as query param
    }
  }

  return (
    <div>
      <h1>Join a Session</h1>
      <input
        type="text"
        value={sessionId}
        onChange={(e) => setSessionId(e.target.value)}
        placeholder="Enter session ID"
      />
      <button onClick={joinSession}>Join session</button>
    </div>
  );
}
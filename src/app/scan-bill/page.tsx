"use client";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useReceiptContext } from "./ReceiptContext";

export default function ScanReceipt() {
  const { receipt, setReceipt, socket } = useReceiptContext();
  const router = useRouter();
  const [link, setLink] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

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

  async function uploadFile(
    evt: React.MouseEvent<HTMLButtonElement, MouseEvent>
  ) {
    evt.preventDefault();

    // Check if a file is selected
    const file = fileInput.current?.files?.[0];
    if (!file) {
      console.error("No file selected");
      return; // Exit if no file is selected
    }

    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append("file", file);

    // Use POST request to send the file
    const response = await fetch(`/api/processbill`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      console.error("Error fetching data:", response.statusText);
      return; // Handle error appropriately
    }

    const result = await response.json();
    setReceipt(result); // Handle the result as needed
    setLink(result.link); // Set the link for sharing TODO get sessionId
    // Save receipt to local storage
    localStorage.setItem("receipt", JSON.stringify(result));
  }

  function joinSession() {
    if (socket && receipt) {
      socket.emit("join_session", {
        session_id: receipt.session_id,
        user_id: receipt.user_id, // Use user_id as username
      });
      router.push(`${receipt.link}?userId=${receipt.user_id}`); // Add userId as query param
    }
  }

  return (
    <div>
      <h1>Upload a photo of your bill</h1>
      <input
        type='file'
        accept='image/*'
        ref={fileInput}
      />
      <button onClick={uploadFile}>Upload</button>

      {receipt && (
        <div>
          <h2>Receipt</h2>
          <ul>
            {receipt.receipt_summary.items.map((item: any, index: number) => (
              <li key={index}>
                {item.quantity} x {item.item} - ${item.price.toFixed(2)}
              </li>
            ))}
          </ul>
          <p>Subtotal: ${receipt.receipt_summary.subtotal?.toFixed(2)}</p>
          <p>Tax: ${receipt.receipt_summary.tax?.toFixed(2)}</p>
          <p>Total: ${receipt.receipt_summary.total?.toFixed(2)}</p>
          <p>Tip: ${receipt.receipt_summary.tip?.toFixed(2)}</p>
        </div>
      )}

      {link && (
        <div>
          <h2>Shareable Link</h2>
          <input type="text" value={link} readOnly />
          <button onClick={joinSession}>Join session</button>
        </div>
      )}
    </div>
  );
}
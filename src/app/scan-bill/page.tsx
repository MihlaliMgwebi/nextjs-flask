"use client";

import { useRef, useState } from "react";

export default function UploadForm() {
  const fileInput = useRef<HTMLInputElement>(null);
  const [receipt, setReceipt] = useState<any>(null);

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
            {receipt.items.map((item: any, index: number) => (
              <li key={index}>
                {item.quantity} x {item.item} - ${item.price.toFixed(2)}
              </li>
            ))}
          </ul>
          <p>Subtotal: ${receipt.subtotal?.toFixed(2)}</p>
          <p>Tax: ${receipt.tax?.toFixed(2)}</p>
          <p>Total: ${receipt.total?.toFixed(2)}</p>
          <p>Tip: ${receipt.tip?.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
}

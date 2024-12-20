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
    evt: React.ChangeEvent<HTMLInputElement>
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
    setLink(result.link.split('/').pop()); // Set the link for sharing TODO get sessionId
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
    <div className='flex flex-col items-center justify-center w-full h-full gap-4'>
       {!link && (<div className='flex items-center justify-center w-full'>
        <label
          htmlFor='dropzone-file'
          className='flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600'>
          <div className='flex flex-col items-center justify-center pt-5 pb-6'>
            <svg
              className='w-8 h-8 mb-4 text-gray-500 dark:text-gray-400'
              aria-hidden='true'
              xmlns='http://www.w3.org/2000/svg'
              fill='none'
              viewBox='0 0 20 16'>
              <path
                stroke='currentColor'
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth='2'
                d='M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2'
              />
            </svg>
            <p className='mb-2 text-sm text-gray-500 dark:text-gray-400'>
              <span className='font-semibold'>Click to upload</span>
            </p>
            <p className='text-xs text-gray-500 dark:text-gray-400'>
              PNG, JPG or JPEG
            </p>
          </div>
          <input
            id='dropzone-file'
            type='file'
            accept='image/*'
            ref={fileInput}
            className='hidden'
            onChange={uploadFile}
          />
        </label>
      </div>
    )}

      {link && (
        <div className="flex flex-col gap-5">
    <div className="flex items-center" onClick={() => navigator.clipboard.writeText(link)}>
      <svg 
        stroke="currentColor" 
        fill="currentColor" 
        stroke-width="0" 
        viewBox="0 0 24 24" 
        height="1em" 
        width="1em" 
        xmlns="http://www.w3.org/2000/svg"
        className="cursor-pointer"
      >
        <g id="Share_2">
          <path d="M18.44,15.94a2.5,2.5,0,0,0-1.96.95L7.97,12.64a2.356,2.356,0,0,0,0-1.29l8.5-4.25a2.5,2.5,0,1,0-.53-1.54,2.269,2.269,0,0,0,.09.65l-8.5,4.25a2.5,2.5,0,1,0,0,3.08l8.5,4.25a2.269,2.269,0,0,0-.09.65,2.5,2.5,0,1,0,2.5-2.5Zm0-11.88a1.5,1.5,0,1,1-1.5,1.5A1.5,1.5,0,0,1,18.44,4.06ZM5.56,13.5A1.5,1.5,0,1,1,7.06,12,1.5,1.5,0,0,1,5.56,13.5Zm12.88,6.44a1.5,1.5,0,1,1,1.5-1.5A1.5,1.5,0,0,1,18.44,19.94Z"></path>
        </g>
      </svg>
      <div>
      <div className="ml-2 text-sm text-gray-500 dark:text-gray-400">Click to copy the session id.</div>
      <div className="ml-2 text-sm text-gray-500 dark:text-gray-400">Share with your foodie friends!</div>
      </div>
    </div>
          {/* <div className="flex flex-col"> */}
          <button onClick={joinSession} type="button" className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Continue</button>
          <button onClick={() => setLink(null)}  type="button" className="py-2.5 px-5 me-2 mb-2 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700">Upload a different bill</button>
{/* </div> */}
        </div>
      )}

    </div>
  );
}

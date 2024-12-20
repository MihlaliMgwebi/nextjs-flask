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
    <div className='flex flex-col items-center justify-center w-full h-full gap-4 px-16'>
      <label
        htmlFor='sessionId'
        className='block mb-2 text-sm font-medium text-gray-900 dark:text-white'>
        Your session id
      </label>
      <input
        id='sessionId'
        type='text'
        value={sessionId}
        onChange={(e) => setSessionId(e.target.value)}
        placeholder='Enter session ID'
        className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        required
      />
      <button
        className='text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800'
        onClick={joinSession}>
        Join session
      </button>
    </div>
  );
}

"use client";
import React, { createContext, useContext, useEffect, useState } from "react";
import { io } from "socket.io-client";

const ReceiptContext = createContext<any>(null);

export const ReceiptProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [receipt, setReceipt] = useState(null);
  const [socket, setSocket] = useState<any>(null);

  useEffect(() => {
    const newSocket = io("http://localhost:5328"); // Replace with your server URL
    setSocket(newSocket);

    newSocket.on("session_update", (data: any) => {
      setReceipt(data);
    });

    return () => {
      newSocket.close();
    };
  }, [setSocket]);

  return (
    <ReceiptContext.Provider value={{ receipt, setReceipt, socket }}>
      {children}
    </ReceiptContext.Provider>
  );
};

export const useReceiptContext = () => {
  return useContext(ReceiptContext);
};

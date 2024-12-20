"use client";

import { useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useReceiptContext } from "../../scan-bill/ReceiptContext";

export default function ClaimMealPage() {
  const { receipt, setReceipt, socket } = useReceiptContext();
  const searchParams = useSearchParams();
  const userId = searchParams.get("userId");

  useEffect(() => {
    // Retrieve receipt from local storage
    if (socket) {
      socket.on("session_update", (data: any) => {
        setReceipt(data);
      });
    }
  }, [socket, setReceipt]);

  const claimItem = (item: any) => {
    if (socket && receipt) {
      socket.emit("claim_item", {
        item,
        session_id: receipt.session_id,
        user_id: userId,
      });
    }
  };

  return (
    <div>
      <h1>Receipt Details</h1>

      {receipt && (
        <div>
          <h2>Receipt</h2>
          <ul>
            {receipt.receipt_summary.items.map((item: any, index: number) => (
              <li key={index}>
                {item.quantity} x {item.item} - ${item.price.toFixed(2)}
                <button onClick={() => claimItem(item)}>Claim</button>
              </li>
            ))}
          </ul>
          <p>Subtotal: ${receipt.receipt_summary.subtotal?.toFixed(2)}</p>
          <p>Tax: ${receipt.receipt_summary.tax?.toFixed(2)}</p>
          <p>Total: ${receipt.receipt_summary.total?.toFixed(2)}</p>
          <p>Tip: ${receipt.receipt_summary.tip?.toFixed(2)}</p>
        </div>
      )}

      {receipt && receipt.users && userId && receipt.users[userId] && (
              <div>
                <h2>My Bill</h2>
                <ul>
                  {receipt.users[userId].claimed_items.map((item: any, index: number) => (
                    <li key={index}>
                      {item.quantity} x {item.item} - ${item.price.toFixed(2)}
                    </li>
                  ))}
                </ul>
                <p>Total: ${receipt.users[userId].claimed_items.reduce((total: number, item: any) => total + item.price * item.quantity, 0).toFixed(2)}</p>
              </div>
            )}
    </div>
  );
}
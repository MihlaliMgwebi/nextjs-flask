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

  const unclaimItem = (item: any) => {
    if (socket && receipt) {
      socket.emit("unclaim_item", {
        item,
        session_id: receipt.session_id,
        user_id: userId,
      });
    }
  };

  return (
    <div>
      {receipt && (
        <div>
          <span className='text-xs text-gray-500 truncate dark:text-gray-400'>
            Transaction details
          </span>
          <ul>
            {receipt.receipt_summary.items.map((item: any, index: number) => (
              <li
                key={index}
                className='pt-3 pb-0 sm:pt-4'>
                <div className='flex items-center space-x-4 rtl:space-x-reverse'>
                  <div className='flex-shrink-0'>
                    <button onClick={() => claimItem(item)}>
                      <svg
                        stroke='currentColor'
                        fill='currentColor'
                        strokeWidth='0'
                        viewBox='0 0 512 512'
                        height='1em'
                        width='1em'
                        xmlns='http://www.w3.org/2000/svg'>
                        <path d='M346.5 240H272v-74.5c0-8.8-7.2-16-16-16s-16 7.2-16 16V240h-74.5c-8.8 0-16 6-16 16s7.5 16 16 16H240v74.5c0 9.5 7 16 16 16s16-7.2 16-16V272h74.5c8.8 0 16-7.2 16-16s-7.2-16-16-16z'></path>
                        <path d='M256 76c48.1 0 93.3 18.7 127.3 52.7S436 207.9 436 256s-18.7 93.3-52.7 127.3S304.1 436 256 436c-48.1 0-93.3-18.7-127.3-52.7S76 304.1 76 256s18.7-93.3 52.7-127.3S207.9 76 256 76m0-28C141.1 48 48 141.1 48 256s93.1 208 208 208 208-93.1 208-208S370.9 48 256 48z'></path>
                      </svg>
                    </button>
                  </div>
                  <div className='flex-1 min-w-0 flex flex-col gap-1'>
                    <p className='text-sm font-medium text-gray-900 truncate dark:text-white'>
                      {item.item}
                    </p>
                    <div className='flex gap-3 text-xs text-gray-500 truncate dark:text-gray-400'>
                      <span>${(item.price / item.quantity).toFixed(2)}</span>
                      <span>{item.quantity}x</span>
                    </div>
                  </div>
                  <div className='inline-flex items-center text-base font-semibold text-gray-900 dark:text-white'>
                    ${item.price.toFixed(2)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
          <hr className="border-t-2 border-dashed border-gray-300 my-4" />
          <div className='flex flex-col gap-1 mt-5'>
            <div className='flex items-center justify-between text-sm'>
              <span className='text-xs text-gray-500 truncate dark:text-gray-400'>
                Subtotal:
              </span>{" "}
              <span>${receipt.receipt_summary.subtotal?.toFixed(2)}</span>
            </div>
            <div className='flex items-center justify-between text-sm'>
              <span className='text-xs text-gray-500 truncate dark:text-gray-400'>
                Total due:
              </span>{" "}
              <span>${receipt.receipt_summary.total?.toFixed(2)}</span>
            </div>
            <div className='flex items-center justify-between text-sm'>
              <span className='text-xs text-gray-500 truncate dark:text-gray-400'>
                Tip:
              </span>{" "}
              <span>${receipt.receipt_summary.tip?.toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}
 <hr className="border-t-2 border-solid border-gray-300 mt-10" />
      {receipt && receipt.users && userId && receipt.users[userId] && (
        <div className="mt-2">
          <span className='text-xs text-gray-500 truncate dark:text-gray-400'>
            My bill due
          </span>
          <ul>
            {receipt.users[userId].claimed_items.map(
              (item: any, index: number) => (
                <li key={index} className='pt-3 pb-0 sm:pt-4'>
                  {/* {item.quantity} x {item.item} - ${item.price.toFixed(2)}
                  <button onClick={() => unclaimItem(item)}>Remove</button> */}
                  <div className='flex items-center space-x-4 rtl:space-x-reverse'>
                  <div className='flex-shrink-0'>
                    <button onClick={() => unclaimItem(item)}>
                    <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 24 24" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><g id="Circle_Remove"><g><path d="M9.525,13.765a.5.5,0,0,0,.71.71c.59-.59,1.175-1.18,1.765-1.76l1.765,1.76a.5.5,0,0,0,.71-.71c-.59-.58-1.18-1.175-1.76-1.765.41-.42.82-.825,1.23-1.235.18-.18.35-.36.53-.53a.5.5,0,0,0-.71-.71L12,11.293,10.235,9.525a.5.5,0,0,0-.71.71L11.293,12Z"></path><path d="M12,21.933A9.933,9.933,0,1,1,21.934,12,9.945,9.945,0,0,1,12,21.933ZM12,3.067A8.933,8.933,0,1,0,20.934,12,8.944,8.944,0,0,0,12,3.067Z"></path></g></g></svg>
                    </button>
                  </div>
                  <div className='flex-1 min-w-0 flex flex-col gap-1'>
                    <p className='text-sm font-medium text-gray-900 truncate dark:text-white'>
                      {item.item}
                    </p>
                    <div className='flex gap-3 text-xs text-gray-500 truncate dark:text-gray-400'>
                      <span>${(item.price / item.quantity).toFixed(2)}</span>
                      <span>{item.quantity}x</span>
                    </div>
                  </div>
                  <div className='inline-flex items-center text-base font-semibold text-gray-900 dark:text-white'>
                    ${item.price.toFixed(2)}
                  </div>
                </div>
                </li>
              )
            )}
          </ul>
          <hr className="border-t-2 border-dashed border-gray-300 my-4" />
      
          <div className='flex items-center justify-between text-sm mt-5'>
              <span className='text-xs text-gray-500 truncate dark:text-gray-400'>
                Total:
              </span>
              <span>${receipt.users[userId].claimed_items
              .reduce(
                (total: number, item: any) =>
                  total + item.price * item.quantity,
                0
              )
              .toFixed(2)}</span>
            </div>
        </div>
      )}
    </div>
  );
}

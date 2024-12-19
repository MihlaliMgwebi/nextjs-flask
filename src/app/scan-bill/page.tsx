"use client";

import { useRef } from "react";

export default function UploadForm() {
  const fileInput = useRef<HTMLInputElement>(null);

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

    // Prepare query parameters
    const params = new URLSearchParams();
    params.append("image", file.name); // Send the filename as a query parameter

    // Use GET request with query parameters
    const response = await fetch(`/api/processbill?${params.toString()}`, {
      method: "GET",
    });

    if (!response.ok) {
      console.error("Error fetching data:", response.statusText);
      return; // Handle error appropriately
    }

    const result = await response.json();
    console.log(result); // Handle the result as needed
  }

  return (
    <>
      <form className='flex flex-col gap-5 items-center justify-center w-full h-full'>
        <h1>Upload a photo of your bill</h1>
        <span>Don't worry, your data will stay safe and private.</span>
        <label className='flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600'>
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
              PNG, JPG or JPEG (MAX. 800x400px)
            </p>
          </div>

          <input
            id='dropzone-file'
            type='file'
            accept='image/*'
            capture='environment'
            ref={fileInput}
            className='hidden'
          />
        </label>
        <span>or</span>
        <button
          type='button'
          onClick={() => fileInput.current?.click()}>
          Open camera & take photo
        </button>

        <button
          type='submit'
          onClick={uploadFile}>
          Continue
        </button>
      </form>
    </>
  );
}

"use client";

import { useEffect, useState } from "react";

// Example of using the Contacts API (if supported)
async function getContacts() {
  if ("contacts" in navigator) {
    const options = new ContactFindOptions();
    options.filter = ""; // Empty string for all contacts
    options.multiple = true; // Get multiple contacts
    const fields = ["name", "phoneNumbers"];

    try {
      const contacts = await navigator.contacts.select(fields, options);
      console.log(contacts);
      return contacts;
    } catch (error) {
      console.error("Error fetching contacts:", error);
    }
  } else {
    console.log("Contacts API not supported");
  }
}

const ContactList = () => {
  const [contacts, setContacts] = useState([]);

  useEffect(() => {
    async function fetchContacts() {
      const fetchedContacts = await getContacts();
      setContacts(fetchedContacts);
    }
    fetchContacts();
  }, []);

  return (
    <div>
      <h2>Select a Contact</h2>
      <ul>
        {/* {contacts.map((contact) => (
          <li key={contact.id}>
            {contact.name} - {contact.phoneNumbers[0]?.value}
          </li>
        ))} */}
      </ul>
    </div>
  );
};

export default ContactList;

const fs = require('fs');
const path = require('path');
// const fetch = require('node-fetch');
const csv = require('csvtojson');

// Define the API URL
const apiUrl = "http://127.0.0.1:5000/preprocess";

// Path to the CSV file
const filePath = path.join(__dirname, 'Test-Set.csv');

// Read and preprocess the CSV file
csv()
  .fromFile(filePath)
  .then(async (jsonData) => {
    // Wrap the data in a JSON object with the key 'dataframe'
    const requestBody = { dataframe: jsonData };

    try {
      // Send a POST request to the Flask API
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      // Check if the response is successful
      if (response.ok) {
        const result = await response.json();
        console.log("Preprocessed Data:");
        console.log(result.data);
      } else {
        console.error("Error:", response.status, await response.json());
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  })
  .catch((error) => {
    console.error("Error reading the CSV file:", error);
  });

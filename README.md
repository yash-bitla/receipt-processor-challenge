# Receipt Processor Challenge

## Table of Contents

- [Description](#description)
- [How to Run the Application](#how-to-run-the-application)
- [Testing the APIs Using Postman](#testing-the-apis-using-postman)
- [Trade-offs and Design Decisions](#trade-offs-and-design-decision)
- [API Specification](#api-specification)
- [Rules for Calculating Points](#rules-for-calculating-points)
- [Conclusion](#conclusion)

## Description

This is a web service that processes receipts and calculates points based on specific rules. The service is built using Python and Flask, and it leverages Docker for containerization to ensure consistent deployment across different environments.

## How to run the Application

### Prerequisites

- Docker must be installed in your system.
- Install Postman for testing the APIs

### Steps to Run

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd receipt-processor
   ```

2. Build the Docker Image:

   ```bash
   docker build -t receipt-processor .
   ```

3. Run the docker container:
   ```bash
   docker run -p 5000:5000 receipt-processor
   ```

## Testing the APIs Using Postman

To test the APIs using Postman, follow the steps below:

### 1. Process a Receipt

1. **Open Postman**: Launch the Postman application on your computer.
2. **Create a New Request**: Click on the "New" button and select "Request".
3. **Set the Request Method to POST**: Choose the `POST` method from the dropdown.
4. **Enter the Request URL**: In the request URL field, enter `http://localhost:5000/receipts/process`.
5. **Set the Request Body**:
   - Click on the "Body" tab.
   - Select the "raw" radio button.
   - Choose "JSON" from the dropdown next to the "raw" option.
   - Enter the following JSON payload in the text area:
   ```json
   {
     "retailer": "Target",
     "purchaseDate": "2022-01-02",
     "purchaseTime": "13:13",
     "total": "1.25",
     "items": [{ "shortDescription": "Pepsi - 12-oz", "price": "1.25" }]
   }
   ```
6. **Send the Request**: Click the "Send" button to send the request.
7. **View the Response**: Check the response section at the bottom to see the receipt ID returned by the API.

### 2. Get Points for a Receipt

1. **Copy the Receipt ID**: Copy the receipt ID returned from the previous step.
2. **Create a New Request**: Click on the "New" button and select "Request".
3. **Set the Request Method to GET**: Choose the `GET` method from the dropdown.
4. **Enter the Request URL**: In the request URL field, enter `http://localhost:5000/receipts/{id}/points`, replacing `{id}` with the actual receipt ID copied from the previous step.
5. **Send the Request**: Click the "Send" button to send the request.
6. **View the Response**: Check the response section at the bottom to see the points awarded for the receipt.

### Example Steps

1. **Process a Receipt**:

   - **Request**:
     - Method: `POST`
     - URL: `http://localhost:5000/receipts/process`
     - Body (JSON):
       ```json
       {
         "retailer": "Target",
         "purchaseDate": "2022-01-01",
         "purchaseTime": "13:01",
         "items": [
           {
             "shortDescription": "Mountain Dew 12PK",
             "price": "6.49"
           },
           {
             "shortDescription": "Emils Cheese Pizza",
             "price": "12.25"
           },
           {
             "shortDescription": "Knorr Creamy Chicken",
             "price": "1.26"
           },
           {
             "shortDescription": "Doritos Nacho Cheese",
             "price": "3.35"
           },
           {
             "shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ",
             "price": "12.00"
           }
         ],
         "total": "35.35"
       }
       ```
   - **Response**:
     ```json
     {
       "id": "7fb1377b-b223-49d9-a31a-5a02701dd310"
     }
     ```

2. **Get Points for a Receipt**:
   - **Request**:
     - Method: `GET`
     - URL: `http://localhost:5000/receipts/7fb1377b-b223-49d9-a31a-5a02701dd310/points`
   - **Response**:
     ```json
     {
       "points": 32
     }
     ```

By following these steps, you can easily test the endpoints of the Receipt Processor API using Postman.

## Trade-offs and Design Decision

- **Consistency over Asynchronous Processing:**

  Initially, the idea was to calculate points asynchronously in the `/receipts/process` endpoint to provide a faster response to the user. However, in real-world scenarios, if the points are calculated asynchronously and the user has already received a `200 OK` response, there could be a delay in updating the points. If the user subsequently requests the `/receipts/{id}/points` endpoint before the points calculation is completed, they would not receive the correct points, leading to a poor user experience. Therefore, I chose to prioritize consistency and calculate points synchronously when the `/receipts/{id}/points` endpoint is called. This ensures that users always receive the correct points when they request them.

- **Deferred Points Calculation:**

  When designing the points calculation mechanism, I considered two approaches:

  1. **Calculate Points Immediately**: Calculate the points in the `/receipts/process` endpoint and store the receipt ID along with its points in memory.
  2. **Calculate Points on Demand**: Store the receipt ID and the entire payload (receipt) in memory, and calculate the points only when the `/receipts/{id}/points` endpoint is requested.

  I chose the second approach (calculate points on demand) for the following reasons:

  In real-world scenarios, the `/receipts/process` endpoint will likely receive more requests than the `/receipts/{id}/points` endpoint. This is because the `/receipts/{id}/points` endpoint is only called after a receipt has been processed, and not every processed receipt will necessarily have its points queried. By deferring the points calculation to the `/receipts/{id}/points` endpoint, we can provide quicker responses for the more frequently used `/receipts/process` endpoint, improving the overall user experience and system efficiency.

  This design choice ensures that the more common operation (processing receipts) is optimized for speed, while the less frequent operation (querying points) can afford a slight delay due to on-demand calculation. This approach balances the need for performance with the necessity of maintaining a consistent and accurate points calculation system.

- **More memory for a faster response:**

  Due to the above consideration, I made a trade-off by storing the entire payload in memory instead of just storing the points. This could be an issue in real-world scenarios if the receipts are very large and take up a lot of memory. To optimize this, we can store only the necessary information required to calculate the points.

  Additionally, to further optimize memory usage and avoid recalculating points every time the `/receipts/{id}/points` endpoint is called for the same ID, I updated the solution to store the calculated points. When the points for a receipt are calculated for the first time, the full payload in memory is replaced with just the points. This ensures that the points calculation only happens the first time the `/receipts/{id}/points` endpoint is called for a given ID. Subsequent calls for the same ID can simply return the pre-calculated points, improving efficiency.

## API Specification

### 1. Process Receipts

- **Endpoint**: `/receipts/process`
- **Method**: `POST`
- **Payload**: Receipt JSON
- **Response**: JSON containing an `id` for the receipt.
- **Description**: Takes in a JSON receipt and returns a JSON object with an ID generated by the code. The ID returned is the ID that should be passed into `/receipts/{id}/points` to get the number of points the receipt was awarded.

### Example Responses

```json
{
  "id": "7fb1377b-b223-49d9-a31a-5a02701dd310"
}
```

### 2. Get Points

- **Endpoint**: `/receipts/{id}/points`
- **Method**: `GET`
- **Response**: A JSON object containing the number of points awarded.
- **Description**: A simple Getter endpoint that looks up the receipt by the ID and returns an object specifying the points awarded.

### Example Responses

```json
{
  "points": 109
}
```

## Rules for Calculating Points

- One point for every alphanumeric character in the retailer name.
- 50 points if the total is a round dollar amount with no cents.
- 25 points if the total is a multiple of 0.25.
- 5 points for every two items on the receipt.
- If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
- 6 points if the day in the purchase date is odd.
- 10 points if the time of purchase is after 2:00pm and before 4:00pm.

## Conclusion

This solution provides a scalable and efficient way to process receipts and calculate points, with trade-offs made to optimize for memory usage and performance. Future enhancements can be made to further improve scalability and maintainability by introducing persistent storage, caching, and a microservices architecture.

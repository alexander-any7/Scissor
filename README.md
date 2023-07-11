# Scissor URL Shortening API (Case Study) [![Scissor API Tests](https://github.com/Anyaegbunam-Alexander/Scissor/actions/workflows/tests.yml/badge.svg)](https://github.com/Anyaegbunam-Alexander/Scissor/actions/workflows/tests.yml)

Brief is the new black, this is what inspires the team at Scissor. In today’s world, it’s important to keep things as short as possible, and this applies to more concepts than you may realize. From music, speeches, to wedding receptions, brief is the new black. Scissor is a simple tool which makes URLs as short as possible. Scissor thinks it can disrupt the URL-shortening industry and give the likes of bit.ly and ow.ly a run for their money within 2 years.


The main goal of this project was to learn **React** and how to integrate it with a **Python** backend, in this case, **Flask-RESTX**.

## Implementation Guide:
- **URL Shortening**:
Scissor allows users to shorten URLs by pasting a long URL into the Scissor platform and a shorter URL gets automatically generated. The shortened URL is designed to be as short as possible, making it easy to share on social media or through other channels.
- **Custom URLs**:
Scissor also allows users to customize their shortened URLs. Users can choose their own custom domain name and customize the URL to reflect their brand or content. This feature is particularly useful for individuals or small businesses who want to create branded links for their businesses
- **QR Code Generation**:
Scissor allows users to also generate QR codes for shortened URLs. Users can download the QR code image and use it in their promotional materials or/and on their website. This feature will be implemented using a third-party QR code generator API, which can be integrated into the Scissor platform.
- **Analytics**:		
Scissor provides basic analytics that allows users to track their shortened URL's performance. Users can see how many clicks their shortened URL has received and where the clicks are coming from. We need to track when a URL is used.
- **Link History**:
Scissor allows users to see the history of links they’ve created so they can easily find and reuse links they have previously created.
- **Restore Deleted Links**:
  Scissor allows users to restore deleted links if they so choose.

 This project uses **Flask-RESTX** and **Python** for the backend and **React** and **JavaScript** for the frontend. The backend and frontend have their own folders and dependencies.

## Backend Setup
Set up environment variables using the `.env_example` file.

### Installation 
1. Install project packages
   ```
   pip install -r requirements.txt
   ```
2. Run Flask
   ```
   flask run
   ```

### Caching
This project uses `Redis` for caching to improve performance

### Testing
There are a total of 32 tests. Testing is done using `pytest-cov`.
```
coverage run -m pytest
```
to view for coverage report
```
coverage report
```

### Linting
This project uses `Flake8` to ensure code quality and adherence to coding standards
```
Flake8
```

## Frontend Setup
1. cd into the frontend folder
   ```
   cd frontend
   ```
2. Install the packages
   ```
   npm install
   ```
3. Run the dev server
   ```
   npm start
   ```
